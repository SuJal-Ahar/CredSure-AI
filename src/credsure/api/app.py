"""CredSure AI - Regulatory-compliant Credit Risk Scorecard & AI Underwriter API.

FastAPI web service serving scoring models, portfolio Monte Carlo analytics,
embedded Qdrant policy search, and autonomous AI underwriting agents.
"""

import os
from contextlib import asynccontextmanager
from typing import Dict, List, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from credsure.api.schemas import (
    BorrowerFeatures,
    ScorecardResponse,
    StressTestRequest,
    StressTestResponse,
    PortfolioMetricsResponse,
    MemoRequest,
    MemoResponse,
    HealthResponse,
)
from credsure.scorecard.calculator import ScorecardCalculator
from credsure.portfolio.expected_loss import BaselExpectedLossEngine
from credsure.portfolio.monte_carlo_var import MonteCarloRiskEngine
from credsure.portfolio.stress_testing import MacroStressTester
from credsure.rag.vector_store import QdrantPolicyVectorStore
from credsure.rag.policy_loader import PolicyDocumentLoader
from credsure.analyst.agent import CreditUnderwriterAgent
from credsure.analyst.memo_generator import CreditMemoGenerator

# Global application state
state: Dict[str, Any] = {}


def generate_baseline_portfolio(n_records: int = 1000) -> List[Dict[str, Any]]:
    """Generate high-fidelity baseline portfolio records for real-time risk analytics."""
    import numpy as np
    rng = np.random.default_rng(42)

    records = []
    calculator = ScorecardCalculator()

    limits = np.round(np.clip(rng.lognormal(11.4, 0.75, n_records), 15000, 500000) / 5000) * 5000
    ages = np.clip(rng.normal(36, 10, n_records).astype(int), 21, 72)
    pay0_choices = [-1, 0, 1, 2, 3]
    pay0_probs = [0.45, 0.35, 0.12, 0.06, 0.02]
    pay0s = rng.choice(pay0_choices, size=n_records, p=pay0_probs)

    for i in range(n_records):
        limit = float(limits[i])
        pay0 = int(pay0s[i])
        util = float(np.clip(rng.beta(2, 5) * (1.3 if pay0 > 0 else 0.8), 0.05, 0.95))
        bill1 = float(np.round(limit * util))
        pay1 = float(np.round(bill1 * (0.1 if pay0 > 0 else rng.uniform(0.5, 1.0))))

        feat = {
            "ID": i + 1,
            "LIMIT_BAL": limit,
            "SEX": int(rng.choice([1, 2])),
            "EDUCATION": int(rng.choice([1, 2, 3])),
            "MARRIAGE": int(rng.choice([1, 2])),
            "AGE": int(ages[i]),
            "PAY_0": pay0,
            "PAY_2": max(-1, pay0 - int(rng.choice([0, 1]))),
            "PAY_3": max(-1, pay0 - int(rng.choice([0, 1]))),
            "PAY_4": 0,
            "PAY_5": 0,
            "PAY_6": 0,
            "BILL_AMT1": bill1,
            "BILL_AMT2": bill1 * 0.95,
            "BILL_AMT3": bill1 * 0.90,
            "PAY_AMT1": pay1,
            "PAY_AMT2": pay1 * 0.95,
            "PAY_AMT3": pay1 * 0.90,
        }

        # Evaluate score and PD
        eval_res = calculator.evaluate(feat)
        feat["score"] = eval_res["score"]
        feat["pd"] = eval_res["pd"]
        feat["risk_category"] = eval_res["risk_category"]

        records.append(feat)

    return records


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize statistical risk cores, local Qdrant, and portfolio data."""
    print("Initializing CredSure AI backend services...")

    # 1. Scorecard Calculator
    calculator = ScorecardCalculator()
    state["calculator"] = calculator

    # 2. Portfolio Risk & Stress Engines
    el_engine = BaselExpectedLossEngine(default_lgd=0.45, default_ccf=0.20)
    mc_engine = MonteCarloRiskEngine(n_simulations=1000, asset_correlation=0.15, default_lgd=0.45, seed=42)
    stress_tester = MacroStressTester(el_engine=el_engine, mc_engine=mc_engine)

    state["el_engine"] = el_engine
    state["mc_engine"] = mc_engine
    state["stress_tester"] = stress_tester

    # 3. Embedded Local Qdrant Vector Store
    vector_store = QdrantPolicyVectorStore(storage_path="./data/qdrant_storage")
    policy_loader = PolicyDocumentLoader(policy_dir="./data/policies")
    chunks = policy_loader.load_all_chunks()
    indexed_count = vector_store.index_policies(chunks)
    print(f"Indexed {indexed_count} policy rule chunks into embedded Qdrant.")

    state["vector_store"] = vector_store
    state["policy_loader"] = policy_loader
    state["indexed_policy_count"] = indexed_count

    # 4. AI Underwriter Agent
    agent = CreditUnderwriterAgent(
        calculator=calculator,
        vector_store=vector_store,
        el_engine=el_engine,
    )
    state["agent"] = agent

    # 5. Baseline Portfolio Data
    portfolio_records = generate_baseline_portfolio(1000)
    state["portfolio_records"] = portfolio_records
    print(f"Generated {len(portfolio_records)} baseline institutional portfolio records.")

    yield

    print("Shutting down CredSure AI backend.")


app = FastAPI(
    title="CredSure AI - Credit Risk Scorecard & Underwriter API",
    description="Regulatory-compliant credit scoring, Basel expected loss, Monte Carlo VaR, and AI loan memo generation.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check and embedded storage status."""
    return HealthResponse(
        status="healthy",
        service="CredSure AI Risk & Underwriter Service",
        version="1.0.0",
        qdrant_status="connected (embedded disk mode ./data/qdrant_storage)",
        qdrant_collection=QdrantPolicyVectorStore.COLLECTION_NAME,
        embedding_model="BAAI/bge-small-en-v1.5 (CPU via FastEmbed)",
        policies_indexed=state.get("indexed_policy_count", 7),
        portfolio_records_loaded=len(state.get("portfolio_records", [])),
    )


