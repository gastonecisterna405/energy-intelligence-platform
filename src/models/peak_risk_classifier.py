"""Peak demand risk scoring models."""

from __future__ import annotations

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.config import MODELS_DIR, RANDOM_STATE, TEST_SIZE_FRACTION
from src.models.demand_forecasting_xgboost import FEATURE_COLUMNS


def add_peak_risk_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Create Low, Medium and High labels from demand percentiles."""
    labeled = df.copy()
    q75 = labeled["demand_mw"].quantile(0.75)
    q90 = labeled["demand_mw"].quantile(0.90)
    labeled["risk_label"] = np.select(
        [labeled["demand_mw"] >= q90, labeled["demand_mw"] >= q75],
        ["High", "Medium"],
        default="Low",
    )
    label_order = {"Low": 0, "Medium": 1, "High": 2}
    labeled["risk_class"] = labeled["risk_label"].map(label_order)
    return labeled


def train_peak_risk_classifier(features: pd.DataFrame) -> tuple[pd.DataFrame, dict, object]:
    """Train logistic baseline and random forest peak-risk classifier."""
    labeled = add_peak_risk_labels(features).sort_values("datetime")
    split_idx = int(len(labeled) * (1 - TEST_SIZE_FRACTION))
    train, test = labeled.iloc[:split_idx], labeled.iloc[split_idx:]

    baseline = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    baseline.fit(train[FEATURE_COLUMNS], train["risk_class"])

    model = RandomForestClassifier(n_estimators=220, max_depth=10, class_weight="balanced", random_state=RANDOM_STATE)
    model.fit(train[FEATURE_COLUMNS], train["risk_class"])
    pred = model.predict(test[FEATURE_COLUMNS])
    probabilities = model.predict_proba(test[FEATURE_COLUMNS])
    risk_score = np.clip(probabilities[:, 2] * 100, 0, 100)

    label_lookup = {0: "Low", 1: "Medium", 2: "High"}
    scores = pd.DataFrame(
        {
            "datetime": test["datetime"].values,
            "demand_mw": test["demand_mw"].values,
            "actual_risk_label": test["risk_label"].values,
            "predicted_risk_label": [label_lookup[int(x)] for x in pred],
            "risk_score": risk_score.round(2),
        }
    )
    metrics = {
        "accuracy": float(accuracy_score(test["risk_class"], pred)),
        "precision_macro": float(precision_score(test["risk_class"], pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(test["risk_class"], pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(test["risk_class"], pred, average="macro", zero_division=0)),
        "confusion_matrix": confusion_matrix(test["risk_class"], pred).tolist(),
        "classification_report": classification_report(test["risk_class"], pred, output_dict=True, zero_division=0),
    }
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "baseline": baseline, "features": FEATURE_COLUMNS}, MODELS_DIR / "peak_risk_classifier.joblib")
    return scores, metrics, model
