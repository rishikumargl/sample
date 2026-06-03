import { useState, useCallback } from "react";
import { ChatMessage, Department, SourceReference } from "@/types";
import { chatAPI } from "@/utils/api";

interface UseChatOptions {
  userId: string;
  department?: Department;
}

export const useChat = ({ userId, department }: UseChatOptions) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (question: string) => {
      if (!question.trim()) {
        setError("Question cannot be empty");
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await chatAPI.sendMessage(question, userId, department);

        setMessages((prev) => [
          ...prev,
          {
            id: `user-${Date.now()}`,
            role: "user",
            content: question,
            timestamp: new Date(),
          },
          {
            id: `assistant-${Date.now()}`,
            role: "assistant",
            content: response.answer,
            timestamp: new Date(),
            sources: response.sources,
          },
        ]);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to send message";
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    },
    [userId, department]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return { messages, loading, error, sendMessage, clearMessages };
};
