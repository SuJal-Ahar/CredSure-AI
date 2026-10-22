"""Strict Pydantic v2 schemas for CredSure AI FastAPI service."""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class BorrowerFeatures(BaseModel):
    """23-feature borrower attribute schema compliant with UCI Credit Card specifications."""

    LIMIT_BAL: float = Field(default=50000.0, description="Authorized credit facility limit ($)", ge=1000.0)
    SEX: int = Field(default=2, description="Gender (1 = Male, 2 = Female)")
    EDUCATION: int = Field(default=2, description="Education (1=Graduate, 2=University, 3=High School, 4=Other)")
    MARRIAGE: int = Field(default=2, description="Marital status (1=Married, 2=Single, 3=Other)")
    AGE: int = Field(default=32, description="Borrower age in years", ge=18, le=100)

    # Repayment status (-2 to 8)
    PAY_0: int = Field(default=0, description="Repayment status in Month M (Sept): -1=pay duly, 0=revolving, 1=1mo delay, 2=2mo delay, etc.")
    PAY_2: int = Field(default=0, description="Repayment status in Month M-1 (August)")
    PAY_3: int = Field(default=0, description="Repayment status in Month M-2 (July)")
    PAY_4: int = Field(default=0, description="Repayment status in Month M-3 (June)")
    PAY_5: int = Field(default=0, description="Repayment status in Month M-4 (May)")
    PAY_6: int = Field(default=0, description="Repayment status in Month M-5 (April)")

    # Bill Statement Amounts
    BILL_AMT1: float = Field(default=12500.0, description="Statement bill amount Month M ($)")
    BILL_AMT2: float = Field(default=11800.0, description="Statement bill amount Month M-1 ($)")
    BILL_AMT3: float = Field(default=10500.0, description="Statement bill amount Month M-2 ($)")
    BILL_AMT4: float = Field(default=9200.0, description="Statement bill amount Month M-3 ($)")
    BILL_AMT5: float = Field(default=8400.0, description="Statement bill amount Month M-4 ($)")
    BILL_AMT6: float = Field(default=7500.0, description="Statement bill amount Month M-5 ($)")

    # Payment Amounts Made
    PAY_AMT1: float = Field(default=3500.0, description="Payment executed in Month M ($)")
    PAY_AMT2: float = Field(default=3000.0, description="Payment executed in Month M-1 ($)")
    PAY_AMT3: float = Field(default=2500.0, description="Payment executed in Month M-2 ($)")
    PAY_AMT4: float = Field(default=2000.0, description="Payment executed in Month M-3 ($)")
    PAY_AMT5: float = Field(default=2000.0, description="Payment executed in Month M-4 ($)")
    PAY_AMT6: float = Field(default=1800.0, description="Payment executed in Month M-5 ($)")


class DriverFactor(BaseModel):
    feature: str
    points: int
    label: str
    description: str


class AdverseReason(BaseModel):
    code: str
    title: str
    detail: str


class ScorecardResponse(BaseModel):
    score: int
    pd: float
    pd_percentage: float
    risk_category: str
    risk_color: str
    utilization: float
    top_positive_drivers: List[DriverFactor]
    top_negative_drivers: List[DriverFactor]
    adverse_action_reasons: List[AdverseReason]
    feature_breakdown: Dict[str, Any]


class StressTestRequest(BaseModel):
    scenario_name: str = Field(default="Custom Stress Scenario")
    delay_shift: int = Field(default=1, description="Repayment delay shift in months (e.g. +1 or +2)", ge=0, le=4)
    balance_shock_pct: float = Field(default=15.0, description="Balance expansion % (e.g. +15%)", ge=0.0, le=100.0)
    pd_multiplier: float = Field(default=1.30, description="Macroeconomic default rate shock multiplier", ge=1.0, le=3.0)
    stressed_lgd: float = Field(default=0.55, description="Stressed Loss Given Default", ge=0.1, le=1.0)


class StressTestResponse(BaseModel):
    scenario_name: str
    parameters: Dict[str, Any]
    baseline: Dict[str, Any]
    stressed: Dict[str, Any]
    impact: Dict[str, Any]
    loss_distributions: Dict[str, Any]


class PortfolioMetricsResponse(BaseModel):
    total_records: int
    total_limit: float
    total_ead: float
    total_expected_loss: float
    portfolio_el_rate_bps: float
    weighted_avg_pd: float
    portfolio_lgd: float
    var_95: float
    var_99: float
    cvar_95: float
    cvar_99: float
    unexpected_loss_95: float
    unexpected_loss_99: float
    risk_tier_counts: Dict[str, int]
    loss_histogram: List[Dict[str, Any]]


class MemoRequest(BaseModel):
    applicant_name: Optional[str] = Field(default="Borrower Application #78421")
    features: BorrowerFeatures


class MemoResponse(BaseModel):
    decision: str
    decision_badge_color: str
    scorecard: Dict[str, Any]
    basel_el: Dict[str, Any]
    policy_citations: List[Dict[str, Any]]
    memo_markdown: str
    memo_package: Dict[str, Any]
    underwriter_name: str
    compliance_attestation: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    qdrant_status: str
    qdrant_collection: str
    embedding_model: str
    policies_indexed: int
    portfolio_records_loaded: int
