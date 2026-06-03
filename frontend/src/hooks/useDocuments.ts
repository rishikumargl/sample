import { useState, useCallback } from "react";
import { Document, Department, DocumentCategory } from "@/types";
import { documentsAPI } from "@/utils/api";

export const useDocuments = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const uploadDocument = useCallback(
    async (
      file: File,
      department: Department,
      category: DocumentCategory
    ) => {
      setLoading(true);
      setError(null);

      try {
        const result = await documentsAPI.uploadDocument(
          file,
          department,
          category
        );
        return result;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to upload document";
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const fetchDocuments = useCallback(
    async (department?: Department, category?: DocumentCategory) => {
      setLoading(true);
      setError(null);

      try {
        const docs = await documentsAPI.listDocuments(department, category);
        setDocuments(docs);
        return docs;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to fetch documents";
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    documents,
    loading,
    error,
    uploadDocument,
    fetchDocuments,
  };
};
