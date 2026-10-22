"""Unit tests for Weight of Evidence (WoE), Information Value (IV), and Points Scaling."""

import pytest
import numpy as np
from credsure.scorecard.woe_iv import WoEIVTransformer
from credsure.scorecard.points_scaling import PointsScaler
from credsure.scorecard.calculator import ScorecardCalculator


def test_woe_iv_calculation():
    """Verify WoE and IV mathematical bounds and directionality."""
    transformer = WoEIVTransformer(iv_threshold=0.02)

    # Synthetic test data: feature strongly correlates with default
    rng = np.random.default_rng(123)
    feature_vals = np.concatenate([rng.normal(20, 5, 200), rng.normal(50, 5, 200)])
    targets = np.concatenate([np.zeros(200, dtype=int), np.ones(200, dtype=int)])

    bins, iv = transformer.fit_feature(feature_vals, targets, feature_name="test_feature", n_bins=4)

    assert len(bins) >= 2
    assert iv > 0.02, "Predictive feature should exceed IV threshold of 0.02"

    for b in bins:
        assert "woe" in b
        assert "dist_good" in b
        assert "dist_bad" in b
        assert isinstance(b["woe"], float)


def test_points_scaling_fico_bounds():
    """Verify points scaling maps log-odds strictly into 300-850 FICO bounds."""
    scaler = PointsScaler(base_score=600.0, pdo=20.0, base_odds=50.0)

    # 1. Base odds (1/51 default rate ~ 0.0196) should map near base score 600
    base_score = scaler.pd_to_score(1.0 / 51.0)
    assert 595 <= base_score <= 605

    # 2. Extreme low risk (PD ~ 0.0001) should map to Super Prime (>= 740)
    high_score = scaler.pd_to_score(0.0001)
    assert high_score >= 740
    assert high_score <= 850

    # 3. Extreme high risk (PD ~ 0.99) should map to Subprime (<= 400)
    low_score = scaler.pd_to_score(0.99)
    assert low_score <= 400
    assert low_score >= 300

    # 4. Inverse mapping: score -> pd
    reconstructed_pd = scaler.score_to_pd(base_score)
    assert abs(reconstructed_pd - (1.0 / 51.0)) < 0.01


def test_calculator_reasons_and_categories():
    """Verify borrower evaluation produces valid rating tier, drivers, and adverse codes."""
    calc = ScorecardCalculator()

    # High risk delinquent borrower
    bad_borrower = {
        "LIMIT_BAL": 15000.0,
        "PAY_0": 2,  # 60 day late
        "PAY_2": 2,
        "BILL_AMT1": 14500.0,  # ~96% util
        "PAY_AMT1": 200.0,
    }
    result = calc.evaluate(bad_borrower)

    assert 300 <= result["score"] <= 850
    assert result["risk_category"] in ["Subprime", "Deep Subprime"]
    assert result["utilization"] > 80.0
    assert len(result["adverse_action_reasons"]) > 0
    assert any(r["code"] == "RC-01" for r in result["adverse_action_reasons"])

    # Pristine Prime borrower
    good_borrower = {
        "LIMIT_BAL": 150000.0,
        "PAY_0": 0,
        "PAY_2": 0,
        "BILL_AMT1": 15000.0,  # 10% util
        "PAY_AMT1": 15000.0,
        "AGE": 45,
    }
    good_res = calc.evaluate(good_borrower)
    assert good_res["score"] >= 680
    assert good_res["risk_category"] in ["Prime", "Super Prime"]
