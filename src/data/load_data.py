"""Data loading helpers for demand, nuclear and text inputs."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.config import DEMAND_RAW_CANDIDATES, MAX_DEMAND_ROWS, RAW_DATA_DIR, SAMPLE_DATA_DIR


def generate_sample_demand(periods: int = 24 * 180) -> pd.DataFrame:
    """Create a realistic hourly load sample used only when no raw CSV exists."""
    rng = np.random.default_rng(42)
    timestamps = pd.date_range("2022-01-01", periods=periods, freq="h")
    hour = timestamps.hour
    dayofyear = timestamps.dayofyear
    weekday = timestamps.dayofweek
    daily_shape = 2800 * np.sin((hour - 7) / 24 * 2 * np.pi) + 1800 * np.sin((hour - 17) / 24 * 2 * np.pi)
    seasonal = 4200 * np.sin((dayofyear - 20) / 365 * 2 * np.pi) ** 2
    weekday_effect = np.where(weekday < 5, 1200, -900)
    noise = rng.normal(0, 850, size=periods)
    demand = 33000 + daily_shape + seasonal + weekday_effect + noise
    return pd.DataFrame({"datetime": timestamps, "demand_mw": np.maximum(demand, 18000).round(2)})


def find_raw_demand_file(raw_dir: Path = RAW_DATA_DIR) -> Path | None:
    """Find a local PJM/EIA-style demand CSV if the user placed one in data/raw."""
    for file_name in DEMAND_RAW_CANDIDATES:
        candidate = raw_dir / file_name
        if candidate.exists():
            return candidate
    excluded = {"nuclear_capacity_sample.csv", "energy_text_comments.csv"}
    for csv_file in sorted(raw_dir.glob("*.csv")):
        if csv_file.name in excluded:
            continue
        try:
            header = pd.read_csv(csv_file, nrows=0).columns.str.lower().tolist()
        except Exception:
            continue
        if any("demand" in col or "load" in col or col in {"pjme_mw", "mw"} for col in header):
            return csv_file
    return None


def load_demand_data(raw_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """Load a real demand CSV when available; otherwise use a documented sample."""
    raw_path = find_raw_demand_file(raw_dir)
    if raw_path is None:
        sample = generate_sample_demand()
        SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)
        sample.to_csv(SAMPLE_DATA_DIR / "demand_sample.csv", index=False)
        return sample

    df = pd.read_csv(raw_path)
    normalized = normalize_demand_columns(df)
    if len(normalized) > MAX_DEMAND_ROWS:
        normalized = normalized.sort_values("datetime").tail(MAX_DEMAND_ROWS)
    return normalized


def normalize_demand_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize common PJM/EIA timestamp and demand column names."""
    lower_map = {col.lower().strip(): col for col in df.columns}
    datetime_col = next((lower_map[c] for c in lower_map if c in {"datetime", "timestamp", "date", "time"}), None)
    demand_col = next((col for col in df.columns if col.lower().strip() in {"demand_mw", "load_mw", "mw", "pjme_mw", "pjm_load_mw"}), None)

    if datetime_col is None:
        datetime_col = df.columns[0]
    if demand_col is None:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if not numeric_cols:
            raise ValueError("Demand CSV must contain at least one numeric demand/load column.")
        demand_col = numeric_cols[0]

    normalized = df[[datetime_col, demand_col]].copy()
    normalized.columns = ["datetime", "demand_mw"]
    normalized["datetime"] = pd.to_datetime(normalized["datetime"], errors="coerce")
    normalized["demand_mw"] = pd.to_numeric(normalized["demand_mw"], errors="coerce")
    return normalized


def load_nuclear_data(raw_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """Load IAEA-style nuclear capacity data or the included sample."""
    raw_path = raw_dir / "nuclear_capacity_sample.csv"
    if not raw_path.exists():
        create_nuclear_sample(raw_path)
    return pd.read_csv(raw_path)


def create_nuclear_sample(path: Path) -> None:
    """Create an IAEA PRIS/RDS-1 compatible sample schema for local demos."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        ("United States", "North America", "Operational", 93, 95600, 772000, 18.2),
        ("France", "Europe", "Operational", 56, 61370, 320400, 62.6),
        ("China", "Asia", "Operational", 56, 54000, 435000, 4.9),
        ("Russia", "Europe/Asia", "Operational", 37, 27700, 224000, 19.6),
        ("South Korea", "Asia", "Operational", 26, 25000, 176000, 30.4),
        ("Canada", "North America", "Operational", 19, 13600, 82000, 13.6),
        ("Japan", "Asia", "Restarting/Operational", 12, 11600, 61000, 7.5),
        ("India", "Asia", "Operational", 23, 7480, 48000, 3.1),
        ("United Kingdom", "Europe", "Operational", 9, 5880, 41000, 14.2),
        ("UAE", "Middle East", "Operational", 4, 5380, 32000, 19.7),
        ("China", "Asia", "Under Construction", 24, 26000, 0, 0.0),
        ("India", "Asia", "Under Construction", 8, 6800, 0, 0.0),
        ("Germany", "Europe", "Shutdown", 0, 0, 0, 0.0),
    ]
    pd.DataFrame(
        rows,
        columns=[
            "country",
            "region",
            "status",
            "reactor_count",
            "capacity_mw",
            "annual_generation_gwh",
            "nuclear_share_pct",
        ],
    ).to_csv(path, index=False)


def load_text_comments(raw_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """Load analyst comments or create a small synthetic text dataset."""
    path = raw_dir / "energy_text_comments.csv"
    if path.exists():
        return pd.read_csv(path)
    comments = [
        ("Peak demand is expected to increase during summer evenings.", "risk"),
        ("Nuclear baseload generation remains stable and supports system reliability.", "support"),
        ("High gas dependency may increase price volatility.", "risk"),
        ("Renewable intermittency requires flexible backup capacity.", "risk"),
        ("Demand response programs can reduce pressure during critical hours.", "mitigation"),
        ("Capacity additions improve resilience in high load periods.", "support"),
        ("Unexpected outages can create reliability concerns during heat waves.", "risk"),
        ("Long-term nuclear output provides predictable low-carbon baseload supply.", "support"),
    ]
    return pd.DataFrame(comments, columns=["comment", "label"])
