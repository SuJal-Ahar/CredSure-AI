"use client";

import React, { useState } from "react";
import { BorrowerFeatures, PresetBorrower } from "@/services/api";
import {
  CreditCard,
  User,
  History,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Gauge,
  Check,
} from "lucide-react";

interface BorrowerFormProps {
  features: BorrowerFeatures;
  onChange: (features: BorrowerFeatures) => void;
  onEvaluate: () => void;
  onGenerateMemo: () => void;
  presets: PresetBorrower[];
  isEvaluating: boolean;
  isGeneratingMemo: boolean;
}

export const BorrowerForm: React.FC<BorrowerFormProps> = ({
  features,
  onChange,
  onEvaluate,
  onGenerateMemo,
  presets,
  isEvaluating,
  isGeneratingMemo,
}) => {
  const [selectedPresetId, setSelectedPresetId] = useState<string>("custom");

  const updateField = (field: keyof BorrowerFeatures, val: number) => {
    setSelectedPresetId("custom");
    onChange({
      ...features,
      [field]: val,
    });
  };

  const setBatchFields = (updates: Partial<BorrowerFeatures>) => {
    setSelectedPresetId("custom");
    onChange({
      ...features,
      ...updates,
    });
  };

  // Live credit utilization calculation
  const utilizationRatio = features.LIMIT_BAL > 0
    ? Math.min(100, Math.max(0, (features.BILL_AMT1 / features.LIMIT_BAL) * 100))
    : 0;

  const applicantPresets = [
    {
      id: "prime",
      name: "Prime Applicant",
      category: "Tier 1 Retail",
      desc: "Impeccable payment history, conservative leverage, optimal credit profile.",
      badge: "Prime A+",
      badgeClass: "badge-success",
      icon: ShieldCheck,
      iconColor: "#15803D",
      features: presets[0]?.features || {
        ...features,
        LIMIT_BAL: 120000,
        BILL_AMT1: 15000,
        PAY_AMT1: 15000,
        AGE: 42,
        EDUCATION: 1,
        MARRIAGE: 1,
        PAY_0: 0,
        PAY_2: 0,
        PAY_3: 0,
        PAY_4: 0,
        PAY_5: 0,
        PAY_6: 0,
      },
    },
    {
      id: "delinquent",
      name: "High-Risk Applicant",
      category: "Adverse Watchlist",
      desc: "Delinquency track record, elevated balance draw, revolving debt strain.",
      badge: "Subprime C",
      badgeClass: "badge-error",
      icon: AlertTriangle,
      iconColor: "#B91C1C",
      features: presets[1]?.features || {
        ...features,
        LIMIT_BAL: 30000,
        BILL_AMT1: 27800,
        PAY_AMT1: 1200,
        AGE: 29,
        EDUCATION: 3,
        MARRIAGE: 2,
        PAY_0: 2,
        PAY_2: 2,
        PAY_3: 1,
        PAY_4: 0,
        PAY_5: 0,
        PAY_6: 0,
      },
    },
    {
      id: "graduate",
      name: "Emerging Applicant",
      category: "Near-Prime Tier",
      desc: "Early career professional with growing credit facility and clean history.",
      badge: "Near-Prime B",
      badgeClass: "badge-accent",
      icon: User,
      iconColor: "#C56A4A",
      features: presets[2]?.features || {
        ...features,
        LIMIT_BAL: 50000,
        BILL_AMT1: 18500,
        PAY_AMT1: 4500,
        AGE: 27,
        EDUCATION: 1,
        MARRIAGE: 2,
        PAY_0: 0,
        PAY_2: 0,
        PAY_3: 0,
        PAY_4: 0,
        PAY_5: 0,
        PAY_6: 0,
      },
    },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      {/* 1. Applicant Profile Presets Section */}
      <div className="card">
        <div className="card-header">
          <div>
            <span className="card-title">
              <User size={15} style={{ color: "#C56A4A" }} />
              Applicant Profile Presets
            </span>
            <span className="card-subtitle">
              Select an archetype to instantly evaluate underwriting decisions
            </span>
          </div>
          <span style={{ fontSize: 11, color: "#78716C" }}>3 Benchmark Archetypes</span>
        </div>

        <div className="card-body">
          <div className="preset-grid">
            {applicantPresets.map((p) => {
              const isSelected = selectedPresetId === p.id;
              const Icon = p.icon;
              return (
                <div
                  key={p.id}
                  onClick={() => {
                    setSelectedPresetId(p.id);
                    onChange(p.features);
                  }}
                  className={`preset-card ${isSelected ? "selected" : ""}`}
                >
                  <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 8 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <div
                        style={{
                          width: 28,
                          height: 28,
                          borderRadius: 7,
                          backgroundColor: "#FAF9F6",
                          border: "1px solid #E7E2D9",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          color: p.iconColor,
                        }}
                      >
                        <Icon size={15} />
                      </div>
                      <div>
                        <span className="preset-title">{p.name}</span>
                        <span style={{ fontSize: 10, color: "#78716C", display: "block" }}>
                          {p.category}
                        </span>
                      </div>
                    </div>
                    <span className={`badge ${p.badgeClass}`}>{p.badge}</span>
                  </div>

                  <p className="preset-desc">{p.desc}</p>

                  <div className="preset-meta">
                    <span>${p.features.LIMIT_BAL.toLocaleString()} Line</span>
                    <span>{p.features.AGE} Yrs</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* 2. Facility Request & Balance Exposure Card */}
      <div className="card">
        <div className="card-header">
          <div>
            <span className="card-title">
              <CreditCard size={15} style={{ color: "#C56A4A" }} />
              Facility Request & Exposure Limits
            </span>
            <span className="card-subtitle">
              Contractual credit lines, drawn statement balances, and monthly debt amortization
            </span>
          </div>
        </div>

        <div className="card-body form-section">
          {/* Live Credit Utilization Meter */}
          <div
            style={{
              padding: "14px 16px",
              borderRadius: 10,
              backgroundColor: utilizationRatio < 30 ? "#F0FDF4" : utilizationRatio < 60 ? "#FFFBEB" : "#FEF2F2",
              border: `1px solid ${utilizationRatio < 30 ? "#BBF7D0" : utilizationRatio < 60 ? "#FDE68A" : "#FECACA"}`,
              display: "flex",
              flexDirection: "column",
              gap: 8,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: 12 }}>
              <span style={{ fontWeight: 600, color: "#292524", display: "flex", alignItems: "center", gap: 6 }}>
                <Gauge size={14} style={{ color: utilizationRatio < 30 ? "#15803D" : utilizationRatio < 60 ? "#B45309" : "#B91C1C" }} />
                Real-Time Revolving Utilization
              </span>
              <span
                style={{
                  fontFamily: "var(--font-mono)",
                  fontWeight: 700,
                  fontSize: 12,
                  color: utilizationRatio < 30 ? "#15803D" : utilizationRatio < 60 ? "#B45309" : "#B91C1C",
                }}
              >
                {utilizationRatio.toFixed(1)}% •{" "}
                {utilizationRatio < 30 ? "Optimal Tier (<30%)" : utilizationRatio < 60 ? "Moderate Leverage" : "High Leverage Alert"}
              </span>
            </div>

            <div className="utilization-bar-wrap">
              <div
                className="utilization-bar-fill"
                style={{
                  width: `${Math.min(utilizationRatio, 100)}%`,
                  backgroundColor: utilizationRatio < 30 ? "#15803D" : utilizationRatio < 60 ? "#D97706" : "#DC2626",
                }}
              />
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 16 }}>
            {/* Input 1: Requested Credit Facility */}
            <div className="form-group">
              <div className="form-label">
                <span>Requested Credit Line</span>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 13, color: "#C56A4A" }}>
                  ${features.LIMIT_BAL.toLocaleString()}
                </span>
              </div>
              <div className="input-container">
                <span className="input-prefix">$</span>
                <input
                  type="number"
                  step="5000"
                  min="5000"
                  max="500000"
                  value={features.LIMIT_BAL}
                  onChange={(e) => updateField("LIMIT_BAL", parseFloat(e.target.value) || 0)}
                  className="input-field"
                />
              </div>
              <input
                type="range"
                min="10000"
                max="300000"
                step="5000"
                value={features.LIMIT_BAL}
                onChange={(e) => updateField("LIMIT_BAL", parseFloat(e.target.value))}
              />
              <div className="chip-group">
                <span style={{ fontSize: 10, color: "#78716C" }}>Presets:</span>
                {[25000, 50000, 100000, 200000].map((amt) => (
                  <button
                    key={amt}
                    type="button"
                    onClick={() => updateField("LIMIT_BAL", amt)}
                    className={`chip-btn ${features.LIMIT_BAL === amt ? "active" : ""}`}
                  >
                    ${(amt / 1000).toFixed(0)}k
                  </button>
                ))}
              </div>
            </div>

            {/* Input 2: Current Statement Balance */}
            <div className="form-group">
              <div className="form-label">
                <span>Current Statement Balance</span>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 13, color: "#292524" }}>
                  ${features.BILL_AMT1.toLocaleString()}
                </span>
              </div>
              <div className="input-container">
                <span className="input-prefix">$</span>
                <input
                  type="number"
                  step="500"
                  min="0"
                  max="300000"
                  value={features.BILL_AMT1}
                  onChange={(e) => updateField("BILL_AMT1", parseFloat(e.target.value) || 0)}
                  className="input-field"
                />
              </div>
              <input
                type="range"
                min="0"
                max={Math.max(features.LIMIT_BAL, 100000)}
                step="1000"
                value={features.BILL_AMT1}
                onChange={(e) => updateField("BILL_AMT1", parseFloat(e.target.value))}
              />
              <div className="chip-group">
                <span style={{ fontSize: 10, color: "#78716C" }}>Exposure:</span>
                <button
                  type="button"
                  onClick={() => updateField("BILL_AMT1", 0)}
                  className="chip-btn"
                >
                  0% (Paid)
                </button>
                <button
                  type="button"
                  onClick={() => updateField("BILL_AMT1", Math.round(features.LIMIT_BAL * 0.25))}
                  className="chip-btn"
                >
                  25% (Safe)
                </button>
                <button
                  type="button"
                  onClick={() => updateField("BILL_AMT1", Math.round(features.LIMIT_BAL * 0.55))}
                  className="chip-btn"
                >
                  55% (Moderate)
                </button>
                <button
                  type="button"
                  onClick={() => updateField("BILL_AMT1", Math.round(features.LIMIT_BAL * 0.85))}
                  className="chip-btn"
                >
                  85% (Heavy)
                </button>
              </div>
            </div>

            {/* Input 3: Recent Monthly Payment */}
            <div className="form-group">
              <div className="form-label">
                <span>Recent Monthly Payment</span>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 13, color: "#15803D" }}>
                  ${features.PAY_AMT1.toLocaleString()}
                </span>
              </div>
              <div className="input-container">
                <span className="input-prefix" style={{ color: "#15803D" }}>$</span>
                <input
                  type="number"
                  step="500"
                  min="0"
                  max="100000"
                  value={features.PAY_AMT1}
                  onChange={(e) => updateField("PAY_AMT1", parseFloat(e.target.value) || 0)}
                  className="input-field"
                />
              </div>
              <input
                type="range"
                min="0"
                max={Math.max(features.BILL_AMT1, 25000)}
                step="500"
                value={features.PAY_AMT1}
                onChange={(e) => updateField("PAY_AMT1", parseFloat(e.target.value))}
              />
              <div className="chip-group">
                <span style={{ fontSize: 10, color: "#78716C" }}>Amortization:</span>
                <button
                  type="button"
                  onClick={() => updateField("PAY_AMT1", Math.round(features.BILL_AMT1 * 0.05))}
                  className="chip-btn"
                >
                  Min 5%
                </button>
                <button
                  type="button"
                  onClick={() => updateField("PAY_AMT1", Math.round(features.BILL_AMT1 * 0.5))}
                  className="chip-btn"
                >
                  50% Partial
                </button>
                <button
                  type="button"
                  onClick={() => updateField("PAY_AMT1", features.BILL_AMT1)}
                  className="chip-btn"
                  style={{ color: "#15803D", borderColor: "#BBF7D0", backgroundColor: "#F0FDF4" }}
                >
                  100% Full Payoff
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Applicant Profile — each field explains WHY it matters */}
      <div className="card">
        <div className="card-header">
          <div>
            <span className="card-title">
              <User size={15} style={{ color: "#C56A4A" }} />
              Applicant Profile
            </span>
            <span className="card-subtitle">
              These factors carry real weight in the scorecard — here's how each one affects the credit decision
            </span>
          </div>
        </div>

        <div className="card-body" style={{ display: "flex", flexDirection: "column", gap: 20 }}>

          {/* ── AGE ── */}
          <div style={{ backgroundColor: "#FAF9F6", border: "1px solid #E7E2D9", borderRadius: 11, padding: 16, display: "flex", flexDirection: "column", gap: 10 }}>
            <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
              <div>
                <div className="form-label" style={{ marginBottom: 2 }}>
                  <span>Borrower Age</span>
                </div>
                <p style={{ fontSize: 11, color: "#78716C", lineHeight: 1.4, maxWidth: 460 }}>
                  Older borrowers statistically default less — they have longer credit histories, stable income, and more assets.
                  The scorecard groups age into 4 risk bands.
                </p>
              </div>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: 15, fontWeight: 700, color: "#292524", whiteSpace: "nowrap" }}>
                {features.AGE} yrs
              </span>
            </div>

            <input
              type="range"
              min="20"
              max="75"
              step="1"
              value={features.AGE}
              onChange={(e) => updateField("AGE", parseInt(e.target.value) || 30)}
            />

            {/* Live age band indicator */}
            <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11 }}>
              <span
                className={`badge ${
                  features.AGE >= 50 ? "badge-success" :
                  features.AGE >= 35 ? "badge-success" :
                  features.AGE >= 26 ? "badge-accent" :
                  "badge-error"
                }`}
              >
                {features.AGE >= 50 ? "Mature (50+)" :
                 features.AGE >= 35 ? "Prime Career (35-49)" :
                 features.AGE >= 26 ? "Young Professional (26-34)" :
                 "Entry Age (18-25)"}
              </span>
              <span style={{ color: "#78716C" }}>→</span>
              <span style={{
                fontWeight: 700,
                fontFamily: "var(--font-mono)",
                color: features.AGE >= 26 ? "#15803D" : "#B91C1C",
              }}>
                {features.AGE >= 50 ? "+14 pts" :
                 features.AGE >= 35 ? "+12 pts" :
                 features.AGE >= 26 ? "+1 pt" :
                 "−12 pts"}
              </span>
              <span style={{ color: "#A8A29E", fontSize: 10 }}>
                (weight: 0.50× — moderate influence)
              </span>
            </div>
          </div>

          {/* ── EDUCATION ── */}
          <div style={{ backgroundColor: "#FAF9F6", border: "1px solid #E7E2D9", borderRadius: 11, padding: 16, display: "flex", flexDirection: "column", gap: 10 }}>
            <div>
              <div className="form-label" style={{ marginBottom: 2 }}>
                <span>Highest Education</span>
              </div>
              <p style={{ fontSize: 11, color: "#78716C", lineHeight: 1.4, maxWidth: 500 }}>
                Higher education correlates with higher income stability and lower default rates.
                Graduate degree holders get the biggest boost; high school only gets a penalty.
                This isn't about intelligence — it's about statistical employment stability patterns.
              </p>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8 }}>
              {[
                { val: 1, label: "Graduate Degree", sub: "Master's / PhD", pts: "+10 pts", color: "#15803D" },
                { val: 2, label: "University", sub: "4-year Bachelor's", pts: "+2 pts", color: "#15803D" },
                { val: 3, label: "High School", sub: "Secondary diploma", pts: "−8 pts", color: "#B91C1C" },
              ].map((ed) => {
                const isActive = features.EDUCATION === ed.val;
                return (
                  <button
                    key={ed.val}
                    type="button"
                    onClick={() => updateField("EDUCATION", ed.val)}
                    style={{
                      padding: "12px 10px",
                      borderRadius: 9,
                      border: isActive ? "1.5px solid #C56A4A" : "1.5px solid #E7E2D9",
                      backgroundColor: isActive ? "#FFFDFB" : "#FFFFFF",
                      boxShadow: isActive ? "0 0 0 2px rgba(197,106,74,0.15)" : "none",
                      cursor: "pointer",
                      textAlign: "left",
                      display: "flex",
                      flexDirection: "column",
                      gap: 4,
                      transition: "all 0.15s ease",
                    }}
                  >
                    <span style={{ fontSize: 12, fontWeight: 600, color: isActive ? "#C56A4A" : "#292524" }}>
                      {ed.label}
                    </span>
                    <span style={{ fontSize: 10, color: "#78716C" }}>{ed.sub}</span>
                    <span style={{ fontSize: 11, fontWeight: 700, fontFamily: "var(--font-mono)", color: ed.color, marginTop: 2 }}>
                      {ed.pts}
                    </span>
                  </button>
                );
              })}
            </div>

            <span style={{ fontSize: 10, color: "#A8A29E" }}>
              Weight: 0.35× — minor influence on total score, but visible in point drivers
            </span>
          </div>

          {/* ── MARITAL STATUS ── */}
          <div style={{ backgroundColor: "#FAF9F6", border: "1px solid #E7E2D9", borderRadius: 11, padding: 16, display: "flex", flexDirection: "column", gap: 10 }}>
            <div>
              <div className="form-label" style={{ marginBottom: 2 }}>
                <span>Marital Status</span>
              </div>
              <p style={{ fontSize: 11, color: "#78716C", lineHeight: 1.4, maxWidth: 500 }}>
                Married borrowers tend to have dual-income household stability and shared financial obligations,
                which statistically lowers individual default risk. Single borrowers carry slightly more risk
                due to single-income dependency. The effect is small — only 0.25× weight.
              </p>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8 }}>
              {[
                { val: 1, label: "Married", sub: "Dual-income household", pts: "+4 pts", color: "#15803D" },
                { val: 2, label: "Single", sub: "Single-income earner", pts: "−4 pts", color: "#B91C1C" },
                { val: 3, label: "Other", sub: "Divorced / Separated", pts: "±0 pts", color: "#78716C" },
              ].map((m) => {
                const isActive = features.MARRIAGE === m.val;
                return (
                  <button
                    key={m.val}
                    type="button"
                    onClick={() => updateField("MARRIAGE", m.val)}
                    style={{
                      padding: "12px 10px",
                      borderRadius: 9,
                      border: isActive ? "1.5px solid #C56A4A" : "1.5px solid #E7E2D9",
                      backgroundColor: isActive ? "#FFFDFB" : "#FFFFFF",
                      boxShadow: isActive ? "0 0 0 2px rgba(197,106,74,0.15)" : "none",
                      cursor: "pointer",
                      textAlign: "left",
                      display: "flex",
                      flexDirection: "column",
                      gap: 4,
                      transition: "all 0.15s ease",
                    }}
                  >
                    <span style={{ fontSize: 12, fontWeight: 600, color: isActive ? "#C56A4A" : "#292524" }}>
                      {m.label}
                    </span>
                    <span style={{ fontSize: 10, color: "#78716C" }}>{m.sub}</span>
                    <span style={{ fontSize: 11, fontWeight: 700, fontFamily: "var(--font-mono)", color: m.color, marginTop: 2 }}>
                      {m.pts}
                    </span>
                  </button>
                );
              })}
            </div>

            <span style={{ fontSize: 10, color: "#A8A29E" }}>
              Weight: 0.25× — lowest influence among all scored features
            </span>
          </div>

          {/* ── ACCOUNT CLASSIFICATION ── */}
          <div style={{ backgroundColor: "#FAF9F6", border: "1px solid #E7E2D9", borderRadius: 11, padding: 16, display: "flex", flexDirection: "column", gap: 10 }}>
            <div>
              <div className="form-label" style={{ marginBottom: 2 }}>
                <span>Account Type</span>
              </div>
              <p style={{ fontSize: 11, color: "#78716C", lineHeight: 1.4, maxWidth: 500 }}>
                This distinguishes between a personal retail credit card borrower and a sole-proprietor
                commercial facility. Commercial accounts have different risk profiles and regulatory
                capital requirements under Basel frameworks.
              </p>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 8 }}>
              {[
                { val: 2, label: "Retail Individual", sub: "Personal consumer credit line — standard retail underwriting rules apply" },
                { val: 1, label: "Commercial / Sole Proprietor", sub: "Business owner facility — subject to commercial credit policies and higher LGD assumptions" },
              ].map((c) => {
                const isActive = features.SEX === c.val;
                return (
                  <button
                    key={c.val}
                    type="button"
                    onClick={() => updateField("SEX", c.val)}
                    style={{
                      padding: "14px 12px",
                      borderRadius: 9,
                      border: isActive ? "1.5px solid #C56A4A" : "1.5px solid #E7E2D9",
                      backgroundColor: isActive ? "#FFFDFB" : "#FFFFFF",
                      boxShadow: isActive ? "0 0 0 2px rgba(197,106,74,0.15)" : "none",
                      cursor: "pointer",
                      textAlign: "left",
                      display: "flex",
                      flexDirection: "column",
                      gap: 4,
                      transition: "all 0.15s ease",
                    }}
                  >
                    <span style={{ fontSize: 12, fontWeight: 600, color: isActive ? "#C56A4A" : "#292524" }}>
                      {c.label}
                    </span>
                    <span style={{ fontSize: 10, color: "#78716C", lineHeight: 1.3 }}>{c.sub}</span>
                  </button>
                );
              })}
            </div>

            <span style={{ fontSize: 10, color: "#A8A29E" }}>
              This field determines the regulatory track (retail vs. commercial) — does not directly add/subtract score points
            </span>
          </div>

          {/* Scoring weight summary */}
          <div style={{
            padding: "10px 14px",
            borderRadius: 9,
            backgroundColor: "#FFFFFF",
            border: "1px solid #E7E2D9",
            fontSize: 11,
            color: "#78716C",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}>
            <span>
              <strong style={{ color: "#292524" }}>How much do these fields matter?</strong>{" "}
              These 4 fields carry only ~13% of total scorecard weight. The remaining ~87% comes from repayment history, utilization, and payment ratio.
            </span>
            <span className="badge badge-neutral">Low Weight</span>
          </div>
        </div>
      </div>

      {/* 4. Payment History (Delinquency Track Record) */}
      <div className="card">
        <div className="card-header">
          <div>
            <span className="card-title">
              <History size={15} style={{ color: "#C56A4A" }} />
              Repayment History (Last 6 Billing Cycles)
            </span>
            <span className="card-subtitle">
              Past-due status across historical statement cycles (primary scorecard weight)
            </span>
          </div>

          {/* Quick Scenario Shortcuts */}
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <button
              type="button"
              onClick={() =>
                setBatchFields({
                  PAY_0: 0,
                  PAY_2: 0,
                  PAY_3: 0,
                  PAY_4: 0,
                  PAY_5: 0,
                  PAY_6: 0,
                })
              }
              className="btn btn-secondary btn-sm"
              style={{ color: "#15803D" }}
            >
              <Check size={11} />
              <span>All Clean</span>
            </button>
            <button
              type="button"
              onClick={() =>
                setBatchFields({
                  PAY_0: 1,
                  PAY_2: 0,
                  PAY_3: 0,
                  PAY_4: 0,
                  PAY_5: 0,
                  PAY_6: 0,
                })
              }
              className="btn btn-secondary btn-sm"
              style={{ color: "#B45309" }}
            >
              <span>30d Delay</span>
            </button>
            <button
              type="button"
              onClick={() =>
                setBatchFields({
                  PAY_0: 2,
                  PAY_2: 2,
                  PAY_3: 1,
                  PAY_4: 0,
                  PAY_5: 0,
                  PAY_6: 0,
                })
              }
              className="btn btn-secondary btn-sm"
              style={{ color: "#B91C1C" }}
            >
              <span>Chronic Delinquency</span>
            </button>
          </div>
        </div>

        <div className="card-body">
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12 }}>
            {[
              { id: "PAY_0", label: "Cycle 1 (Current)", key: "PAY_0" as const },
              { id: "PAY_2", label: "Cycle 2 (1 Mo)", key: "PAY_2" as const },
              { id: "PAY_3", label: "Cycle 3 (2 Mo)", key: "PAY_3" as const },
              { id: "PAY_4", label: "Cycle 4 (3 Mo)", key: "PAY_4" as const },
              { id: "PAY_5", label: "Cycle 5 (4 Mo)", key: "PAY_5" as const },
              { id: "PAY_6", label: "Cycle 6 (5 Mo)", key: "PAY_6" as const },
            ].map((cycle) => {
              const currentVal = features[cycle.key];
              return (
                <div
                  key={cycle.id}
                  style={{
                    backgroundColor: "#FAF9F6",
                    border: "1px solid #E7E2D9",
                    borderRadius: 10,
                    padding: 10,
                    display: "flex",
                    flexDirection: "column",
                    gap: 6,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <span style={{ fontSize: 11, fontWeight: 600, color: "#292524" }}>
                      {cycle.label}
                    </span>
                    <span
                      className={`badge ${
                        currentVal <= 0 ? "badge-success" : currentVal === 1 ? "badge-warning" : "badge-error"
                      }`}
                    >
                      {currentVal <= 0 ? "Clean" : currentVal === 1 ? "30d Delay" : "60d+ Past"}
                    </span>
                  </div>

                  <div className="segmented-control" style={{ padding: 2 }}>
                    {[
                      { val: 0, label: "Clean" },
                      { val: 1, label: "30d" },
                      { val: 2, label: "60d" },
                      { val: 3, label: "90d+" },
                    ].map((pill) => {
                      const isActive =
                        pill.val === 0
                          ? currentVal <= 0
                          : pill.val === 3
                          ? currentVal >= 3
                          : currentVal === pill.val;

                      return (
                        <button
                          key={pill.val}
                          type="button"
                          onClick={() => updateField(cycle.key, pill.val)}
                          className={`segmented-btn ${isActive ? "active" : ""}`}
                          style={{
                            fontSize: 10,
                            padding: "4px 6px",
                            color: isActive
                              ? pill.val === 0
                                ? "#15803D"
                                : pill.val === 1
                                ? "#B45309"
                                : "#B91C1C"
                              : undefined,
                          }}
                        >
                          {pill.label}
                        </button>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Primary Action Button */}
      <div>
        <button
          type="button"
          onClick={onGenerateMemo}
          disabled={isGeneratingMemo}
          className="btn btn-primary btn-lg"
          style={{ width: "100%", padding: "14px 24px", fontSize: 14 }}
        >
          {isGeneratingMemo ? (
            <>
              <div
                style={{
                  width: 16,
                  height: 16,
                  borderRadius: "50%",
                  border: "2px solid rgba(255,255,255,0.3)",
                  borderTopColor: "#FFFFFF",
                  animation: "spin 0.8s linear infinite",
                }}
              />
              <span>Underwriting Facility with AI Committee...</span>
            </>
          ) : (
            <>
              <Sparkles size={16} />
              <span>Evaluate Credit Application & Underwrite with AI</span>
              <ArrowRight size={16} />
            </>
          )}
        </button>
      </div>
    </div>
  );
};
