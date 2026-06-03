export type Department = "engineering" | "hr" | "operations" | "product";
export type DocumentCategory = "policy" | "technical" | "incident" | "procedure" | "faq" | "release_notes";
export type UserRole = "user" | "admin" | "department_lead";

export interface User {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  department?: Department;
}

export interface Document {
  id: number;
  name: string;
  department: Department;
  category: DocumentCategory;
  chunks_count: number;
}

export interface SourceReference {
  document_id: number;
  document_name: string;
  relevance_score: number;
  excerpt: string;
}

export interface ChatResponse {
  answer: string;
  sources: SourceReference[];
  confidence: number;
  is_hallucination_risk: boolean;
  warning_message?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: SourceReference[];
}
