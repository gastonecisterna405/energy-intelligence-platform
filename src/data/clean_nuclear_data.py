"""Nuclear capacity data cleaning."""

import pandas as pd


def clean_nuclear_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize IAEA-style nuclear capacity fields."""
    cleaned = df.copy()
    text_cols = ["country", "region", "status"]
    for col in text_cols:
        cleaned[col] = cleaned[col].astype(str).str.strip()
    numeric_cols = ["reactor_count", "capacity_mw", "annual_generation_gwh", "nuclear_share_pct"]
    for col in numeric_cols:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce").fillna(0)
    return cleaned
