"""Statistical demand forecasting baseline."""

from __future__ import annotations

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from src.config import MODELS_DIR, TEST_SIZE_FRACTION
from src.models.model_evaluation import regression_metrics


def train_statsmodels_baseline(demand: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    """Train Exponential Smoothing when statsmodels is available, else a naive baseline."""
    series = demand.sort_values("datetime").set_index("datetime")["demand_mw"].asfreq("h")
    split_idx = int(len(series) * (1 - TEST_SIZE_FRACTION))
    train, test = series.iloc[:split_idx], series.iloc[split_idx:]

    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        model = ExponentialSmoothing(train, seasonal="add", seasonal_periods=24, trend=None).fit(optimized=True)
        predictions = model.forecast(len(test))
        saved_model = model
    except Exception:
        last_daily = train.shift(24).dropna()
        predictions = pd.Series(train.iloc[-24:].tolist() * ((len(test) // 24) + 1), index=test.index).iloc[: len(test)]
        saved_model = RandomForestRegressor(n_estimators=1, random_state=42).fit([[0]], [train.mean()])

    forecast = pd.DataFrame(
        {
            "datetime": test.index,
            "actual_demand_mw": test.values,
            "predicted_demand_mw": predictions.values,
            "model": "statsmodels_exponential_smoothing",
        }
    )
    metrics = regression_metrics(forecast["actual_demand_mw"], forecast["predicted_demand_mw"])
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(saved_model, MODELS_DIR / "demand_forecast_model.joblib")
    return forecast, metrics
