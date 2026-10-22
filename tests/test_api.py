"""Integration tests for all CredSure AI FastAPI endpoints."""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath("src"))

from starlette.testclient import TestClient
from credsure.api.app import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    """GET /health verifies service status and Qdrant connection."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "qdrant" in data["qdrant_status"].lower()
    assert data["policies_indexed"] > 0
    assert data["portfolio_records_loaded"] >= 500


def test_scorecard_endpoint(client):
    """POST /scorecard/score returns 300-850 score, PD, and reason codes."""
    payload = {
        "LIMIT_BAL": 80000.0,
        "AGE": 38,
        "PAY_0": 0,
        "BILL_AMT1": 24000.0,
        "PAY_AMT1": 8000.0,
    }
    res = client.post("/scorecard/score", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert 300 <= data["score"] <= 850
    assert 0.0 <= data["pd"] <= 1.0
    assert data["risk_category"] in ["Super Prime", "Prime", "Near-Prime", "Subprime", "Deep Subprime"]
    assert len(data["top_positive_drivers"]) > 0 or len(data["top_negative_drivers"]) > 0


def test_presets_endpoint(client):
    """GET /scorecard/presets provides 1-click test configurations."""
    res = client.get("/scorecard/presets")
    assert res.status_code == 200
    data = res.json()
    assert "presets" in data
    assert len(data["presets"]) >= 3


def test_portfolio_metrics_endpoint(client):
    """GET /portfolio/metrics returns Basel EL and Monte Carlo VaR 95/99."""
    res = client.get("/portfolio/metrics")
    assert res.status_code == 200
    data = res.json()
    assert data["total_records"] >= 500
    assert data["total_expected_loss"] > 0
    assert data["var_95"] >= data["total_expected_loss"]
    assert data["var_99"] >= data["var_95"]
    assert "Super Prime" in data["risk_tier_counts"]
    assert len(data["loss_histogram"]) > 0


def test_stress_test_endpoint(client):
    """POST /portfolio/stress-test executes macroeconomic scenario."""
    payload = {
        "scenario_name": "Mild Recession Test",
        "delay_shift": 1,
        "balance_shock_pct": 10.0,
        "pd_multiplier": 1.25,
        "stressed_lgd": 0.50,
    }
    res = client.post("/portfolio/stress-test", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["impact"]["delta_expected_loss"] > 0
    assert data["stressed"]["expected_loss"] > data["baseline"]["expected_loss"]


def test_analyst_memo_endpoint(client):
    """POST /analyst/memo generates structured AI Underwriting Memorandum."""
    payload = {
        "applicant_name": "Jane Doe (#98231)",
        "features": {
            "LIMIT_BAL": 100000.0,
            "AGE": 40,
            "PAY_0": 0,
            "BILL_AMT1": 15000.0,
            "PAY_AMT1": 12000.0,
        },
    }
    res = client.post("/analyst/memo", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["decision"] in ["APPROVED", "CONDITIONAL", "DECLINED"]
    assert "memo_markdown" in data
    assert len(data["memo_markdown"]) > 50
    assert "policy_citations" in data
    assert "memo_package" in data
