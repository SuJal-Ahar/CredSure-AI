"use client";

import React from "react";
import {
  FileText,
  PieChart,
  ChevronRight,
  ShieldAlert,
  Download,
  RotateCcw,
} from "lucide-react";

interface AppHeaderProps {
  activeView: "application" | "portfolio";
  onViewChange: (view: "application" | "portfolio") => void;
  onReset?: () => void;
  applicantId?: string;
}

export const AppHeader: React.FC<AppHeaderProps> = ({
  activeView,
  onViewChange,
  onReset,
  applicantId = "#CFS-9410",
}) => {
  return (
    <header className="app-header">
      {/* Breadcrumb & Section Title */}
      <div className="header-title-wrap">
        <div className="header-breadcrumbs">
          <span>Credit Underwriting</span>
          <ChevronRight size={12} />
          <span>Institutional Facility</span>
          <ChevronRight size={12} />
          <span style={{ color: "#C56A4A", fontWeight: 600 }}>{applicantId}</span>
        </div>
        <h2>
          {activeView === "application"
            ? "Commercial Credit Assessment & AI Underwriting"
            : "Portfolio Risk & Basel Tail Loss Analytics"}
        </h2>
      </div>

      {/* Header Actions */}
      <div className="header-actions">
        {/* View Switcher segmented control */}
        <div className="segmented-control" style={{ width: 260 }}>
          <button
            type="button"
            onClick={() => onViewChange("application")}
            className={`segmented-btn ${activeView === "application" ? "active" : ""}`}
          >
            Credit Assessment
          </button>
          <button
            type="button"
            onClick={() => onViewChange("portfolio")}
            className={`segmented-btn ${activeView === "portfolio" ? "active" : ""}`}
          >
            Portfolio Risk (VaR)
          </button>
        </div>

        {onReset && (
          <button
            type="button"
            onClick={onReset}
            className="btn btn-secondary btn-sm"
            title="Reset to default facility request"
          >
            <RotateCcw size={12} />
            <span>Reset</span>
          </button>
        )}
      </div>
    </header>
  );
};
