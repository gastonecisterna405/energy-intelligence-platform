"""Demand data cleaning."""

import pandas as pd


def clean_demand_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean timestamp, remove invalid records and enforce hourly ordering."""
    cleaned = df.copy()
    cleaned["datetime"] = pd.to_datetime(cleaned["datetime"], errors="coerce")
    cleaned["demand_mw"] = pd.to_numeric(cleaned["demand_mw"], errors="coerce")
    cleaned = cleaned.dropna(subset=["datetime", "demand_mw"])
    cleaned = cleaned[cleaned["demand_mw"] > 0]
    cleaned = cleaned.drop_duplicates(subset=["datetime"]).sort_values("datetime")
    cleaned = cleaned.set_index("datetime").asfreq("h")
    cleaned["demand_mw"] = cleaned["demand_mw"].interpolate("time").ffill().bfill()
    return cleaned.reset_index()
