"""Lag and rolling demand features."""

import pandas as pd


def add_lag_features(df: pd.DataFrame, target_col: str = "demand_mw") -> pd.DataFrame:
    """Add lagged demand and rolling averages."""
    featured = df.copy().sort_values("datetime")
    for lag in [1, 2, 24, 48, 168]:
        featured[f"lag_{lag}h"] = featured[target_col].shift(lag)
    for window in [6, 24, 168]:
        featured[f"rolling_mean_{window}h"] = featured[target_col].shift(1).rolling(window).mean()
    return featured.dropna().reset_index(drop=True)
