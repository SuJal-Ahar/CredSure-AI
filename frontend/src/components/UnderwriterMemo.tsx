"use client";

import React, { useState } from "react";
import { MemoResponse } from "@/services/api";
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  FileCheck2,
  Copy,
  Check,
  TrendingDown,
  TrendingUp,
  FileText,
  Printer,
  Sparkles,
  ShieldAlert,
} from "lucide-react";

interface UnderwriterMemoProps {
  memo: MemoResponse | null;
  isLoading: boolean;
}

export const UnderwriterMemo: React.FC<UnderwriterMemoProps> = ({ memo, isLoading }) => {
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<"memo" | "factors" | "next_steps">("memo");

  const handleCopy = () => {
    if (!memo) return;
    navigator.clipboard.writeText(memo.memo_markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = () => {
    window.print();
  };

  // Loading State
  if (isLoading) {
    return (
      <div className="card">
        <div className="card-header">
          <span className="card-title">
            <Sparkles size={15} style={{ color: "#C56A4A" }} />
            Underwriting Engine
          </span>
          <span className="badge badge-accent">Processing</span>
        </div>
        <div
          className="card-body"
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: "48px 24px",
            textAlign: "center",
            gap: 16,
          }}
        >
          <div
            style={{
              width: 44,
              height: 44,
              borderRadius: "50%",
              border: "3px solid #EFECE4",
              borderTopColor: "#C56A4A",
              animation: "spin 0.8s linear infinite",
            }}
          />
          <div>
            <h4 style={{ fontSize: 14, fontWeight: 700, color: "#292524" }}>
              Evaluating Institutional Facility...
            </h4>
            <p style={{ fontSize: 12, color: "#78716C", marginTop: 4, maxWidth: 320 }}>
              Applying Weight of Evidence scorecard, computing Basel Expected Loss, and querying credit policy guidelines.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Polished Empty State
  if (!memo) {
    return (
      <div className="card">
        <div className="card-header">
          <span className="card-title">
            <FileCheck2 size={15} style={{ color: "#78716C" }} />
            Underwriting Determination
          </span>
          <span className="badge badge-neutral">Pending Submission</span>
        </div>
        <div
          className="card-body"
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: "40px 24px",
            textAlign: "center",
            gap: 14,
          }}
        >
          <div
            style={{
              width: 44,
              height: 44,
              borderRadius: 12,
              backgroundColor: "#FAF9F6",
              border: "1px solid #E7E2D9",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#78716C",
            }}
          >
            <FileCheck2 size={22} />
          </div>
          <div>
            <h4 style={{ fontSize: 14, fontWeight: 700, color: "#292524" }}>
              Application Awaiting Evaluation
            </h4>
            <p style={{ fontSize: 12, color: "#78716C", marginTop: 4, maxWidth: 300, lineHeight: 1.4 }}>
              Click <strong>&ldquo;Evaluate Credit Application&rdquo;</strong> to run statistical scorecard models and generate an official underwriting decision.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const pkg = memo.memo_package || {};
  const header = pkg.header || {};
  const scorecard = memo.scorecard || {};
  const adverse = pkg.adverse_action || {};

  const isApproved = memo.decision === "APPROVED";
  const isConditional = memo.decision === "CONDITIONAL";

  return (
    <div className="card">
      {/* Decision Status Header Banner */}
      <div
        style={{
          padding: "16px 20px",
          backgroundColor: isApproved ? "#F0FDF4" : isConditional ? "#FFFBEB" : "#FEF2F2",
          borderBottom: `1px solid ${isApproved ? "#BBF7D0" : isConditional ? "#FDE68A" : "#FECACA"}`,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              backgroundColor: "#FFFFFF",
              border: `1px solid ${isApproved ? "#BBF7D0" : isConditional ? "#FDE68A" : "#FECACA"}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "var(--shadow-xs)",
            }}
          >
            {isApproved ? (
              <CheckCircle size={18} style={{ color: "#15803D" }} />
            ) : isConditional ? (
              <AlertTriangle size={18} style={{ color: "#B45309" }} />
            ) : (
              <XCircle size={18} style={{ color: "#B91C1C" }} />
            )}
          </div>
          <div>
            <span
              style={{
                fontSize: 10,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.06em",
                color: isApproved ? "#15803D" : isConditional ? "#B45309" : "#B91C1C",
                display: "block",
              }}
            >
              Committee Determination
            </span>
            <h3 style={{ fontSize: 14, fontWeight: 700, color: "#292524", letterSpacing: "-0.01em" }}>
              {isApproved
                ? "FACILITY APPROVED"
                : isConditional
                ? "CONDITIONAL APPROVAL"
                : "APPLICATION DECLINED"}
            </h3>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <button
            type="button"
            onClick={handleCopy}
            className="btn btn-secondary btn-sm"
            title="Copy Memo Text"
          >
            {copied ? <Check size={12} style={{ color: "#15803D" }} /> : <Copy size={12} />}
            <span>{copied ? "Copied" : "Copy"}</span>
          </button>
          <button
            type="button"
            onClick={handlePrint}
            className="btn btn-secondary btn-sm"
            title="Print or Export PDF"
          >
            <Printer size={12} />
          </button>
        </div>
      </div>

      {/* Recommended Facility Terms Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 1,
          backgroundColor: "var(--border-color)",
          borderBottom: "1px solid var(--border-color)",
        }}
      >
        <div style={{ backgroundColor: "#FAF9F6", padding: "10px 14px" }}>
          <span style={{ fontSize: 10, fontWeight: 600, color: "#78716C", textTransform: "uppercase" }}>
            Credit Limit
          </span>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: 13, fontWeight: 700, color: "#292524", marginTop: 2 }}>
            {header.authorized_limit || "$50,000"}
          </p>
        </div>

        <div style={{ backgroundColor: "#FAF9F6", padding: "10px 14px" }}>
          <span style={{ fontSize: 10, fontWeight: 600, color: "#78716C", textTransform: "uppercase" }}>
            Utilization
          </span>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: 13, fontWeight: 700, color: "#292524", marginTop: 2 }}>
            {header.revolving_utilization || "0.0%"}
          </p>
        </div>

        <div style={{ backgroundColor: "#FAF9F6", padding: "10px 14px" }}>
          <span style={{ fontSize: 10, fontWeight: 600, color: "#78716C", textTransform: "uppercase" }}>
            Risk Grade
          </span>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: 13, fontWeight: 700, color: "#C56A4A", marginTop: 2 }}>
            {scorecard.risk_category || "Prime"}
          </p>
        </div>

        <div style={{ backgroundColor: "#FAF9F6", padding: "10px 14px" }}>
          <span style={{ fontSize: 10, fontWeight: 600, color: "#78716C", textTransform: "uppercase" }}>
            Expected Loss
          </span>
          <p style={{ fontFamily: "var(--font-mono)", fontSize: 13, fontWeight: 700, color: "#78716C", marginTop: 2 }}>
            ${(memo.basel_el?.expected_loss || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </p>
        </div>
      </div>

      {/* Sub-tabs */}
      <div style={{ padding: "12px 20px 0 20px" }}>
        <div className="segmented-control">
          <button
            type="button"
            onClick={() => setActiveTab("memo")}
            className={`segmented-btn ${activeTab === "memo" ? "active" : ""}`}
          >
            Underwriting Memorandum
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("factors")}
            className={`segmented-btn ${activeTab === "factors" ? "active" : ""}`}
          >
            Score Drivers & Basel
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("next_steps")}
            className={`segmented-btn ${activeTab === "next_steps" ? "active" : ""}`}
          >
            Next Steps & Action
          </button>
        </div>
      </div>

      <div className="card-body">
        {/* Tab 1: Underwriting Memorandum */}
        {activeTab === "memo" && (
          <div
            style={{
              backgroundColor: "#FAF9F6",
              border: "1px solid #E7E2D9",
              borderRadius: 10,
              padding: 16,
              fontSize: 12,
              lineHeight: 1.6,
              color: "#292524",
              whiteSpace: "pre-wrap",
              fontFamily: "var(--font-sans)",
            }}
          >
            {memo.memo_markdown}
          </div>
        )}

        {/* Tab 2: Point Drivers & Basel Breakdown */}
        {activeTab === "factors" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            {/* Positive Drivers */}
            <div>
              <span style={{ fontSize: 11, fontWeight: 600, color: "#15803D", display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
                <TrendingUp size={13} />
                Positive Score Contributors
              </span>
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {(scorecard.top_positive_drivers || []).length > 0 ? (
                  scorecard.top_positive_drivers.map((d: any, idx: number) => (
                    <div key={idx} className="driver-bar-item positive">
                      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                        <span style={{ fontWeight: 600, color: "#292524" }}>{d.label}</span>
                        <span className="badge badge-success" style={{ fontSize: 9 }}>
                          +{d.points} pts
                        </span>
                      </div>
                      <span style={{ fontSize: 10, color: "#78716C" }}>{d.description}</span>
                    </div>
                  ))
                ) : (
                  <span style={{ fontSize: 11, color: "#A8A29E", fontStyle: "italic" }}>
                    No significant positive drivers.
                  </span>
                )}
              </div>
            </div>

            {/* Negative Deductions */}
            <div>
              <span style={{ fontSize: 11, fontWeight: 600, color: "#B91C1C", display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
                <TrendingDown size={13} />
                Risk Factors & Deductions
              </span>
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {(scorecard.top_negative_drivers || []).length > 0 ? (
                  scorecard.top_negative_drivers.map((d: any, idx: number) => (
                    <div key={idx} className="driver-bar-item negative">
                      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                        <span style={{ fontWeight: 600, color: "#292524" }}>{d.label}</span>
                        <span className="badge badge-error" style={{ fontSize: 9 }}>
                          {d.points} pts
                        </span>
                      </div>
                      <span style={{ fontSize: 10, color: "#78716C" }}>{d.description}</span>
                    </div>
                  ))
                ) : (
                  <span style={{ fontSize: 11, color: "#A8A29E", fontStyle: "italic" }}>
                    Zero adverse risk deductions.
                  </span>
                )}
              </div>
            </div>

            {/* FCRA Adverse Notices if applicable */}
            {adverse.reasons && adverse.reasons.length > 0 && (
              <div
                style={{
                  padding: 12,
                  borderRadius: 9,
                  backgroundColor: "#FFFBEB",
                  border: "1px solid #FDE68A",
                  display: "flex",
                  flexDirection: "column",
                  gap: 6,
                }}
              >
                <span style={{ fontSize: 11, fontWeight: 700, color: "#B45309", textTransform: "uppercase" }}>
                  FCRA Statutory Adverse Action Disclosures
                </span>
                {adverse.reasons.map((r: any, idx: number) => (
                  <div key={idx} style={{ fontSize: 11, color: "#292524" }}>
                    <strong style={{ color: "#B45309" }}>[{r.code}]</strong> <strong>{r.title}:</strong> {r.detail}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Actionable Next Steps */}
        {activeTab === "next_steps" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ padding: 12, borderRadius: 9, backgroundColor: "#FAF9F6", border: "1px solid #E7E2D9" }}>
              <span style={{ fontSize: 11, fontWeight: 700, color: "#292524" }}>
                Underwriting Procedure
              </span>
              <p style={{ fontSize: 12, color: "#78716C", marginTop: 4, lineHeight: 1.4 }}>
                {isApproved
                  ? "Proceed with standard facility closing documentation. Deliver promissory note, schedule revolving facility draw parameters, and register lien per Tier 1 underwriting standards."
                  : isConditional
                  ? "Refer application to Credit Committee Manager for risk covenant exception approval. Require secondary cash flow verification and personal guarantee prior to disbursement."
                  : "Issue adverse action notification letter to applicant within 30 statutory days per Equal Credit Opportunity Act (ECOA) and FCRA Section 615 requirements."}
              </p>
            </div>

            <div style={{ fontSize: 11, color: "#78716C", borderTop: "1px solid #EFECE4", paddingTop: 8 }}>
              Attestation: <em>{memo.compliance_attestation || "Decision generated in adherence with institutional risk guidelines and Basel regulatory capital frameworks."}</em>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
