"""Demand projection scenarios through 2030."""

from __future__ import annotations

import pandas as pd


DEFAULT_SCENARIOS = {
    "Conservative": {
        "structural_growth_pct": 0.6,
        "ai_data_center_pct": 0.3,
        "electrification_pct": 0.4,
        "blockchain_pct": 0.0,
        "efficiency_offset_pct": -0.6,
    },
    "Base": {
        "structural_growth_pct": 1.0,
        "ai_data_center_pct": 0.8,
        "electrification_pct": 0.7,
        "blockchain_pct": 0.2,
        "efficiency_offset_pct": -0.5,
    },
    "Accelerated": {
        "structural_growth_pct": 1.5,
        "ai_data_center_pct": 1.6,
        "electrification_pct": 1.2,
        "blockchain_pct": 0.5,
        "efficiency_offset_pct": -0.3,
    },
}


def annual_demand_summary(demand: pd.DataFrame) -> pd.DataFrame:
    """Summarize hourly demand into annual average and annual peak demand."""
    df = demand.copy()
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["year"] = df["datetime"].dt.year
    return (
        df.groupby("year", as_index=False)
        .agg(avg_demand_mw=("demand_mw", "mean"), peak_demand_mw=("demand_mw", "max"))
        .sort_values("year")
    )


def build_demand_projection(
    demand: pd.DataFrame,
    start_year: int = 2026,
    end_year: int = 2030,
    scenarios: dict[str, dict[str, float]] | None = None,
) -> pd.DataFrame:
    """Build explainable demand scenarios from a historical demand anchor.

    This is a scenario model. It is designed for business planning discussion, not as a
    precise long-range hourly load forecast.
    """
    annual = annual_demand_summary(demand)
    if annual.empty:
        return pd.DataFrame()

    anchor = annual.iloc[-1]
    anchor_year = int(anchor["year"])
    scenarios = scenarios or DEFAULT_SCENARIOS
    rows = []
    for scenario_name, assumptions in scenarios.items():
        net_growth_pct = sum(assumptions.values())
        peak_extra_pct = assumptions["ai_data_center_pct"] * 0.35 + assumptions["blockchain_pct"] * 0.25
        peak_growth_pct = net_growth_pct + peak_extra_pct
        for year in range(start_year, end_year + 1):
            years_ahead = year - start_year + 1
            rows.append(
                {
                    "scenario": scenario_name,
                    "year": year,
                    "anchor_year": anchor_year,
                    "anchor_avg_demand_mw": anchor["avg_demand_mw"],
                    "anchor_peak_demand_mw": anchor["peak_demand_mw"],
                    "net_avg_growth_pct": net_growth_pct,
                    "net_peak_growth_pct": peak_growth_pct,
                    "projected_avg_demand_mw": anchor["avg_demand_mw"] * ((1 + net_growth_pct / 100) ** years_ahead),
                    "projected_peak_demand_mw": anchor["peak_demand_mw"] * ((1 + peak_growth_pct / 100) ** years_ahead),
                    **assumptions,
                }
            )
    return pd.DataFrame(rows)
