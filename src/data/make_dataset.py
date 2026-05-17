"""Build processed datasets used by models, SQL and dashboard."""

import pandas as pd

from src.config import PROCESSED_DATA_DIR
from src.data.clean_demand_data import clean_demand_data
from src.data.clean_nuclear_data import clean_nuclear_data
from src.data.load_data import load_demand_data, load_nuclear_data, load_text_comments
from src.features.lag_features import add_lag_features
from src.features.time_features import add_time_features


def build_processed_datasets() -> dict[str, pd.DataFrame]:
    """Create processed demand, nuclear and text datasets."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    demand = clean_demand_data(load_demand_data())
    demand_features = add_lag_features(add_time_features(demand), target_col="demand_mw")
    nuclear = clean_nuclear_data(load_nuclear_data())
    comments = load_text_comments()

    demand.to_csv(PROCESSED_DATA_DIR / "demand_clean.csv", index=False)
    demand_features.to_csv(PROCESSED_DATA_DIR / "demand_features.csv", index=False)
    nuclear.to_csv(PROCESSED_DATA_DIR / "nuclear_capacity.csv", index=False)
    comments.to_csv(PROCESSED_DATA_DIR / "nlp_comments.csv", index=False)
    return {"demand": demand, "demand_features": demand_features, "nuclear": nuclear, "comments": comments}
