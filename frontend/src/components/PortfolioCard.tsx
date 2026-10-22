"use client";

import React, { useState } from "react";
import { PortfolioMetricsResponse, StressTestResponse, api } from "@/services/api";
import {
  Layers,
  Activity,
  Play,
  RefreshCw,
  BarChart3,
  ShieldCheck,
  AlertTriangle,
  Flame,
} from "lucide-react";

interface PortfolioCardProps {
  metrics: PortfolioMetricsResponse | null;
  onRefreshMetrics: () => void;
  isLoading: boolean;
}

export const PortfolioCard: React.FC<PortfolioCardProps> = ({
  metrics,
  onRefreshMetrics,
  isLoading,
}) => {
  const [delayShift, setDelayShift] = useState(1);
  const [balanceShock, setBalanceShock] = useState(15);
  const [pdMult, setPdMult] = useState(1.3);
  const [stressedLgd, setStressedLgd] = useState(0.55);
  const [stressResult, setStressResult] = useState<StressTestResponse | null>(null);
  const [isStressTesting, setIsStressTesting] = useState(false);
  const [activeScenario, setActiveScenario] = useState<string>("recession");

  const runScenarioWithParams = async (
    name: string,
    shift: number,
    shock: number,
    pd: number,
    lgd: number
  ) => {
    setDelayShift(shift);
    setBalanceShock(shock);
    setPdMult(pd);
    setStressedLgd(lgd);
    setIsStressTesting(true);

    try {
      const res = await api.runStressTest({
        scenario_name: name,
        delay_shift: shift,
        balance_shock_pct: shock,
        pd_multiplier: pd,
        stressed_lgd: lgd,
      });
      setStressResult(res);
    } catch (e) {
      console.error("Stress test failed:", e);
    } finally {
      setIsStressTesting(false);
    }
  };

  const handleRunStressTest = () => {
    runScenarioWithParams("Custom Stress Scenario", delayShift, balanceShock, pdMult, stressedLgd);
  };

  if (!metrics) {
    return (
      <div className="card">
        <div className="card-body" style={{ padding: 48, textAlign: "center" }}>
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: "50%",
              backgroundColor: "#FAF9F6",
              border: "1px solid #E7E2D9",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 12px auto",
              color: "#C56A4A",
            }}
          >
            <RefreshCw size={18} className="animate-spin" />
          </div>
          <h4 style={{ fontSize: 14, fontWeight: 700, color: "#292524" }}>
            Computing Portfolio Risk Metrics...
          </h4>
          <p style={{ fontSize: 12, color: "#78716C", marginTop: 4 }}>
            Aggregating Basel II/III capital charges and 1,000-scenario Monte Carlo simulations.
          </p>
        </div>
      </div>
    );
  }

  const tiers = metrics.risk_tier_counts;
  const totalTierLoans = Object.values(tiers).reduce((a, b) => a + b, 0) || 1;

  const presets = [
    {
      id: "baseline",
      name: "Normal Baseline",
      desc: "Contractual parameters",
      shift: 0,
      shock: 0,
      pd: 1.0,
      lgd: 0.45,
      icon: ShieldCheck,
      color: "#15803D",
    },
    {
      id: "recession",
      name: "Mild Recession",
      desc: "+1 mo delay, +15% bal, 1.3x PD",
      shift: 1,
      shock: 15,
      pd: 1.3,
      lgd: 0.55,
      icon: Activity,
      color: "#B45309",
    },
    {
      id: "crisis",
      name: "2008 Financial Shock",
      desc: "+2 mo delay, +25% bal, 1.8x PD",
      shift: 2,
      shock: 25,
      pd: 1.8,
      lgd: 0.65,
      icon: AlertTriangle,
      color: "#DC2626",
    },
    {
      id: "stagflation",
      name: "Severe Stagflation",
      desc: "+3 mo delay, +30% bal, 2.2x PD",
      shift: 3,
      shock: 30,
      pd: 2.2,
      lgd: 0.70,
      icon: Flame,
      color: "#7F1D1D",
    },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      {/* Portfolio Basel Capital Summary */}
      <div className="card">
        <div className="card-header">
          <div>
            <span className="card-title">
              <Layers size={15} style={{ color: "#C56A4A" }} />
              Institutional Portfolio Risk & Capital Adequacy
            </span>
            <span className="card-subtitle">
              Basel Expected Loss (EL) and 1,000-scenario Monte Carlo Value at Risk (VaR)
            </span>
          </div>

          <button
            type="button"
            onClick={onRefreshMetrics}
            disabled={isLoading}
            className="btn btn-secondary btn-sm"
          >
            <RefreshCw size={12} className={isLoading ? "animate-spin" : ""} />
            <span>{isLoading ? "Recalculating..." : "Refresh Portfolio"}</span>
          </button>
        </div>

        <div className="card-body" style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          {/* Top 4 Basel Metrics */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12 }}>
            <div className="metric-box">
              <span className="metric-box-title">Total Exposure (EAD)</span>
              <p className="metric-box-value">${(metrics.total_ead / 1000000).toFixed(2)}M</p>
              <span style={{ fontSize: 10, color: "#78716C" }}>
                {metrics.total_records.toLocaleString()} Active Facilities
              </span>
            </div>

            <div className="metric-box">
              <span className="metric-box-title">Basel Expected Loss (EL)</span>
              <p className="metric-box-value" style={{ color: "#C56A4A" }}>
                ${(metrics.total_expected_loss / 1000).toFixed(1)}k
              </p>
              <span style={{ fontSize: 10, color: "#78716C" }}>
                {metrics.portfolio_el_rate_bps.toFixed(0)} bps Provision Rate
              </span>
            </div>

            <div className="metric-box">
              <span className="metric-box-title">Monte Carlo VaR 95%</span>
              <p className="metric-box-value" style={{ color: "#B45309" }}>
                ${(metrics.var_95 / 1000).toFixed(1)}k
              </p>
              <span style={{ fontSize: 10, color: "#78716C" }}>
                CVaR: ${(metrics.cvar_95 / 1000).toFixed(1)}k
              </span>
            </div>

            <div className="metric-box">
              <span className="metric-box-title">Extreme Tail VaR 99%</span>
              <p className="metric-box-value" style={{ color: "#B91C1C" }}>
                ${(metrics.var_99 / 1000).toFixed(1)}k
              </p>
              <span style={{ fontSize: 10, color: "#78716C" }}>
                Tail CVaR: ${(metrics.cvar_99 / 1000).toFixed(1)}k
              </span>
            </div>
          </div>

          {/* Rating Tier Distribution */}
          <div>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: 12, marginBottom: 8 }}>
              <span style={{ fontWeight: 600, color: "#292524", display: "flex", alignItems: "center", gap: 6 }}>
                <BarChart3 size={13} style={{ color: "#C56A4A" }} />
                Portfolio Credit Rating Distribution
              </span>
              <span style={{ fontSize: 11, color: "#78716C" }}>
                Weighted Average PD: <strong>{(metrics.weighted_avg_pd * 100).toFixed(2)}%</strong>
              </span>
            </div>

            <div style={{ width: "100%", height: 10, borderRadius: 999, overflow: "hidden", display: "flex", backgroundColor: "#EFECE4" }}>
              <div style={{ width: `${(tiers["Super Prime"] / totalTierLoans) * 100}%`, backgroundColor: "#15803D" }} title="Super Prime" />
              <div style={{ width: `${(tiers["Prime"] / totalTierLoans) * 100}%`, backgroundColor: "#C56A4A" }} title="Prime" />
              <div style={{ width: `${(tiers["Near-Prime"] / totalTierLoans) * 100}%`, backgroundColor: "#B45309" }} title="Near-Prime" />
              <div style={{ width: `${(tiers["Subprime"] / totalTierLoans) * 100}%`, backgroundColor: "#D97706" }} title="Subprime" />
              <div style={{ width: `${(tiers["Deep Subprime"] / totalTierLoans) * 100}%`, backgroundColor: "#B91C1C" }} title="Deep Subprime" />
            </div>

            <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", gap: 8, marginTop: 10, fontSize: 11, color: "#78716C" }}>
              <span><span style={{ display: "inline-block", width: 8, height: 8, borderRadius: "50%", backgroundColor: "#15803D", marginRight: 4 }} /> Super Prime ({tiers["Super Prime"] || 0})</span>
              <span><span style={{ display: "inline-block", width: 8, height: 8, borderRadius: "50%", backgroundColor: "#C56A4A", marginRight: 4 }} /> Prime ({tiers["Prime"] || 0})</span>
              <span><span style={{ display: "inline-block", width: 8, height: 8, borderRadius: "50%", backgroundColor: "#B45309", marginRight: 4 }} /> Near-Prime ({tiers["Near-Prime"] || 0})</span>
              <span><span style={{ display: "inline-block", width: 8, height: 8, borderRadius: "50%", backgroundColor: "#D97706", marginRight: 4 }} /> Subprime ({tiers["Subprime"] || 0})</span>
              <span><span style={{ display: "inline-block", width: 8, height: 8, borderRadius: "50%", backgroundColor: "#B91C1C", marginRight: 4 }} /> Deep Subprime ({tiers["Deep Subprime"] || 0})</span>
            </div>
          </div>

          {/* Simulated Monte Carlo SVG Distribution Curve */}
          <div style={{ backgroundColor: "#FAF9F6", border: "1px solid #E7E2D9", borderRadius: 10, padding: 16 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: 11, marginBottom: 8 }}>
              <span style={{ fontWeight: 600, color: "#292524" }}>
                1,000-Scenario Simulated Loss Distribution Curve
              </span>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <span style={{ color: "#C56A4A" }}>■ Expected Loss</span>
                <span style={{ color: "#B45309" }}>■ 95% VaR</span>
                <span style={{ color: "#B91C1C" }}>■ 99% Tail VaR</span>
              </div>
            </div>

            <div style={{ width: "100%", height: 110, position: "relative" }}>
              <svg viewBox="0 0 600 110" preserveAspectRatio="none" style={{ width: "100%", height: "100%" }}>
                {/* Shaded Tail Area */}
                <path d="M 450,100 L 450,40 Q 520,70 580,95 L 580,100 Z" fill="rgba(185, 28, 28, 0.12)" />
                {/* Distribution curve */}
                <path d="M 20,100 Q 120,98 180,68 Q 240,16 280,16 Q 320,16 380,45 Q 460,78 580,100" fill="none" stroke="#C56A4A" strokeWidth="2.5" />
                {stressResult && (
                  <path d="M 20,100 Q 140,100 220,85 Q 300,38 360,20 Q 420,20 480,48 Q 540,78 590,100" fill="none" stroke="#DC2626" strokeWidth="2" strokeDasharray="4 3" />
                )}
                <line x1="280" y1="12" x2="280" y2="100" stroke="#C56A4A" strokeWidth="1.5" strokeDasharray="3 3" />
                <line x1="450" y1="36" x2="450" y2="100" stroke="#B45309" strokeWidth="1.5" strokeDasharray="3 3" />
                <line x1="530" y1="70" x2="530" y2="100" stroke="#B91C1C" strokeWidth="2" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Macro Stress Test Simulator */}
      <div className="card">
        <div className="card-header">
          <div>
            <span className="card-title">
              <Activity size={15} style={{ color: "#C56A4A" }} />
              Macroeconomic Stress Simulator (CCAR / EBA)
            </span>
            <span className="card-subtitle">
              Simulate systemic shocks to loan balances, payment delays, and recovery rates
            </span>
          </div>

          <button
            type="button"
            onClick={handleRunStressTest}
            disabled={isStressTesting}
            className="btn btn-primary btn-sm"
          >
            <Play size={11} />
            <span>{isStressTesting ? "Simulating..." : "Run Macro Shock"}</span>
          </button>
        </div>

        <div className="card-body" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Preset Stress Scenarios */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 10 }}>
            {presets.map((sc) => {
              const Icon = sc.icon;
              const isSelected = activeScenario === sc.id;
              return (
                <div
                  key={sc.id}
                  onClick={() => {
                    setActiveScenario(sc.id);
                    runScenarioWithParams(sc.name, sc.shift, sc.shock, sc.pd, sc.lgd);
                  }}
                  className={`preset-card ${isSelected ? "selected" : ""}`}
                  style={{ padding: 12 }}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <span style={{ fontSize: 12, fontWeight: 700, color: sc.color }}>{sc.name}</span>
                    <Icon size={14} style={{ color: sc.color }} />
                  </div>
                  <span style={{ fontSize: 10, color: "#78716C", marginTop: 4 }}>{sc.desc}</span>
                </div>
              );
            })}
          </div>

          {/* 4 Stress Sliders */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12 }}>
            <div className="form-group">
              <div className="form-label">
                <span>Delay Shift</span>
                <span style={{ fontFamily: "var(--font-mono)", color: "#C56A4A" }}>+{delayShift} mo</span>
              </div>
              <input
                type="range"
                min="0"
                max="3"
                step="1"
                value={delayShift}
                onChange={(e) => {
                  setActiveScenario("custom");
                  setDelayShift(parseInt(e.target.value));
                }}
              />
            </div>

            <div className="form-group">
              <div className="form-label">
                <span>Balance Draw Shock</span>
                <span style={{ fontFamily: "var(--font-mono)", color: "#C56A4A" }}>+{balanceShock}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="30"
                step="5"
                value={balanceShock}
                onChange={(e) => {
                  setActiveScenario("custom");
                  setBalanceShock(parseInt(e.target.value));
                }}
              />
            </div>

            <div className="form-group">
              <div className="form-label">
                <span>PD Multiplier</span>
                <span style={{ fontFamily: "var(--font-mono)", color: "#C56A4A" }}>{pdMult.toFixed(2)}x</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="2.5"
                step="0.05"
                value={pdMult}
                onChange={(e) => {
                  setActiveScenario("custom");
                  setPdMult(parseFloat(e.target.value));
                }}
              />
            </div>

            <div className="form-group">
              <div className="form-label">
                <span>Stressed LGD</span>
                <span style={{ fontFamily: "var(--font-mono)", color: "#C56A4A" }}>{(stressedLgd * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0.45"
                max="0.75"
                step="0.05"
                value={stressedLgd}
                onChange={(e) => {
                  setActiveScenario("custom");
                  setStressedLgd(parseFloat(e.target.value));
                }}
              />
            </div>
          </div>

          {/* Stressed Outcome Delta Box */}
          {stressResult && (
            <div
              style={{
                padding: 16,
                borderRadius: 10,
                backgroundColor: "#FFFBEB",
                border: "1px solid #FDE68A",
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                gap: 12,
              }}
            >
              <div>
                <span style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", color: "#78716C" }}>
                  Stressed Expected Loss
                </span>
                <p style={{ fontFamily: "var(--font-mono)", fontSize: 16, fontWeight: 700, color: "#B45309", marginTop: 2 }}>
                  ${(stressResult.stressed.expected_loss / 1000).toFixed(1)}k
                </p>
                <span style={{ fontSize: 10, color: "#B45309", fontWeight: 600 }}>
                  +{stressResult.impact.pct_increase_expected_loss}% vs baseline
                </span>
              </div>

              <div>
                <span style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", color: "#78716C" }}>
                  Capital Buffer Drain (Δ EL)
                </span>
                <p style={{ fontFamily: "var(--font-mono)", fontSize: 16, fontWeight: 700, color: "#292524", marginTop: 2 }}>
                  +${(stressResult.impact.delta_expected_loss / 1000).toFixed(1)}k
                </p>
                <span style={{ fontSize: 10, color: "#78716C" }}>Required Loss Provision</span>
              </div>

              <div>
                <span style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", color: "#78716C" }}>
                  Stressed VaR 99% Tail
                </span>
                <p style={{ fontFamily: "var(--font-mono)", fontSize: 16, fontWeight: 700, color: "#B91C1C", marginTop: 2 }}>
                  ${(stressResult.stressed.var_99 / 1000).toFixed(1)}k
                </p>
                <span style={{ fontSize: 10, color: "#B91C1C", fontWeight: 600 }}>
                  +${(stressResult.impact.delta_var_99 / 1000).toFixed(1)}k Drain
                </span>
              </div>

              <div>
                <span style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", color: "#78716C" }}>
                  Institutional Status
                </span>
                <p style={{ fontSize: 13, fontWeight: 700, color: "#292524", marginTop: 2 }}>
                  {stressResult.impact.capital_strain_status}
                </p>
                <span style={{ fontSize: 10, color: "#78716C" }}>Tier 1 Capital Reserves</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
