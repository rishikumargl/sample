import React from "react";
import { Department } from "@/types";

interface SidebarProps {
  selectedDepartment: Department | undefined;
  onDepartmentChange: (department: Department | undefined) => void;
  documentCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  selectedDepartment,
  onDepartmentChange,
  documentCount,
}) => {
  const departments: Department[] = ["engineering", "hr", "operations", "product"];

  const departmentLabels: Record<Department, string> = {
    engineering: "🛠️ Engineering",
    hr: "👥 Human Resources",
    operations: "⚙️ Operations",
    product: "📦 Product",
  };

  return (
    <aside
      style={{
        width: "250px",
        backgroundColor: "#1a1a1a",
        color: "white",
        padding: "20px",
        height: "100vh",
        overflowY: "auto",
        boxSizing: "border-box",
      }}
    >
      <div style={{ marginBottom: "30px" }}>
        <h1 style={{ fontSize: "24px", margin: "0 0 8px 0" }}>EKA</h1>
        <p style={{ fontSize: "12px", color: "#999", margin: 0 }}>
          Enterprise Knowledge Assistant
        </p>
      </div>

      <div style={{ marginBottom: "30px" }}>
        <p style={{ fontSize: "12px", color: "#999", margin: "0 0 12px 0", fontWeight: "bold" }}>
          Filter by Department
        </p>
        <button
          onClick={() => onDepartmentChange(undefined)}
          style={{
            width: "100%",
            textAlign: "left",
            padding: "10px 12px",
            marginBottom: "8px",
            backgroundColor: selectedDepartment === undefined ? "#0066cc" : "#333",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            transition: "background-color 0.2s",
          }}
        >
          All Departments
        </button>
        {departments.map((dept) => (
          <button
            key={dept}
            onClick={() => onDepartmentChange(dept)}
            style={{
              width: "100%",
              textAlign: "left",
              padding: "10px 12px",
              marginBottom: "8px",
              backgroundColor: selectedDepartment === dept ? "#0066cc" : "#333",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              transition: "background-color 0.2s",
            }}
          >
            {departmentLabels[dept]}
          </button>
        ))}
      </div>

      <div
        style={{
          padding: "16px",
          backgroundColor: "#333",
          borderRadius: "4px",
          marginBottom: "30px",
        }}
      >
        <div style={{ marginBottom: "8px" }}>
          <span style={{ fontSize: "16px", marginRight: "8px" }}>📚</span>
          <span style={{ fontWeight: "bold" }}>Knowledge Base</span>
        </div>
        <p style={{ fontSize: "12px", color: "#999", margin: 0 }}>
          {documentCount} document{documentCount !== 1 ? "s" : ""} uploaded
        </p>
      </div>
    </aside>
  );
};
