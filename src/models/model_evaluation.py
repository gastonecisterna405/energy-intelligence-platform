"""Shared model evaluation utilities."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


def regression_metrics(y_true: pd.Series, y_pred: pd.Series) -> dict[str, float]:
    """Return MAE, RMSE and MAPE for demand forecasts."""
    y_true_arr = np.asarray(y_true, dtype=float)
    y_pred_arr = np.asarray(y_pred, dtype=float)
    mape = np.mean(np.abs((y_true_arr - y_pred_arr) / np.clip(np.abs(y_true_arr), 1e-9, None))) * 100
    return {
        "mae": float(mean_absolute_error(y_true_arr, y_pred_arr)),
        "rmse": float(np.sqrt(mean_squared_error(y_true_arr, y_pred_arr))),
        "mape": float(mape),
    }


def save_json(payload: dict, path: Path) -> None:
    """Persist a dictionary as formatted JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
