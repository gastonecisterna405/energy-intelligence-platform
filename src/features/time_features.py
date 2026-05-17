"""Time-based feature engineering."""

import pandas as pd


def add_time_features(df: pd.DataFrame, datetime_col: str = "datetime") -> pd.DataFrame:
    """Add calendar features used by forecasting and risk models."""
    featured = df.copy()
    dt = pd.to_datetime(featured[datetime_col])
    featured["hour"] = dt.dt.hour
    featured["day_of_week"] = dt.dt.dayofweek
    featured["month"] = dt.dt.month
    featured["year"] = dt.dt.year
    featured["day_of_year"] = dt.dt.dayofyear
    featured["is_weekend"] = (featured["day_of_week"] >= 5).astype(int)
    featured["is_business_hour"] = featured["hour"].between(8, 18).astype(int)
    return featured
