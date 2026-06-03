import React from "react";
import { ChatMessage as ChatMessageType, SourceReference } from "@/types";

interface ChatMessageProps {
  message: ChatMessageType;
}

const SourceBadge: React.FC<{ source: SourceReference }> = ({ source }) => (
  <a
    href={`#doc-${source.document_id}`}
    style={{
      display: "inline-block",
      padding: "4px 8px",
      marginRight: "8px",
      marginTop: "8px",
      backgroundColor: "#e3f2fd",
      color: "#0066cc",
      borderRadius: "4px",
      fontSize: "12px",
      textDecoration: "none",
      border: "1px solid #90caf9",
    }}
  >
    📄 {source.document_name}
  </a>
);

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === "user";

  return (
    <div
      style={{
        marginBottom: "15px",
        display: "flex",
        flexDirection: isUser ? "row-reverse" : "row",
        gap: "10px",
      }}
    >
      <div
        style={{
          width: "32px",
          height: "32px",
          borderRadius: "50%",
          backgroundColor: isUser ? "#e3f2fd" : "#f5f5f5",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "18px",
          flexShrink: 0,
        }}
      >
        {isUser ? "👤" : "🤖"}
      </div>

      <div style={{ flex: 1 }}>
        <div
          style={{
            padding: "12px 16px",
            backgroundColor: isUser ? "#0066cc" : "#f5f5f5",
            color: isUser ? "white" : "#333",
            borderRadius: "8px",
            wordBreak: "break-word",
          }}
        >
          {message.content}
        </div>

        {message.sources && message.sources.length > 0 && (
          <div style={{ marginTop: "8px" }}>
            <div style={{ fontSize: "12px", fontWeight: "bold", color: "#666" }}>
              Sources:
            </div>
            <div>
              {message.sources.map((source) => (
                <SourceBadge key={source.document_id} source={source} />
              ))}
            </div>
          </div>
        )}

        <div style={{ fontSize: "11px", color: "#999", marginTop: "4px" }}>
          {message.timestamp.toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};