@app.post("/scorecard/score", response_model=ScorecardResponse)
def score_borrower(borrower: BorrowerFeatures):
    """Evaluate borrower 23 features and return transparent FICO score (300-850), PD, and score drivers."""
    calculator: ScorecardCalculator = state["calculator"]
    features_dict = borrower.model_dump()
    result = calculator.evaluate(features_dict)
    return ScorecardResponse(**result)


@app.get("/scorecard/presets")
def get_borrower_presets():
    """Retrieve 1-click test borrower presets for the UI."""
    return {
        "presets": [
            {
                "id": "prime",
                "name": "Prime Borrower",
                "tagline": "FICO ~760 | Zero Delinquencies | Low Utilization",
                "features": {
                    "LIMIT_BAL": 120000.0,
                    "SEX": 2,
                    "EDUCATION": 1,
                    "MARRIAGE": 1,
                    "AGE": 42,
                    "PAY_0": 0,
                    "PAY_2": 0,
                    "PAY_3": 0,
                    "PAY_4": 0,
                    "PAY_5": 0,
                    "PAY_6": 0,
                    "BILL_AMT1": 15000.0,
                    "BILL_AMT2": 14200.0,
                    "BILL_AMT3": 13500.0,
                    "BILL_AMT4": 12000.0,
                    "BILL_AMT5": 11000.0,
                    "BILL_AMT6": 10000.0,
                    "PAY_AMT1": 14200.0,
                    "PAY_AMT2": 13500.0,
                    "PAY_AMT3": 12000.0,
                    "PAY_AMT4": 11000.0,
                    "PAY_AMT5": 10000.0,
                    "PAY_AMT6": 9500.0,
                },
            },
            {
                "id": "delinquent",
                "name": "Overextended Delinquent",
                "tagline": "FICO ~540 | 60-Day Late Payment | 95% Utilization",
                "features": {
                    "LIMIT_BAL": 20000.0,
                    "SEX": 1,
                    "EDUCATION": 3,
                    "MARRIAGE": 2,
                    "AGE": 29,
                    "PAY_0": 2,
                    "PAY_2": 2,
                    "PAY_3": 1,
                    "PAY_4": 0,
                    "PAY_5": 0,
                    "PAY_6": 0,
                    "BILL_AMT1": 19200.0,
                    "BILL_AMT2": 18900.0,
                    "BILL_AMT3": 18100.0,
                    "BILL_AMT4": 17200.0,
                    "BILL_AMT5": 16500.0,
                    "BILL_AMT6": 15000.0,
                    "PAY_AMT1": 500.0,
                    "PAY_AMT2": 400.0,
                    "PAY_AMT3": 400.0,
                    "PAY_AMT4": 500.0,
                    "PAY_AMT5": 500.0,
                    "PAY_AMT6": 500.0,
                },
            },
            {
                "id": "graduate",
                "name": "Recent Graduate",
                "tagline": "FICO ~655 | Entry Credit Line | 35% Utilization",
                "features": {
                    "LIMIT_BAL": 35000.0,
                    "SEX": 2,
                    "EDUCATION": 1,
                    "MARRIAGE": 2,
                    "AGE": 24,
                    "PAY_0": 0,
                    "PAY_2": 0,
                    "PAY_3": 0,
                    "PAY_4": 0,
                    "PAY_5": 0,
                    "PAY_6": 0,
                    "BILL_AMT1": 11500.0,
                    "BILL_AMT2": 10200.0,
                    "BILL_AMT3": 9500.0,
                    "BILL_AMT4": 8200.0,
                    "BILL_AMT5": 7000.0,
                    "BILL_AMT6": 6500.0,
                    "PAY_AMT1": 3500.0,
                    "PAY_AMT2": 3000.0,
                    "PAY_AMT3": 2500.0,
                    "PAY_AMT4": 2000.0,
                    "PAY_AMT5": 1800.0,
                    "PAY_AMT6": 1500.0,
                },
            },
        ]
    }


