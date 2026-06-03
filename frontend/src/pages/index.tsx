import React, { useState, useEffect } from "react";
import { useChat } from "@/hooks/useChat";
import { Department } from "@/types";
import { healthAPI } from "@/utils/api";

export default function Home() {
  const [userId] = useState("demo-user");
  const [selectedDepartment, setSelectedDepartment] = useState<Department | undefined>();
  const [connected, setConnected] = useState(false);
  const [input, setInput] = useState("");

  const { messages, loading, sendMessage } = useChat({
    userId,
    department: selectedDepartment,
  });

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await healthAPI.check();
        setConnected(true);
      } catch {
        setConnected(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleSend = async () => {
    if (input.trim()) {
      await sendMessage(input);
      setInput("");
    }
  };

  return (
    <div style={{ fontFamily: "Arial", maxWidth: "900px", margin: "0 auto", padding: "20px" }}>
      <h1>Enterprise Knowledge Assistant</h1>

      <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
        <select
          value={selectedDepartment || ""}
          onChange={(e) => setSelectedDepartment((e.target.value as any) || undefined)}
          style={{ padding: "10px", borderRadius: "4px", border: "1px solid #ccc" }}
        >
          <option value="">All Departments</option>
          <option value="engineering">Engineering</option>
          <option value="hr">HR</option>
          <option value="operations">Operations</option>
          <option value="product">Product</option>
        </select>

        <div style={{ color: connected ? "green" : "red", fontWeight: "bold" }}>
          {connected ? "● Connected" : "● Disconnected"}
        </div>
      </div>

      <div
        style={{
          border: "1px solid #ccc",
          borderRadius: "8px",
          padding: "20px",
          marginBottom: "20px",
          height: "400px",
          overflowY: "auto",
          backgroundColor: "#f9f9f9",
        }}
      >
        {messages.length === 0 ? (
          <p style={{ color: "#999" }}>No messages yet. Ask a question to start.</p>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              style={{
                marginBottom: "15px",
                padding: "10px",
                backgroundColor: msg.role === "user" ? "#e3f2fd" : "#f5f5f5",
                borderRadius: "4px",
              }}
            >
              <strong>{msg.role === "user" ? "You" : "Assistant"}:</strong> {msg.content}
            </div>
          ))
        )}
      </div>

      <div style={{ display: "flex", gap: "10px" }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask a question..."
          disabled={loading}
          style={{
            flex: 1,
            padding: "10px",
            border: "1px solid #ccc",
            borderRadius: "4px",
          }}
        />
        <button
          onClick={handleSend}
          disabled={loading}
          style={{
            padding: "10px 20px",
            backgroundColor: loading ? "#ccc" : "#0066cc",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Loading..." : "Send"}
        </button>
      </div>
    </div>
  );
}
