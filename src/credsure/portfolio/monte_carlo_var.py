"""Institutional Monte Carlo Value-at-Risk (VaR) and CVaR Simulation Engine.

Simulates 1,000 portfolio macroeconomic default scenarios using vectorized NumPy sampling.
Implements the Basel / Vasicek one-factor asset correlation framework:
    Z ~ N(0, 1)  (Systemic Macroeconomic Factor)
    PD_i(Z) = Phi((Phi^-1(PD_i) - sqrt(rho)*Z) / sqrt(1 - rho))
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np


class MonteCarloRiskEngine:
    """Vectorized Monte Carlo engine for estimating credit portfolio loss distributions,

    95% & 99% Value-at-Risk (VaR), and Conditional Value-at-Risk (CVaR / Expected Shortfall).
    """

    def __init__(
        self,
        n_simulations: int = 1000,
        asset_correlation: float = 0.15,
        default_lgd: float = 0.45,
        seed: Optional[int] = 42,
    ):
        self.n_simulations = n_simulations
        self.asset_correlation = float(asset_correlation)
        self.default_lgd = float(default_lgd)
        self.seed = seed

    def simulate(
        self,
        portfolio_records: List[Dict[str, Any]],
        lgd: Optional[float] = None,
        ccf: float = 0.20,
    ) -> Dict[str, Any]:
        """Execute 1,000-path Monte Carlo credit portfolio simulation."""
        if not portfolio_records:
            return {
                "n_simulations": self.n_simulations,
                "portfolio_ead": 0.0,
                "expected_loss": 0.0,
                "var_95": 0.0,
                "var_99": 0.0,
                "cvar_95": 0.0,
                "cvar_99": 0.0,
                "unexpected_loss_95": 0.0,
                "unexpected_loss_99": 0.0,
                "loss_percentiles": {},
                "histogram": [],
            }

        rng = np.random.default_rng(self.seed)
        lgd_val = self.default_lgd if lgd is None else float(lgd)

        # Extract vectors: EAD and PD
        eads = []
        pds = []
        for r in portfolio_records:
            limit = float(r.get("LIMIT_BAL", 0.0))
            bill = max(0.0, float(r.get("BILL_AMT1", 0.0)))
            undrawn = max(0.0, limit - bill)
            ead = bill + (ccf * undrawn)
            pd = float(r.get("pd", 0.05))
            eads.append(ead)
            pds.append(pd)

        ead_vec = np.array(eads, dtype=np.float64)  # shape (N,)
        pd_vec = np.clip(np.array(pds, dtype=np.float64), 1e-5, 0.999)  # shape (N,)
        total_ead = float(np.sum(ead_vec))

        # Expected Loss benchmark
        baseline_el = float(np.sum(pd_vec * ead_vec * lgd_val))

        # Vasicek / Basel Single-Factor Copula:
        # Z: Macro shock drawn from Standard Normal N(0, 1) across S simulations
        rho = self.asset_correlation
        sqrt_rho = np.sqrt(rho)
        sqrt_one_minus_rho = np.sqrt(1.0 - rho)

        # Draw S macro factor values
        Z = rng.standard_normal(self.n_simulations)  # shape (S,)

        # Approximating Inverse Normal CDF via Rational Polynomial (Winitzki / Abramowitz)
        def norm_ppf(p: np.ndarray) -> np.ndarray:
            # High-accuracy rational approximation for probit function
            c0 = 2.515517
            c1 = 0.802853
            c2 = 0.010328
            d1 = 1.432788
            d2 = 0.189269
            d3 = 0.001308
            p_safe = np.clip(p, 1e-7, 1.0 - 1e-7)
            t = np.where(p_safe < 0.5, np.sqrt(-2.0 * np.log(p_safe)), np.sqrt(-2.0 * np.log(1.0 - p_safe)))
            numerator = c0 + (c1 * t) + (c2 * t * t)
            denominator = 1.0 + (d1 * t) + (d2 * t * t) + (d3 * t * t * t)
            approx = t - (numerator / denominator)
            return np.where(p_safe < 0.5, -approx, approx)

        def norm_cdf(x: np.ndarray) -> np.ndarray:
            # Fast error function approximation
            return 0.5 * (1.0 + np.vectorize(np.tanh)(x * 0.7978845608 * (1.0 + 0.044715 * x * x)))

        # Conditional default probabilities: shape (S, N)
        # PD_conditional = norm_cdf((norm_ppf(pd) - sqrt(rho)*Z) / sqrt(1 - rho))
        inv_norm_pd = norm_ppf(pd_vec)  # (N,)

        # Broadcast Z (S, 1) and inv_norm_pd (1, N)
        numerator = inv_norm_pd[np.newaxis, :] - (sqrt_rho * Z[:, np.newaxis])
        cond_pds = norm_cdf(numerator / sqrt_one_minus_rho)  # (S, N)
        cond_pds = np.clip(cond_pds, 0.0, 1.0)

        # Vectorized Bernoulli draws: Uniform random numbers U(0, 1) of shape (S, N)
        uniform_draws = rng.uniform(0.0, 1.0, size=(self.n_simulations, len(pd_vec)))
        defaults = (uniform_draws < cond_pds).astype(np.float64)  # (S, N)

        # Loss matrix: Defaults (S, N) * EAD (N,) * LGD
        loss_by_obligation = defaults * (ead_vec * lgd_val)[np.newaxis, :]
        simulated_losses = np.sum(loss_by_obligation, axis=1)  # (S,)

        # Sort simulated losses for percentile analysis
        sorted_losses = np.sort(simulated_losses)

        # VaR: Percentiles
        var_95_idx = int(0.95 * self.n_simulations)
        var_99_idx = int(0.99 * self.n_simulations)

        var_95 = float(sorted_losses[var_95_idx])
        var_99 = float(sorted_losses[var_99_idx])

        # CVaR (Conditional Value-at-Risk / Expected Shortfall): Mean of losses >= VaR
        cvar_95 = float(np.mean(sorted_losses[var_95_idx:]))
        cvar_99 = float(np.mean(sorted_losses[var_99_idx:]))

        unexpected_loss_95 = max(0.0, var_95 - baseline_el)
        unexpected_loss_99 = max(0.0, var_99 - baseline_el)

        # Generate 15-bin histogram distribution for frontend visualization
        counts, bin_edges = np.histogram(sorted_losses, bins=15)
        histogram = [
            {
                "bin_start": round(float(bin_edges[i]), 2),
                "bin_end": round(float(bin_edges[i + 1]), 2),
                "midpoint": round(float((bin_edges[i] + bin_edges[i + 1]) / 2.0), 2),
                "count": int(counts[i]),
            }
            for i in range(len(counts))
        ]

        percentiles = {
            "p50": round(float(np.percentile(sorted_losses, 50)), 2),
            "p75": round(float(np.percentile(sorted_losses, 75)), 2),
            "p90": round(float(np.percentile(sorted_losses, 90)), 2),
            "p95": round(var_95, 2),
            "p99": round(var_99, 2),
            "max": round(float(sorted_losses[-1]), 2),
        }

        return {
            "n_simulations": self.n_simulations,
            "portfolio_ead": round(total_ead, 2),
            "expected_loss": round(baseline_el, 2),
            "var_95": round(var_95, 2),
            "var_99": round(var_99, 2),
            "cvar_95": round(cvar_95, 2),
            "cvar_99": round(cvar_99, 2),
            "unexpected_loss_95": round(unexpected_loss_95, 2),
            "unexpected_loss_99": round(unexpected_loss_99, 2),
            "loss_percentiles": percentiles,
            "histogram": histogram,
        }
