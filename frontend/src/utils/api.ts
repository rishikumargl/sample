import axios from "axios";
import { ChatResponse, Document, Department, DocumentCategory } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

export const chatAPI = {
  sendMessage: async (
    question: string,
    userId: string,
    department?: Department
  ): Promise<ChatResponse> => {
    const response = await api.post("/api/chat", {
      question,
      user_id: userId,
      department,
    });
    return response.data;
  },

  getChatHistory: async (userId: string) => {
    const response = await api.get(`/api/chat/history/${userId}`);
    return response.data;
  },
};

export const documentsAPI = {
  uploadDocument: async (
    file: File,
    department: Department,
    category: DocumentCategory
  ) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("department", department);
    formData.append("category", category);

    const response = await api.post("/api/documents/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  listDocuments: async (
    department?: Department,
    category?: DocumentCategory
  ): Promise<Document[]> => {
    const response = await api.get("/api/documents", {
      params: { department, category },
    });
    return response.data;
  },

  getDocument: async (documentId: number): Promise<Document> => {
    const response = await api.get(`/api/documents/${documentId}`);
    return response.data;
  },

  deleteDocument: async (documentId: number) => {
    const response = await api.delete(`/api/documents/${documentId}`);
    return response.data;
  },
};

export const healthAPI = {
  check: async () => {
    const response = await api.get("/health");
    return response.data;
  },
};

export default api;
