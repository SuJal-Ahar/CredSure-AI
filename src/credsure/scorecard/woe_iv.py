"""Weight of Evidence (WoE) and Information Value (IV) calculation engine.

Strictly statistical implementation using pure NumPy (with full Pandas DataFrame support).
No black-box machine learning models.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None


class WoEIVTransformer:
    """Computes Weight of Evidence (WoE) and Information Value (IV)

    for continuous and categorical features.

    WoE = ln((% Non-Defaults) / (% Defaults))
    IV = sum((% Non-Default - % Default) * WoE)

    Industry Standard Rules:
    - IV < 0.02: Unpredictive (discarded)
    - 0.02 <= IV < 0.1: Weak predictor
    - 0.1 <= IV < 0.3: Medium predictor
    - 0.3 <= IV < 0.5: Strong predictor
    - IV >= 0.5: Suspicious / over-predictive
    """

    def __init__(self, iv_threshold: float = 0.02, epsilon: float = 1e-4):
        self.iv_threshold = iv_threshold
        self.epsilon = epsilon
        self.bins: Dict[str, List[Dict[str, Any]]] = {}
        self.iv_summary: Dict[str, float] = {}
        self.selected_features: List[str] = []

    def fit_feature(
        self,
        values: Union[np.ndarray, List[Any], Any],
        targets: Union[np.ndarray, List[int], Any],
        feature_name: str,
        n_bins: int = 5,
        is_categorical: bool = False,
    ) -> Tuple[List[Dict[str, Any]], float]:
        """Fit WoE bins and calculate IV for a single feature using NumPy."""
        targets = np.asarray(targets, dtype=int)
        values = np.asarray(values)

        total_goods = int(np.sum(targets == 0))
        total_bads = int(np.sum(targets == 1))

        if total_goods == 0 or total_bads == 0:
            raise ValueError("Target variable must contain both 0 (good) and 1 (bad) observations.")

        bin_data = []

        if is_categorical:
            unique_cats = np.unique(values)
            for cat in unique_cats:
                mask = values == cat
                goods = int(np.sum((mask) & (targets == 0)))
                bads = int(np.sum((mask) & (targets == 1)))
                bin_data.append({
                    "category": cat,
                    "is_cat": True,
                    "goods": goods,
                    "bads": bads,
                    "label": str(cat),
                })
        else:
            # Continuous feature: calculate quantiles via numpy
            try:
                num_vals = values.astype(float)
                # Compute distinct quantile bin edges
                percentiles = np.linspace(0, 100, n_bins + 1)
                q_edges = np.unique(np.percentile(num_vals, percentiles))
                if len(q_edges) <= 2:
                    q_edges = np.linspace(np.min(num_vals), np.max(num_vals), n_bins + 1)
                    q_edges = np.unique(q_edges)
            except Exception:
                q_edges = np.array([-np.inf, np.inf])

            if len(q_edges) < 2:
                q_edges = np.array([-np.inf, np.inf])

            q_edges = list(q_edges)
            q_edges[0] = -np.inf
            q_edges[-1] = np.inf

            for i in range(len(q_edges) - 1):
                lower = q_edges[i]
                upper = q_edges[i + 1]
                if lower == -np.inf:
                    mask = num_vals <= upper
                elif upper == np.inf:
                    mask = num_vals > lower
                else:
                    mask = (num_vals > lower) & (num_vals <= upper)

                goods = int(np.sum((mask) & (targets == 0)))
                bads = int(np.sum((mask) & (targets == 1)))

                lbl = f"{round(lower, 2) if lower != -np.inf else '-∞'} to {round(upper, 2) if upper != np.inf else '+∞'}"
                bin_data.append({
                    "lower": lower,
                    "upper": upper,
                    "is_cat": False,
                    "goods": goods,
                    "bads": bads,
                    "label": lbl,
                })

        feature_iv = 0.0
        final_bins = []

        for b in bin_data:
            goods = b["goods"]
            bads = b["bads"]

            dist_good = max(goods / total_goods, self.epsilon)
            dist_bad = max(bads / total_bads, self.epsilon)

            woe = float(np.log(dist_good / dist_bad))
            bin_iv = (dist_good - dist_bad) * woe
            feature_iv += bin_iv

            b_record = dict(b)
            b_record["dist_good"] = dist_good
            b_record["dist_bad"] = dist_bad
            b_record["woe"] = woe
            b_record["bin_iv"] = float(bin_iv)
            final_bins.append(b_record)

        feature_iv = float(feature_iv)
        return final_bins, feature_iv

    def fit(
        self,
        data: Any,
        features: List[str],
        target: str = "default",
        categorical_features: Optional[List[str]] = None,
        n_bins: int = 5,
    ) -> "WoEIVTransformer":
        """Fit WoE and IV across all specified features."""
        categorical_features = categorical_features or []
        self.bins = {}
        self.iv_summary = {}
        self.selected_features = []

        # Support both Pandas DataFrame and dict of arrays/lists
        is_df = HAS_PANDAS and isinstance(data, pd.DataFrame)
        targets = data[target] if is_df else data[target]

        for f in features:
            if f == target:
                continue
            if is_df and f not in data.columns:
                continue
            if not is_df and f not in data:
                continue

            vals = data[f]
            is_cat = f in categorical_features
            bins, iv = self.fit_feature(vals, targets, f, n_bins=n_bins, is_categorical=is_cat)
            self.iv_summary[f] = iv
            self.bins[f] = bins

            if iv >= self.iv_threshold:
                self.selected_features.append(f)

        return self

    def transform_value(self, feature: str, value: Any) -> Tuple[float, str]:
        """Map a single feature value to its corresponding WoE and bin label."""
        if feature not in self.bins:
            return 0.0, "unknown"

        bin_list = self.bins[feature]
        for b in bin_list:
            if b.get("is_cat", False):
                if b["category"] == value or str(b["category"]) == str(value):
                    return b["woe"], b["label"]
            else:
                lower = b["lower"]
                upper = b["upper"]
                try:
                    num_val = float(value)
                    if (num_val > lower or lower == -np.inf) and (num_val <= upper or upper == np.inf):
                        return b["woe"], b["label"]
                except (ValueError, TypeError):
                    continue

        if bin_list:
            return bin_list[0]["woe"], bin_list[0]["label"]
        return 0.0, "unassigned"

    def get_feature_iv_dict(self) -> Dict[str, float]:
        """Return the dictionary of IV values for all fitted features."""
        return self.iv_summary
