"use client";

import React from "react";
import {
  ShieldCheck,
  FilePlus2,
  PieChart,
  History,
  FileCheck2,
  Sliders,
  LogOut,
  ChevronRight,
  Database,
  Cpu,
} from "lucide-react";

interface AppSidebarProps {
  activeView: "application" | "portfolio";
  onViewChange: (view: "application" | "portfolio") => void;
  systemOnline?: boolean;
}

export const AppSidebar: React.FC<AppSidebarProps> = ({
  activeView,
  onViewChange,
  systemOnline = true,
}) => {
  return (
    <aside className="app-sidebar">
      {/* Brand Header */}
      <div className="sidebar-header">
        <div
          style={{
            width: 38,
            height: 38,
            borderRadius: 10,
            backgroundColor: "#FBF0EB",
            border: "1px solid #F0C4B4",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#C56A4A",
          }}
        >
          <ShieldCheck size={22} />
        </div>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ fontSize: 16, fontWeight: 700, color: "#292524", letterSpacing: "-0.01em" }}>
              CredSure <span style={{ color: "#C56A4A" }}>AI</span>
            </span>
          </div>
          <span style={{ fontSize: 11, color: "#78716C", fontWeight: 500, display: "block" }}>
            Credit Underwriting OS
          </span>
        </div>
      </div>

      {/* Navigation Sections */}
      <nav className="sidebar-nav">
        <span className="nav-section-title">Underwriting Core</span>

        <button
          type="button"
          onClick={() => onViewChange("application")}
          className={`sidebar-nav-item ${activeView === "application" ? "active" : ""}`}
        >
          <FilePlus2 size={16} />
          <span>New Assessment</span>
        </button>

        <button
          type="button"
          onClick={() => onViewChange("portfolio")}
          className={`sidebar-nav-item ${activeView === "portfolio" ? "active" : ""}`}
        >
          <PieChart size={16} />
          <span>Portfolio Risk & VaR</span>
        </button>

        <span className="nav-section-title" style={{ marginTop: 8 }}>Institutional Tools</span>

        <button
          type="button"
          onClick={() => onViewChange("application")}
          className="sidebar-nav-item"
        >
          <History size={16} />
          <span>Facility Pipeline (30k)</span>
        </button>

        <button
          type="button"
          onClick={() => onViewChange("application")}
          className="sidebar-nav-item"
        >
          <FileCheck2 size={16} />
          <span>Policy Vectors (Qdrant)</span>
        </button>

        {/* Engine Status Banner inside Navigation */}
        <div
          style={{
            marginTop: "auto",
            padding: "12px",
            borderRadius: 10,
            backgroundColor: "#FAF8F5",
            border: "1px solid #E7E2D9",
            display: "flex",
            flexDirection: "column",
            gap: 6,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", color: "#78716C" }}>
              Analytics Engine
            </span>
            <span
              style={{
                width: 7,
                height: 7,
                borderRadius: "50%",
                backgroundColor: systemOnline ? "#15803D" : "#B45309",
                display: "inline-block",
              }}
            />
          </div>
          <span style={{ fontSize: 11, fontWeight: 600, color: "#292524" }}>
            Pure Statistical Scorecard
          </span>
          <span style={{ fontSize: 10, color: "#78716C" }}>
            NumPy/Pandas WoE • Basel II/III
          </span>
        </div>
      </nav>

      {/* User Profile Footer */}
      <div className="sidebar-footer">
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 34,
              height: 34,
              borderRadius: "50%",
              backgroundColor: "#EFECE4",
              border: "1px solid #E7E2D9",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: 700,
              fontSize: 12,
              color: "#292524",
            }}
          >
            SA
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <p style={{ fontSize: 12, fontWeight: 600, color: "#292524", lineHeight: 1.2 }}>
              Sujal Ahar
            </p>
            <span style={{ fontSize: 10, color: "#78716C", display: "block" }}>
              Senior Risk Underwriter
            </span>
          </div>
          <span className="badge badge-accent" style={{ fontSize: 9 }}>
            Tier 1
          </span>
        </div>
      </div>
    </aside>
  );
};
