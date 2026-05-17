"""Download real public PJM hourly demand data for the project demo."""

from __future__ import annotations

import urllib.request

from src.config import PJM_LOAD_GITHUB_URL, RAW_DATA_DIR


def download_pjm_hourly_load() -> None:
    """Download a public PJM hourly load CSV mirror into data/raw."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RAW_DATA_DIR / "PJME_hourly.csv"
    metadata_path = RAW_DATA_DIR / "demand_data_source.txt"
    print(f"Downloading PJM hourly load data from {PJM_LOAD_GITHUB_URL}")
    urllib.request.urlretrieve(PJM_LOAD_GITHUB_URL, output_path)
    metadata_path.write_text(
        "Demand dataset: PJM East hourly energy consumption data.\n"
        "Original context: PJM hourly energy consumption dataset.\n"
        f"Downloaded mirror URL: {PJM_LOAD_GITHUB_URL}\n"
        "Place an updated PJM/EIA CSV in data/raw/ to replace this file.\n",
        encoding="utf-8",
    )
    print(f"Saved real demand data to {output_path}")


if __name__ == "__main__":
    download_pjm_hourly_load()
