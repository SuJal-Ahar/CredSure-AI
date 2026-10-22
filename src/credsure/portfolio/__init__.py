"""Portfolio risk management and stress testing module.

Computes Basel Expected Loss (EL = PD * EAD * LGD),
Vectorized Monte Carlo Value-at-Risk (VaR 95/99) & CVaR,
and macroeconomic perturbation stress scenarios.
"""

from credsure.portfolio.expected_loss import BaselExpectedLossEngine
from credsure.portfolio.monte_carlo_var import MonteCarloRiskEngine
from credsure.portfolio.stress_testing import MacroStressTester

__all__ = ["BaselExpectedLossEngine", "MonteCarloRiskEngine", "MacroStressTester"]
