/**
 * Type-safe API Client for CredSure AI FastAPI Backend Services
 * Automatically detects active CredSure API on port 8000 or 8001
 */

const DEFAULT_API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8001";
let activeBaseUrl = DEFAULT_API_URL;

async function getBaseUrl(): Promise<string> {
  // If explicitly overridden via env
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  // Probe port 8001 first (where the full v1.0 Underwriter Service runs)
  for (const url of ["http://127.0.0.1:8001", "http://127.0.0.1:8000"]) {
    try {
      const res = await fetch(`${url}/health`, { signal: AbortSignal.timeout(1500) });
      if (res.ok) {
        const data = await res.json();
        // Specifically check for v1.0 Underwriter Service with memo support
        if (data.service?.includes("Underwriter") || data.version === "1.0.0") {
          activeBaseUrl = url;
          return activeBaseUrl;
        }
      }
    } catch (e) {
      // try next port
    }
  }

  return activeBaseUrl;
}

export interface BorrowerFeatures {
  LIMIT_BAL: number;
  SEX: number;
  EDUCATION: number;
  MARRIAGE: number;
  AGE: number;
  PAY_0: number;
  PAY_2: number;
  PAY_3: number;
  PAY_4: number;
  PAY_5: number;
  PAY_6: number;
  BILL_AMT1: number;
  BILL_AMT2: number;
  BILL_AMT3: number;
  BILL_AMT4: number;
  BILL_AMT5: number;
  BILL_AMT6: number;
  PAY_AMT1: number;
  PAY_AMT2: number;
  PAY_AMT3: number;
  PAY_AMT4: number;
  PAY_AMT5: number;
  PAY_AMT6: number;
}

export interface DriverFactor {
  feature: string;
  points: number;
  label: string;
  description: string;
}

export interface AdverseReason {
  code: string;
  title: string;
  detail: string;
}

export interface ScorecardResponse {
  score: number;
  pd: number;
  pd_percentage: number;
  risk_category: string;
  risk_color: string;
  utilization: number;
  top_positive_drivers: DriverFactor[];
  top_negative_drivers: DriverFactor[];
  adverse_action_reasons: AdverseReason[];
  feature_breakdown: Record<string, any>;
}

export interface PresetBorrower {
  id: string;
  name: string;
  tagline: string;
  features: BorrowerFeatures;
}

export interface PortfolioMetricsResponse {
  total_records: number;
  total_limit: number;
  total_ead: number;
  total_expected_loss: number;
  portfolio_el_rate_bps: number;
  weighted_avg_pd: number;
  portfolio_lgd: number;
  var_95: number;
  var_99: number;
  cvar_95: number;
  cvar_99: number;
  unexpected_loss_95: number;
  unexpected_loss_99: number;
  risk_tier_counts: Record<string, number>;
  loss_histogram: Array<{
    bin_start: number;
    bin_end: number;
    midpoint: number;
    count: number;
  }>;
}

export interface StressTestRequest {
  scenario_name: string;
  delay_shift: number;
  balance_shock_pct: number;
  pd_multiplier: number;
  stressed_lgd: number;
}

export interface StressTestResponse {
  scenario_name: string;
  parameters: Record<string, any>;
  baseline: {
    total_ead: number;
    expected_loss: number;
    el_rate_bps: number;
    weighted_avg_pd: number;
    var_95: number;
    var_99: number;
    cvar_95: number;
    cvar_99: number;
  };
  stressed: {
    total_ead: number;
    expected_loss: number;
    el_rate_bps: number;
    weighted_avg_pd: number;
    var_95: number;
    var_99: number;
    cvar_95: number;
    cvar_99: number;
  };
  impact: {
    delta_expected_loss: number;
    pct_increase_expected_loss: number;
    delta_var_95: number;
    delta_var_99: number;
    capital_strain_status: string;
  };
  loss_distributions: {
    baseline_histogram: any[];
    stressed_histogram: any[];
  };
}

export interface MemoResponse {
  decision: "APPROVED" | "CONDITIONAL" | "DECLINED";
  decision_badge_color: string;
  scorecard: Record<string, any>;
  basel_el: Record<string, any>;
  policy_citations: Array<{
    chunk_id: string;
    section_title: string;
    rule_category: string;
    text: string;
    score: number;
  }>;
  memo_markdown: string;
  memo_package: Record<string, any>;
  underwriter_name: string;
  compliance_attestation: string;
}

export const api = {
  async getHealth() {
    const base = await getBaseUrl();
    const res = await fetch(`${base}/health`);
    if (!res.ok) throw new Error("Health check failed");
    return res.json();
  },

  async scoreBorrower(features: BorrowerFeatures): Promise<ScorecardResponse> {
    const base = await getBaseUrl();
    const res = await fetch(`${base}/scorecard/score`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(features),
    });
    if (!res.ok) throw new Error("Scoring evaluation failed");
    return res.json();
  },

  async getPresets(): Promise<{ presets: PresetBorrower[] }> {
    const base = await getBaseUrl();
    const res = await fetch(`${base}/scorecard/presets`);
    if (!res.ok) throw new Error("Failed to load presets");
    return res.json();
  },

  async getPortfolioMetrics(): Promise<PortfolioMetricsResponse> {
    const base = await getBaseUrl();
    const res = await fetch(`${base}/portfolio/metrics`);
    if (!res.ok) throw new Error("Failed to fetch portfolio risk metrics");
    return res.json();
  },

  async runStressTest(params: StressTestRequest): Promise<StressTestResponse> {
    const base = await getBaseUrl();
    const res = await fetch(`${base}/portfolio/stress-test`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    if (!res.ok) throw new Error("Stress testing simulation failed");
    return res.json();
  },

  async generateMemo(features: BorrowerFeatures, applicantName?: string): Promise<MemoResponse> {
    const base = await getBaseUrl();
    const res = await fetch(`${base}/analyst/memo`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        applicant_name: applicantName || "Credit Facility Application #9410",
        features,
      }),
    });
    if (!res.ok) throw new Error("Underwriting memorandum generation failed");
    return res.json();
  },
};
