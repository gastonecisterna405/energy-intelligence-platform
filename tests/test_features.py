import pandas as pd

from src.features.lag_features import add_lag_features
from src.features.time_features import add_time_features


def test_time_and_lag_features_are_created():
    df = pd.DataFrame({"datetime": pd.date_range("2024-01-01", periods=200, freq="h"), "demand_mw": range(200)})
    featured = add_lag_features(add_time_features(df))
    assert {"hour", "day_of_week", "lag_24h", "rolling_mean_24h"}.issubset(featured.columns)
    assert not featured.empty
