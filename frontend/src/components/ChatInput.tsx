import React, { useState } from "react";
import { Department, DocumentCategory } from "@/types";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  loading?: boolean;
  selectedDepartment?: Department;
  selectedCategory?: DocumentCategory;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  loading = false,
  selectedDepartment,
  selectedCategory,
}) => {
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim()) return;

    onSendMessage(input);
    setInput("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        borderTop: "1px solid #ddd",
        padding: "16px",
        display: "flex",
        gap: "8px",
      }}
    >
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask a question..."
        disabled={loading}
        style={{
          flex: 1,
          padding: "12px",
          border: "1px solid #ccc",
          borderRadius: "4px",
          fontSize: "14px",
          opacity: loading ? 0.6 : 1,
          cursor: loading ? "not-allowed" : "text",
        }}
      />
      <button
        type="submit"
        disabled={loading || !input.trim()}
        style={{
          padding: "12px 24px",
          backgroundColor: loading ? "#ccc" : "#0066cc",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: loading || !input.trim() ? "not-allowed" : "pointer",
          fontSize: "14px",
          fontWeight: "bold",
          transition: "background-color 0.2s",
        }}
      >
        {loading ? "Sending..." : "Send"}
      </button>
    </form>
  );
};
