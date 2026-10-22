"""Unit tests for Basel Expected Loss (EL = PD * EAD * LGD) and Monte Carlo VaR."""

import pytest
from credsure.portfolio.expected_loss import BaselExpectedLossEngine, EADMode
from credsure.portfolio.monte_carlo_var import MonteCarloRiskEngine
from credsure.portfolio.stress_testing import MacroStressTester


def test_basel_expected_loss_modes():
    """Verify EAD modes: Statement Balance, Authorized Limit, and Basel CCF."""
    engine = BaselExpectedLossEngine(default_lgd=0.45, default_ccf=0.20)

    limit = 100000.0
    drawn = 40000.0
    pd = 0.05

    # 1. Statement balance mode: EAD = drawn = 40,000
    ead_stat = engine.calculate_ead(limit, drawn, mode=EADMode.STATEMENT_BALANCE)
    assert ead_stat == 40000.0

    # 2. Authorized limit mode: EAD = 100,000
    ead_limit = engine.calculate_ead(limit, drawn, mode=EADMode.AUTHORIZED_LIMIT)
    assert ead_limit == 100000.0

    # 3. Basel CCF mode: 40,000 + 0.20 * (60,000) = 52,000
    ead_ccf = engine.calculate_ead(limit, drawn, mode=EADMode.BASEL_CCF)
    assert ead_ccf == 52000.0

    # 4. EL single facility calculation
    single = engine.calculate_single(pd=pd, limit_bal=limit, bill_amt1=drawn, mode=EADMode.BASEL_CCF)
    assert single["ead"] == 52000.0
    assert single["expected_loss"] == round(0.05 * 52000.0 * 0.45, 2)  # $1,170.00


def test_monte_carlo_var_bounds():
    """Verify 1,000-run Monte Carlo VaR satisfies VaR 95 < VaR 99 <= max loss."""
    mc_engine = MonteCarloRiskEngine(n_simulations=1000, asset_correlation=0.15, default_lgd=0.45, seed=42)

    sample_portfolio = [
        {"LIMIT_BAL": 50000.0, "BILL_AMT1": 20000.0, "pd": 0.03},
        {"LIMIT_BAL": 100000.0, "BILL_AMT1": 60000.0, "pd": 0.08},
        {"LIMIT_BAL": 80000.0, "BILL_AMT1": 40000.0, "pd": 0.05},
        {"LIMIT_BAL": 30000.0, "BILL_AMT1": 25000.0, "pd": 0.12},
    ]

    sim = mc_engine.simulate(sample_portfolio)

    assert sim["n_simulations"] == 1000
    assert sim["portfolio_ead"] > 0
    assert sim["expected_loss"] > 0
    assert sim["var_95"] >= sim["expected_loss"]
    assert sim["var_99"] >= sim["var_95"]
    assert sim["cvar_95"] >= sim["var_95"]
    assert sim["cvar_99"] >= sim["var_99"]
    assert len(sim["histogram"]) > 0


def test_stress_testing_impact():
    """Verify macroeconomic perturbation shifts expected loss upwards."""
    stress_tester = MacroStressTester()
    sample_portfolio = [
        {"LIMIT_BAL": 50000.0, "BILL_AMT1": 20000.0, "PAY_0": 0, "pd": 0.04},
        {"LIMIT_BAL": 100000.0, "BILL_AMT1": 70000.0, "PAY_0": 1, "pd": 0.09},
    ]

    res = stress_tester.apply_scenario(
        sample_portfolio,
        scenario_name="Stress Check",
        delay_shift=1,
        balance_shock_pct=15.0,
        pd_multiplier=1.4,
        stressed_lgd=0.55,
        run_monte_carlo=False,
    )

    assert res["stressed"]["expected_loss"] > res["baseline"]["expected_loss"]
    assert res["impact"]["delta_expected_loss"] > 0
    assert res["impact"]["pct_increase_expected_loss"] > 0