@app.get("/portfolio/metrics", response_model=PortfolioMetricsResponse)
def get_portfolio_metrics():
    """Compute aggregate portfolio Expected Loss, 1,000-run Monte Carlo VaR 95/99, and risk tier counts."""
    el_engine: BaselExpectedLossEngine = state["el_engine"]
    mc_engine: MonteCarloRiskEngine = state["mc_engine"]
    records: List[Dict[str, Any]] = state.get("portfolio_records", [])

    el_stats = el_engine.calculate_portfolio(records)
    mc_stats = mc_engine.simulate(records)

    # Risk tier distribution
    tier_counts = {"Super Prime": 0, "Prime": 0, "Near-Prime": 0, "Subprime": 0, "Deep Subprime": 0}
    for r in records:
        cat = r.get("risk_category", "Near-Prime")
        if cat in tier_counts:
            tier_counts[cat] += 1
        else:
            tier_counts["Near-Prime"] += 1

    return PortfolioMetricsResponse(
        total_records=el_stats["total_records"],
        total_limit=el_stats["total_limit"],
        total_ead=el_stats["total_ead"],
        total_expected_loss=el_stats["total_expected_loss"],
        portfolio_el_rate_bps=el_stats["portfolio_el_rate_bps"],
        weighted_avg_pd=el_stats["weighted_avg_pd"],
        portfolio_lgd=el_stats["portfolio_lgd"],
        var_95=mc_stats["var_95"],
        var_99=mc_stats["var_99"],
        cvar_95=mc_stats["cvar_95"],
        cvar_99=mc_stats["cvar_99"],
        unexpected_loss_95=mc_stats["unexpected_loss_95"],
        unexpected_loss_99=mc_stats["unexpected_loss_99"],
        risk_tier_counts=tier_counts,
        loss_histogram=mc_stats.get("histogram", []),
    )


@app.post("/portfolio/stress-test", response_model=StressTestResponse)
def run_stress_test(req: StressTestRequest):
    """Execute macroeconomic perturbation stress simulation."""
    stress_tester: MacroStressTester = state["stress_tester"]
    records = state.get("portfolio_records", [])

    result = stress_tester.apply_scenario(
        portfolio_records=records,
        scenario_name=req.scenario_name,
        delay_shift=req.delay_shift,
        balance_shock_pct=req.balance_shock_pct,
        pd_multiplier=req.pd_multiplier,
        stressed_lgd=req.stressed_lgd,
        run_monte_carlo=True,
    )

    return StressTestResponse(**result)


@app.post("/analyst/memo", response_model=MemoResponse)
def generate_underwriting_memo(req: MemoRequest):
    """Generate official institutional AI Credit Underwriting Memorandum."""
    agent: CreditUnderwriterAgent = state["agent"]
    features_dict = req.features.model_dump()

    memo_result = agent.evaluate_and_generate_memo(features_dict)
    package = CreditMemoGenerator.format_memo(
        borrower_features=features_dict,
        scorecard_result=memo_result["scorecard"],
        basel_el=memo_result["basel_el"],
        policy_citations=memo_result["policy_citations"],
        ai_memo_text=memo_result["memo_markdown"],
        applicant_name=req.applicant_name or "Applicant #78421",
    )

    return MemoResponse(
        decision=memo_result["decision"],
        decision_badge_color=memo_result["decision_badge_color"],
        scorecard=memo_result["scorecard"],
        basel_el=memo_result["basel_el"],
        policy_citations=memo_result["policy_citations"],
        memo_markdown=memo_result["memo_markdown"],
        memo_package=package,
        underwriter_name=memo_result["underwriter_name"],
        compliance_attestation=memo_result["compliance_attestation"],
    )


@app.get("/policies/rules")
def get_policy_rules(query: str = "underwriting approval", category: str = None):
    """Search Qdrant embedded policy knowledge base."""
    vector_store: QdrantPolicyVectorStore = state["vector_store"]
    results = vector_store.search(query=query, limit=5, rule_category=category)
    return {"query": query, "results": results}
