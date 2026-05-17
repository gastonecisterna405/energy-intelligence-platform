"""Build SQLite database from processed project outputs."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from src.config import OUTPUTS_DIR, PROCESSED_DATA_DIR


def build_sqlite_database(db_path: Path | None = None) -> Path:
    """Create SQLite analytical tables from CSV outputs."""
    db_path = db_path or OUTPUTS_DIR / "energy_intelligence.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    table_files = {
        "demand_observations": PROCESSED_DATA_DIR / "demand_clean.csv",
        "demand_forecasts": PROCESSED_DATA_DIR / "demand_forecasts.csv",
        "peak_risk_scores": PROCESSED_DATA_DIR / "peak_risk_scores.csv",
        "nuclear_capacity": PROCESSED_DATA_DIR / "nuclear_capacity.csv",
        "nlp_comments": PROCESSED_DATA_DIR / "nlp_comments.csv",
        "model_metrics": PROCESSED_DATA_DIR / "model_metrics.csv",
    }
    for table, path in table_files.items():
        if path.exists():
            pd.read_csv(path).to_sql(table, conn, if_exists="replace", index=False)
    conn.close()
    return db_path
