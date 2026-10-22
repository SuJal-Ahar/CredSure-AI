"use client";

import React, { useEffect, useState } from "react";
import { Gauge, ShieldCheck, AlertTriangle, TrendingDown } from "lucide-react";

interface ScoreGaugeProps {
  score: number;
  pd: number;
  category: string;
  color?: string;
  utilization: number;
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({
  score = 650,
  pd = 0.05,
  category = "Prime",
  color = "#C56A4A",
  utilization = 25.0,
}) => {
  // Smooth count-up ticker for numeric score
  const [displayScore, setDisplayScore] = useState(score);

  useEffect(() => {
    let frameId: number;
    const startScore = displayScore;
    const endScore = score;
    const duration = 400; // ms
    const startTime = performance.now();

    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // easeOutQuad
      const eased = 1 - (1 - progress) * (1 - progress);
      const current = Math.round(startScore + (endScore - startScore) * eased);
      setDisplayScore(current);

      if (progress < 1) {
        frameId = requestAnimationFrame(animate);
      }
    };

    frameId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frameId);
  }, [score]);

  // Semicircle arc calculations
  // Score range: 300 to 850 (span = 550)
  const clampedScore = Math.max(300, Math.min(850, score));
  const scoreRatio = (clampedScore - 300) / 550;

  // Semicircle arc: cx=100, cy=95, r=72
  // Total arc length = PI * 72 = 226.19
  const arcRadius = 72;
  const arcLength = Math.PI * arcRadius;
  const strokeOffset = arcLength * (1 - scoreRatio);

  // Semantic category color mapping
  const getSemanticColor = () => {
    if (score >= 700) return { main: "#15803D", bg: "#F0FDF4", border: "#BBF7D0", badge: "badge-success" };
    if (score >= 640) return { main: "#C56A4A", bg: "#FBF0EB", border: "#F0C4B4", badge: "badge-accent" };
    if (score >= 580) return { main: "#B45309", bg: "#FFFBEB", border: "#FDE68A", badge: "badge-warning" };
    return { main: "#B91C1C", bg: "#FEF2F2", border: "#FECACA", badge: "badge-error" };
  };

  const sem = getSemanticColor();

  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">
          <Gauge size={15} style={{ color: "#C56A4A" }} />
          Credit Risk Scorecard
        </span>
        <span className={`badge ${sem.badge}`}>
          {category}
        </span>
      </div>

      <div className="card-body risk-gauge-card">
        {/* Compact Semicircular SVG Gauge */}
        <div className="gauge-svg-wrapper">
          <svg
            viewBox="0 0 200 115"
            style={{ width: "100%", height: "100%", overflow: "visible" }}
          >
            <defs>
              {/* Soft gradient along arc */}
              <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#B91C1C" />
                <stop offset="45%" stopColor="#B45309" />
                <stop offset="75%" stopColor="#C56A4A" />
                <stop offset="100%" stopColor="#15803D" />
              </linearGradient>
            </defs>

            {/* Background Track (Muted Neutral) */}
            <path
              d="M 28 95 A 72 72 0 0 1 172 95"
              fill="none"
              stroke="#EFECE4"
              strokeWidth="9"
              strokeLinecap="round"
            />

            {/* Active Colored Progress Arc */}
            <path
              d="M 28 95 A 72 72 0 0 1 172 95"
              fill="none"
              stroke={sem.main}
              strokeWidth="9"
              strokeLinecap="round"
              strokeDasharray={arcLength}
              strokeDashoffset={strokeOffset}
              style={{
                transition: "stroke-dashoffset 0.4s ease, stroke 0.3s ease",
              }}
            />

            {/* Range End Labels: 300 and 850 */}
            <text x="24" y="112" fill="#A8A29E" fontSize="9" fontWeight="600" textAnchor="middle" fontFamily="var(--font-mono)">
              300
            </text>
            <text x="176" y="112" fill="#A8A29E" fontSize="9" fontWeight="600" textAnchor="middle" fontFamily="var(--font-mono)">
              850
            </text>
          </svg>

          {/* Centered Numeric Score Counter */}
          <div
            style={{
              position: "absolute",
              bottom: 4,
              left: 0,
              right: 0,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <span className="score-display-number" style={{ color: sem.main }}>
              {displayScore}
            </span>
            <span style={{ fontSize: 10, fontWeight: 600, color: "#78716C", marginTop: 2 }}>
              FICO-EQUIVALENT POINTS
            </span>
          </div>
        </div>

        {/* Supporting Risk Metrics Row */}
        <div className="score-metric-row">
          <div className="metric-box">
            <span className="metric-box-title">Default Probability</span>
            <p className="metric-box-value" style={{ color: sem.main }}>
              {(pd * 100).toFixed(2)}%
            </p>
            <span style={{ fontSize: 10, color: "#78716C" }}>
              {pd < 0.03 ? "Standard grade" : pd < 0.08 ? "Elevated risk" : "High impairment"}
            </span>
          </div>

          <div className="metric-box">
            <span className="metric-box-title">Credit Utilization</span>
            <p className="metric-box-value">
              {utilization.toFixed(1)}%
            </p>
            <span style={{ fontSize: 10, color: utilization < 30 ? "#15803D" : utilization < 60 ? "#B45309" : "#B91C1C" }}>
              {utilization < 30 ? "Optimal tier" : utilization < 60 ? "Moderate draw" : "High leverage"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
