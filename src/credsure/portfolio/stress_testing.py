"""Institutional Stress Testing Engine for Macroeconomic Shocks.

Simulates regulatory stress scenarios (CCAR / DFAST / EBA compliant):
- Repayment delay shifts (+1 or +2 months delinquency across accounts)
- Balance expansion (+15% drawn balance expansion)
- Economic downturn PD multipliers (1.25x - 1.75x)
- LGD deterioration (45% -> 55% - 65%)
"""

from typing import Dict, List, Any, Optional
import copy
import numpy as np
from credsure.portfolio.expected_loss import BaselExpectedLossEngine, EADMode
from credsure.portfolio.monte_carlo_var import MonteCarloRiskEngine


class MacroStressTester:
    """Executes macroeconomic perturbation stress tests across credit portfolios

    and individual facilities to evaluate capital vulnerability.
    """

    def __init__(
        self,
        el_engine: Optional[BaselExpectedLossEngine] = None,
        mc_engine: Optional[MonteCarloRiskEngine] = None,
    ):
        self.el_engine = el_engine or BaselExpectedLossEngine()
        self.mc_engine = mc_engine or MonteCarloRiskEngine()

    def apply_scenario(
        self,
        portfolio_records: List[Dict[str, Any]],
        scenario_name: str = "custom",
        delay_shift: int = 1,
        balance_shock_pct: float = 15.0,
        pd_multiplier: float = 1.30,
        stressed_lgd: float = 0.55,
        run_monte_carlo: bool = True,
    ) -> Dict[str, Any]:
        """Apply macro stress parameters to a portfolio and evaluate impact against baseline."""
        # 1. Baseline analysis
        baseline_el = self.el_engine.calculate_portfolio(portfolio_records)
        baseline_mc = self.mc_engine.simulate(portfolio_records) if run_monte_carlo else {}

        # 2. Perturb records
        stressed_records = []
        balance_mult = 1.0 + (balance_shock_pct / 100.0)

        for rec in portfolio_records:
            s_rec = copy.deepcopy(rec)

            # Payment delay shift
            for pay_key in ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]:
                if pay_key in s_rec:
                    curr_val = int(s_rec[pay_key])
                    # If already delinquent or revolving, shift delinquency upwards
                    if curr_val >= 0:
                        s_rec[pay_key] = curr_val + delay_shift

            # Balance expansion shock
            if "BILL_AMT1" in s_rec:
                s_rec["BILL_AMT1"] = float(s_rec["BILL_AMT1"]) * balance_mult

            # Stressed PD
            curr_pd = float(s_rec.get("pd", 0.05))
            stressed_pd = min(0.999, curr_pd * pd_multiplier)
            s_rec["pd"] = stressed_pd

            stressed_records.append(s_rec)

        # 3. Evaluate stressed portfolio
        stressed_el = self.el_engine.calculate_portfolio(
            stressed_records,
            lgd=stressed_lgd,
            mode=EADMode.BASEL_CCF,
        )

        stressed_mc = (
            self.mc_engine.simulate(stressed_records, lgd=stressed_lgd)
            if run_monte_carlo
            else {}
        )

        # 4. Comparative deltas
        base_loss = baseline_el["total_expected_loss"]
        stress_loss = stressed_el["total_expected_loss"]
        delta_el = stress_loss - base_loss
        pct_increase_el = ((delta_el / base_loss) * 100.0) if base_loss > 0 else 0.0

        base_var95 = baseline_mc.get("var_95", 0.0)
        stress_var95 = stressed_mc.get("var_95", 0.0)
        delta_var95 = stress_var95 - base_var95

        base_var99 = baseline_mc.get("var_99", 0.0)
        stress_var99 = stressed_mc.get("var_99", 0.0)
        delta_var99 = stress_var99 - base_var99

        return {
            "scenario_name": scenario_name,
            "parameters": {
                "delay_shift_months": delay_shift,
                "balance_expansion_pct": balance_shock_pct,
                "pd_multiplier": pd_multiplier,
                "stressed_lgd": stressed_lgd,
            },
            "baseline": {
                "total_ead": baseline_el["total_ead"],
                "expected_loss": base_loss,
                "el_rate_bps": baseline_el["portfolio_el_rate_bps"],
                "weighted_avg_pd": baseline_el["weighted_avg_pd"],
                "var_95": base_var95,
                "var_99": base_var99,
                "cvar_95": baseline_mc.get("cvar_95", 0.0),
                "cvar_99": baseline_mc.get("cvar_99", 0.0),
            },
            "stressed": {
                "total_ead": stressed_el["total_ead"],
                "expected_loss": stress_loss,
                "el_rate_bps": stressed_el["portfolio_el_rate_bps"],
                "weighted_avg_pd": stressed_el["weighted_avg_pd"],
                "var_95": stress_var95,
                "var_99": stress_var99,
                "cvar_95": stressed_mc.get("cvar_95", 0.0),
                "cvar_99": stressed_mc.get("cvar_99", 0.0),
            },
            "impact": {
                "delta_expected_loss": round(delta_el, 2),
                "pct_increase_expected_loss": round(pct_increase_el, 2),
                "delta_var_95": round(delta_var95, 2),
                "delta_var_99": round(delta_var99, 2),
                "capital_strain_status": "Severe" if pct_increase_el > 50 else ("Moderate" if pct_increase_el > 20 else "Manageable"),
            },
            "loss_distributions": {
                "baseline_histogram": baseline_mc.get("histogram", []),
                "stressed_histogram": stressed_mc.get("histogram", []),
            },
        }

    def get_standard_scenarios(
        self, portfolio_records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run standard institutional scenarios: Mild Recession and Severe Stagflation."""
        mild = self.apply_scenario(
            portfolio_records,
            scenario_name="Mild Recession",
            delay_shift=1,
            balance_shock_pct=10.0,
            pd_multiplier=1.20,
            stressed_lgd=0.50,
            run_monte_carlo=True,
        )

        severe = self.apply_scenario(
            portfolio_records,
            scenario_name="Severe Stagflation",
            delay_shift=2,
            balance_shock_pct=15.0,
            pd_multiplier=1.50,
            stressed_lgd=0.60,
            run_monte_carlo=True,
        )

        return {
            "mild_recession": mild,
            "severe_stagflation": severe,
        }
