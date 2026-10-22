"""FICO Points Scaling Engine.

Translates log-odds and Weight of Evidence (WoE) into institutional credit scores
bounded strictly between 300 and 850, with transparent feature points breakdown.
"""

from typing import Dict, List, Tuple
import numpy as np


class PointsScaler:
    """Converts linear log-odds and WoE metrics into FICO-style credit scores (300 to 850).

    Formula:
        Factor = PDO / ln(2)
        Offset = Base Score - Factor * ln(Base Odds)
        Score = Base Score + sum(Points Deltas)

    Default Parameters:
        Base Score = 600
        PDO (Points to Double the Odds) = 20
        Base Odds = 50:1 (Non-default to Default)
    """

    def __init__(
        self,
        base_score: float = 600.0,
        pdo: float = 20.0,
        base_odds: float = 50.0,
        min_score: int = 300,
        max_score: int = 850,
    ):
        self.base_score = float(base_score)
        self.pdo = float(pdo)
        self.base_odds = float(base_odds)
        self.min_score = min_score
        self.max_score = max_score

        # Factor and Offset derivation
        self.factor = self.pdo / np.log(2.0)  # ~28.85
        self.offset = self.base_score - (self.factor * np.log(self.base_odds))

    def pd_to_score(self, pd: float) -> int:
        """Convert a Probability of Default (PD) into a bounded credit score (300 - 850)."""
        clamped_pd = float(np.clip(pd, 1e-6, 1.0 - 1e-6))
        odds = (1.0 - clamped_pd) / clamped_pd
        score = self.offset + (self.factor * np.log(odds))
        return int(np.clip(np.round(score), self.min_score, self.max_score))

    def score_to_pd(self, score: float) -> float:
        """Inverse mapping: Convert a credit score back to estimated PD."""
        clamped_score = float(np.clip(score, self.min_score, self.max_score))
        log_odds = (clamped_score - self.offset) / self.factor
        odds = np.exp(log_odds)
        pd = 1.0 / (1.0 + odds)
        return float(np.clip(pd, 0.0001, 0.9999))

    def calculate_bin_points(
        self,
        feature_weights: Dict[str, float],
        feature_woes: Dict[str, float],
    ) -> Tuple[int, Dict[str, int]]:
        """Calculate total score and integer point deltas for each feature."""
        feature_deltas: Dict[str, int] = {}
        total_delta = 0

        for feature, woe in feature_woes.items():
            # Scaling coefficient so individual bin deltas match banking conventions:
            # e.g., PAY_0 on-time: ~+30 pts; PAY_0 60-day late: ~-70 pts
            weight = feature_weights.get(feature, 1.0)
            pts_delta = int(np.round(self.factor * weight * woe))
            feature_deltas[feature] = pts_delta
            total_delta += pts_delta

        raw_score = int(np.round(self.base_score + total_delta))
        final_score = int(np.clip(raw_score, self.min_score, self.max_score))

        return final_score, feature_deltas

    def categorize_risk(self, score: int) -> Tuple[str, str]:
        """Categorize credit score into regulatory rating tiers."""
        if score >= 740:
            return "Super Prime", "#10B981"  # Emerald
        elif score >= 670:
            return "Prime", "#3B82F6"  # Blue
        elif score >= 580:
            return "Near-Prime", "#F59E0B"  # Amber
        elif score >= 500:
            return "Subprime", "#F97316"  # Orange
        else:
            return "Deep Subprime", "#EF4444"  # Red
