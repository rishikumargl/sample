import React, { useState } from "react";
import { Department, DocumentCategory } from "@/types";

interface DocumentUploadProps {
  onUpload: (
    file: File,
    department: Department,
    category: DocumentCategory
  ) => Promise<void>;
  loading?: boolean;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUpload,
  loading = false,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [department, setDepartment] = useState<Department>("engineering");
  const [category, setCategory] = useState<DocumentCategory>("policy");
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const validTypes = ["application/pdf", "text/plain", "text/markdown"];
      if (!validTypes.includes(selectedFile.type)) {
        setError("Only PDF, TXT, and Markdown files are supported");
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setError("");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      setError("Please select a file");
      return;
    }

    setUploading(true);
    try {
      await onUpload(file, department, category);
      setFile(null);
      setDepartment("engineering");
      setCategory("policy");
      setIsOpen(false);
      setError("");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to upload document"
      );
    } finally {
      setUploading(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        style={{
          padding: "10px 20px",
          backgroundColor: "#28a745",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
          fontWeight: "bold",
        }}
      >
        📤 Upload Document
      </button>
    );
  }

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(0,0,0,0.5)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
      }}
    >
      <div
        style={{
          backgroundColor: "white",
          borderRadius: "8px",
          boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
          width: "100%",
          maxWidth: "400px",
        }}
      >
        <div
          style={{
            padding: "20px",
            borderBottom: "1px solid #ddd",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <h2 style={{ margin: 0 }}>Upload Document</h2>
          <button
            onClick={() => setIsOpen(false)}
            style={{
              background: "none",
              border: "none",
              fontSize: "24px",
              cursor: "pointer",
            }}
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ padding: "20px" }}>
          <div style={{ marginBottom: "16px" }}>
            <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>
              File
            </label>
            <input
              type="file"
              accept=".pdf,.txt,.md"
              onChange={handleFileChange}
              disabled={uploading}
              style={{ width: "100%", padding: "8px" }}
            />
            {file && (
              <p style={{ fontSize: "12px", color: "#666", marginTop: "8px" }}>
                Selected: <strong>{file.name}</strong>
              </p>
            )}
          </div>

          <div style={{ marginBottom: "16px" }}>
            <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>
              Department
            </label>
            <select
              value={department}
              onChange={(e) => setDepartment(e.target.value as Department)}
              disabled={uploading}
              style={{
                width: "100%",
                padding: "8px",
                border: "1px solid #ccc",
                borderRadius: "4px",
              }}
            >
              <option value="engineering">Engineering</option>
              <option value="hr">Human Resources</option>
              <option value="operations">Operations</option>
              <option value="product">Product</option>
            </select>
          </div>

          <div style={{ marginBottom: "16px" }}>
            <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>
              Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value as DocumentCategory)}
              disabled={uploading}
              style={{
                width: "100%",
                padding: "8px",
                border: "1px solid #ccc",
                borderRadius: "4px",
              }}
            >
              <option value="policy">Policy</option>
              <option value="technical">Technical</option>
              <option value="incident">Incident</option>
              <option value="procedure">Procedure</option>
              <option value="faq">FAQ</option>
              <option value="release_notes">Release Notes</option>
            </select>
          </div>

          {error && (
            <div
              style={{
                padding: "12px",
                backgroundColor: "#fee",
                color: "#c00",
                borderRadius: "4px",
                marginBottom: "16px",
                fontSize: "14px",
              }}
            >
              {error}
            </div>
          )}

          <div style={{ display: "flex", gap: "8px" }}>
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              disabled={uploading}
              style={{
                flex: 1,
                padding: "10px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                backgroundColor: "#f5f5f5",
                cursor: uploading ? "not-allowed" : "pointer",
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={uploading || !file}
              style={{
                flex: 1,
                padding: "10px",
                backgroundColor: uploading ? "#ccc" : "#0066cc",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: uploading || !file ? "not-allowed" : "pointer",
                fontWeight: "bold",
              }}
            >
              {uploading ? "Uploading..." : "Upload"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
