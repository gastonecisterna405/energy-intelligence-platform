import pandas as pd

from src.data.load_data import generate_sample_demand
from src.features.lag_features import add_lag_features
from src.features.time_features import add_time_features
from src.models.peak_risk_classifier import add_peak_risk_labels


def test_peak_risk_labels_include_expected_classes():
    df = add_lag_features(add_time_features(generate_sample_demand(periods=400)))
    labeled = add_peak_risk_labels(df)
    assert set(labeled["risk_label"].unique()).issubset({"Low", "Medium", "High"})
    assert labeled["risk_class"].notna().all()
