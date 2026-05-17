"""Nuclear capacity analytical summaries."""

import pandas as pd


def summarize_nuclear_capacity(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Aggregate capacity and reactor counts by useful business dimensions."""
    by_country = df.groupby("country", as_index=False).agg(
        capacity_mw=("capacity_mw", "sum"),
        reactor_count=("reactor_count", "sum"),
        annual_generation_gwh=("annual_generation_gwh", "sum"),
    ).sort_values("capacity_mw", ascending=False)
    by_region = df.groupby("region", as_index=False).agg(
        capacity_mw=("capacity_mw", "sum"),
        reactor_count=("reactor_count", "sum"),
        annual_generation_gwh=("annual_generation_gwh", "sum"),
    ).sort_values("capacity_mw", ascending=False)
    by_status = df.groupby("status", as_index=False).agg(
        reactor_count=("reactor_count", "sum"),
        capacity_mw=("capacity_mw", "sum"),
    ).sort_values("reactor_count", ascending=False)
    return {"by_country": by_country, "by_region": by_region, "by_status": by_status}


def build_nuclear_capacity_projection(df: pd.DataFrame, start_year: int = 2025, end_year: int = 2030) -> pd.DataFrame:
    """Build simple 2030 nuclear capacity scenarios from current and under-construction capacity.

    This is a planning scenario, not a deterministic forecast. It assumes existing operational
    capacity remains available and under-construction capacity is added gradually by 2030.
    """
    current = df[df["status"].str.contains("Operational|Restarting", case=False, na=False)]
    construction = df[df["status"].str.contains("Under Construction", case=False, na=False)]
    current_by_country = current.groupby(["country", "region"], as_index=False)["capacity_mw"].sum()
    construction_by_country = construction.groupby("country", as_index=False)["capacity_mw"].sum()
    merged = current_by_country.merge(
        construction_by_country,
        on="country",
        how="left",
        suffixes=("_current", "_under_construction"),
    ).fillna({"capacity_mw_under_construction": 0})

    years = list(range(start_year, end_year + 1))
    rows = []
    for _, row in merged.iterrows():
        for year in years:
            progress = (year - start_year) / max(end_year - start_year, 1)
            for scenario, multiplier in [("Low", 0.4), ("Base", 0.7), ("High", 1.0)]:
                added = row["capacity_mw_under_construction"] * progress * multiplier
                rows.append(
                    {
                        "country": row["country"],
                        "region": row["region"],
                        "year": year,
                        "scenario": scenario,
                        "projected_capacity_mw": row["capacity_mw_current"] + added,
                        "current_capacity_mw": row["capacity_mw_current"],
                        "under_construction_capacity_mw": row["capacity_mw_under_construction"],
                    }
                )
    return pd.DataFrame(rows)
