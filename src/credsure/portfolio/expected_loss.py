"""Basel II / III Expected Loss (EL) Calculation Engine.

Formula:
    EL = PD * EAD * LGD

Exposure at Default (EAD) Modes:
1. 'statement_balance': Current drawn statement balance (max(BILL_AMT1, 0))
2. 'authorized_limit': Maximum contractual limit (LIMIT_BAL)
3. 'basel_ccf': Drawn + Credit Conversion Factor (CCF 20%) on undrawn commitment
"""

from enum import Enum
from typing import Dict, List, Any, Optional
import numpy as np


class EADMode(str, Enum):
    STATEMENT_BALANCE = "statement_balance"
    AUTHORIZED_LIMIT = "authorized_limit"
    BASEL_CCF = "basel_ccf"


class BaselExpectedLossEngine:
    """Computes Expected Loss (EL), Exposure at Default (EAD), and Loss Given Default (LGD)

    in compliance with Basel Committee on Banking Supervision (BCBS) standards.
    """

    def __init__(self, default_lgd: float = 0.45, default_ccf: float = 0.20):
        self.default_lgd = float(default_lgd)
        self.default_ccf = float(default_ccf)

    def calculate_ead(
        self,
        limit_bal: float,
        bill_amt1: float,
        mode: EADMode = EADMode.BASEL_CCF,
        ccf: Optional[float] = None,
    ) -> float:
        """Calculate Exposure at Default based on chosen regulatory mode."""
        ccf_val = self.default_ccf if ccf is None else float(ccf)
        drawn = max(0.0, float(bill_amt1))
        limit = max(0.0, float(limit_bal))

        if mode == EADMode.STATEMENT_BALANCE:
            return drawn
        elif mode == EADMode.AUTHORIZED_LIMIT:
            return limit
        elif mode == EADMode.BASEL_CCF:
            undrawn = max(0.0, limit - drawn)
            return drawn + (ccf_val * undrawn)
        else:
            raise ValueError(f"Unsupported EAD mode: {mode}")

    def calculate_single(
        self,
        pd: float,
        limit_bal: float,
        bill_amt1: float,
        lgd: Optional[float] = None,
        mode: EADMode = EADMode.BASEL_CCF,
    ) -> Dict[str, float]:
        """Calculate EL, EAD, and metrics for a single loan/facility."""
        lgd_val = self.default_lgd if lgd is None else float(lgd)
        ead = self.calculate_ead(limit_bal, bill_amt1, mode=mode)
        el = pd * ead * lgd_val

        return {
            "pd": round(float(pd), 4),
            "ead": round(float(ead), 2),
            "lgd": round(float(lgd_val), 4),
            "expected_loss": round(float(el), 2),
            "el_rate_percent": round(float(pd * lgd_val * 100), 2),
        }

    def calculate_portfolio(
        self,
        records: List[Dict[str, Any]],
        lgd: Optional[float] = None,
        mode: EADMode = EADMode.BASEL_CCF,
    ) -> Dict[str, Any]:
        """Vectorized Expected Loss computation across an entire credit portfolio."""
        if not records:
            return {
                "total_records": 0,
                "total_limit": 0.0,
                "total_ead": 0.0,
                "total_expected_loss": 0.0,
                "portfolio_el_rate_bps": 0.0,
                "weighted_avg_pd": 0.0,
                "portfolio_lgd": self.default_lgd,
                "ead_mode": mode.value if hasattr(mode, "value") else str(mode),
            }

        lgd_val = self.default_lgd if lgd is None else float(lgd)

        limits = np.array([float(r.get("LIMIT_BAL", 0.0)) for r in records], dtype=np.float64)
        bills = np.array([float(r.get("BILL_AMT1", 0.0)) for r in records], dtype=np.float64)
        pds = np.array([float(r.get("pd", 0.05)) for r in records], dtype=np.float64)

        drawn = np.maximum(bills, 0.0)
        limits = np.maximum(limits, 0.0)

        if mode == EADMode.STATEMENT_BALANCE:
            eads = drawn
        elif mode == EADMode.AUTHORIZED_LIMIT:
            eads = limits
        else:
            undrawn = np.maximum(limits - drawn, 0.0)
            eads = drawn + (self.default_ccf * undrawn)

        # EL vector = PD * EAD * LGD
        els = pds * eads * lgd_val

        total_limit = float(np.sum(limits))
        total_ead = float(np.sum(eads))
        total_el = float(np.sum(els))

        weighted_pd = float(np.sum(pds * eads) / total_ead) if total_ead > 0 else float(np.mean(pds))
        el_rate_bps = (total_el / total_ead) * 10000.0 if total_ead > 0 else 0.0

        return {
            "total_records": len(records),
            "total_limit": round(total_limit, 2),
            "total_ead": round(total_ead, 2),
            "total_expected_loss": round(total_el, 2),
            "portfolio_el_rate_bps": round(el_rate_bps, 1),
            "weighted_avg_pd": round(weighted_pd, 4),
            "portfolio_lgd": round(lgd_val, 4),
            "ead_mode": mode.value if hasattr(mode, "value") else str(mode),
        }
