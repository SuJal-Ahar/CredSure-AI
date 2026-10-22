"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  api,
  BorrowerFeatures,
  ScorecardResponse,
  PresetBorrower,
  PortfolioMetricsResponse,
  MemoResponse,
} from "@/services/api";
import { AppSidebar } from "@/components/AppSidebar";
import { AppHeader } from "@/components/AppHeader";
import { ScoreGauge } from "@/components/ScoreGauge";
import { BorrowerForm } from "@/components/BorrowerForm";
import { PortfolioCard } from "@/components/PortfolioCard";
import { UnderwriterMemo } from "@/components/UnderwriterMemo";

const DEFAULT_BORROWER: BorrowerFeatures = {
  LIMIT_BAL: 80000.0,
  SEX: 2,
  EDUCATION: 2,
  MARRIAGE: 1,
  AGE: 38,
  PAY_0: 0,
  PAY_2: 0,
  PAY_3: 0,
  PAY_4: 0,
  PAY_5: 0,
  PAY_6: 0,
  BILL_AMT1: 18000.0,
  BILL_AMT2: 17200.0,
  BILL_AMT3: 16500.0,
  BILL_AMT4: 15000.0,
  BILL_AMT5: 14000.0,
  BILL_AMT6: 13000.0,
  PAY_AMT1: 8000.0,
  PAY_AMT2: 7500.0,
  PAY_AMT3: 7000.0,
  PAY_AMT4: 6500.0,
  PAY_AMT5: 6000.0,
  PAY_AMT6: 5500.0,
};

export default function Dashboard() {
  const [activeView, setActiveView] = useState<"application" | "portfolio">("application");
  const [features, setFeatures] = useState<BorrowerFeatures>(DEFAULT_BORROWER);
  const [scorecard, setScorecard] = useState<ScorecardResponse | null>(null);
  const [presets, setPresets] = useState<PresetBorrower[]>([]);
  const [portfolioMetrics, setPortfolioMetrics] = useState<PortfolioMetricsResponse | null>(null);
  const [memo, setMemo] = useState<MemoResponse | null>(null);

  const [isEvaluating, setIsEvaluating] = useState(false);
  const [isGeneratingMemo, setIsGeneratingMemo] = useState(false);
  const [isLoadingMetrics, setIsLoadingMetrics] = useState(false);
  const [systemOnline, setSystemOnline] = useState(true);

  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const initData = async () => {
      try {
        const [presetData, health] = await Promise.allSettled([
          api.getPresets(),
          api.getHealth(),
        ]);

        if (presetData.status === "fulfilled") {
          setPresets(presetData.value.presets);
        }
        if (health.status === "fulfilled") {
          setSystemOnline(true);
        }
      } catch (e) {
        console.warn("Initialization note:", e);
      }

      handleEvaluate(DEFAULT_BORROWER);
      loadPortfolioMetrics();
    };

    initData();
  }, []);

  const handleEvaluate = async (featToScore?: BorrowerFeatures) => {
    setIsEvaluating(true);
    try {
      const res = await api.scoreBorrower(featToScore || features);
      setScorecard(res);
      setSystemOnline(true);
    } catch (e) {
      console.error("Scorecard evaluation error:", e);
    } finally {
      setIsEvaluating(false);
    }
  };

  const handleFormChange = (newFeats: BorrowerFeatures) => {
    setFeatures(newFeats);

    // Debounce live evaluation so slider interaction is silky smooth
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    debounceTimerRef.current = setTimeout(() => {
      handleEvaluate(newFeats);
    }, 120);
  };

  const handleReset = () => {
    setFeatures(DEFAULT_BORROWER);
    setMemo(null);
    handleEvaluate(DEFAULT_BORROWER);
  };

  const loadPortfolioMetrics = async () => {
    setIsLoadingMetrics(true);
    try {
      const metrics = await api.getPortfolioMetrics();
      setPortfolioMetrics(metrics);
    } catch (e) {
      console.error("Portfolio metrics load error:", e);
    } finally {
      setIsLoadingMetrics(false);
    }
  };

  const handleGenerateMemo = async () => {
    setIsGeneratingMemo(true);
    try {
      const memoRes = await api.generateMemo(features);
      setMemo(memoRes);
    } catch (e) {
      console.error("Memo generation error:", e);
    } finally {
      setIsGeneratingMemo(false);
    }
  };

  return (
    <div className="app-shell">
      {/* 1. Left Application Sidebar */}
      <AppSidebar
        activeView={activeView}
        onViewChange={setActiveView}
        systemOnline={systemOnline}
      />

      {/* 2. Main Application Workspace Area */}
      <div className="app-main">
        {/* Top Header */}
        <AppHeader
          activeView={activeView}
          onViewChange={setActiveView}
          onReset={handleReset}
          applicantId="#CFS-9410"
        />

        {/* Content Container */}
        <main className="app-content">
          {activeView === "application" ? (
            /* Two-Column Underwriting Workspace */
            <div className="workspace-grid">
              {/* Left Main Workspace (~68% width) */}
              <div className="workspace-main">
                <BorrowerForm
                  features={features}
                  onChange={handleFormChange}
                  onEvaluate={() => handleEvaluate(features)}
                  onGenerateMemo={handleGenerateMemo}
                  presets={presets}
                  isEvaluating={isEvaluating}
                  isGeneratingMemo={isGeneratingMemo}
                />
              </div>

              {/* Right Summary Panel (~32% width) */}
              <div className="workspace-aside">
                {/* Compact Risk Scorecard Gauge */}
                <ScoreGauge
                  score={scorecard?.score || 650}
                  pd={scorecard?.pd || 0.05}
                  category={scorecard?.risk_category || "Prime"}
                  color={scorecard?.risk_color || "#C56A4A"}
                  utilization={scorecard?.utilization || 25.0}
                />

                {/* Structured Decision Summary Panel */}
                <UnderwriterMemo memo={memo} isLoading={isGeneratingMemo} />
              </div>
            </div>
          ) : (
            /* Institutional Portfolio Risk View */
            <PortfolioCard
              metrics={portfolioMetrics}
              onRefreshMetrics={loadPortfolioMetrics}
              isLoading={isLoadingMetrics}
            />
          )}

          {/* Institutional Compliance Footer */}
          <footer
            style={{
              marginTop: 40,
              paddingTop: 16,
              borderTop: "1px solid var(--border-color)",
              display: "flex",
              flexWrap: "wrap",
              alignItems: "center",
              justifyContent: "space-between",
              gap: 12,
              fontSize: 11,
              color: "var(--text-secondary)",
            }}
          >
            <span>
              CredSure AI • Commercial Credit Underwriting OS • Pure Statistical Scorecard
            </span>
            <span style={{ color: "var(--text-muted)" }}>
              Equal Credit Opportunity Act (ECOA) & FCRA § 615 Adverse Disclosure Compliant
            </span>
          </footer>
        </main>
      </div>
    </div>
  );
}
