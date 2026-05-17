"""XGBoost demand forecasting model."""

from __future__ import annotations

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor

from src.config import MODELS_DIR, RANDOM_STATE, TEST_SIZE_FRACTION
from src.models.model_evaluation import regression_metrics

FEATURE_COLUMNS = [
    "hour",
    "day_of_week",
    "month",
    "year",
    "day_of_year",
    "is_weekend",
    "is_business_hour",
    "lag_1h",
    "lag_2h",
    "lag_24h",
    "lag_48h",
    "lag_168h",
    "rolling_mean_6h",
    "rolling_mean_24h",
    "rolling_mean_168h",
]


def _build_regressor():
    try:
        from xgboost import XGBRegressor

        return XGBRegressor(
            n_estimators=180,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="reg:squarederror",
            random_state=RANDOM_STATE,
        )
    except Exception:
        return GradientBoostingRegressor(random_state=RANDOM_STATE)


def train_xgboost_forecaster(features: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float], object]:
    """Train a tree-based demand forecasting model on time and lag features."""
    ordered = features.sort_values("datetime").dropna(subset=FEATURE_COLUMNS + ["demand_mw"])
    split_idx = int(len(ordered) * (1 - TEST_SIZE_FRACTION))
    train, test = ordered.iloc[:split_idx], ordered.iloc[split_idx:]
    model = _build_regressor()
    model.fit(train[FEATURE_COLUMNS], train["demand_mw"])
    predictions = model.predict(test[FEATURE_COLUMNS])

    forecast = pd.DataFrame(
        {
            "datetime": test["datetime"].values,
            "actual_demand_mw": test["demand_mw"].values,
            "predicted_demand_mw": predictions,
            "model": "xgboost_regressor",
        }
    )
    metrics = regression_metrics(forecast["actual_demand_mw"], forecast["predicted_demand_mw"])
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURE_COLUMNS}, MODELS_DIR / "xgboost_demand_model.joblib")
    return forecast, metrics, model
