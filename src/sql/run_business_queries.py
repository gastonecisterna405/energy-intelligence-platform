"""Execute business SQL queries and save their results."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from src.config import METRICS_DIR, OUTPUTS_DIR

BUSINESS_QUERIES = {
    "average_demand_by_month": """
        SELECT substr(datetime, 1, 7) AS month, AVG(demand_mw) AS avg_demand_mw
        FROM demand_observations GROUP BY month ORDER BY month
    """,
    "peak_demand_periods": """
        SELECT datetime, demand_mw FROM demand_observations
        ORDER BY demand_mw DESC LIMIT 20
    """,
    "high_risk_days": """
        SELECT substr(datetime, 1, 10) AS day, COUNT(*) AS high_risk_hours
        FROM peak_risk_scores WHERE predicted_risk_label = 'High'
        GROUP BY day ORDER BY high_risk_hours DESC
    """,
    "nuclear_capacity_by_country": """
        SELECT country, SUM(capacity_mw) AS capacity_mw
        FROM nuclear_capacity GROUP BY country ORDER BY capacity_mw DESC
    """,
    "forecast_error_by_period": """
        SELECT datetime, actual_demand_mw, predicted_demand_mw,
               ABS(actual_demand_mw - predicted_demand_mw) AS absolute_error_mw
        FROM demand_forecasts ORDER BY datetime
    """,
}


def run_business_queries(db_path: Path | None = None) -> pd.DataFrame:
    """Run built-in executive queries and save one combined CSV."""
    db_path = db_path or OUTPUTS_DIR / "energy_intelligence.db"
    rows = []
    conn = sqlite3.connect(db_path)
    for name, query in BUSINESS_QUERIES.items():
        result = pd.read_sql_query(query, conn)
        result.to_csv(METRICS_DIR / f"{name}.csv", index=False)
        rows.append({"query_name": name, "row_count": len(result)})
    conn.close()
    summary = pd.DataFrame(rows)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    summary.to_csv(METRICS_DIR / "sql_query_results.csv", index=False)
    return summary
