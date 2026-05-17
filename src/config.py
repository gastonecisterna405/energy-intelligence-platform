"""Project configuration and relative paths."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
METRICS_DIR = OUTPUTS_DIR / "metrics"
REPORTS_DIR = OUTPUTS_DIR / "reports"
SQL_DIR = PROJECT_ROOT / "sql"

DEMAND_RAW_CANDIDATES = [
    "PJME_hourly.csv",
    "PJM_Load_hourly.csv",
    "demand.csv",
    "electricity_demand.csv",
]

RANDOM_STATE = 42
TEST_SIZE_FRACTION = 0.2
MAX_DEMAND_ROWS = 24 * 365 * 3
PJM_LOAD_GITHUB_URL = "https://raw.githubusercontent.com/analyticsbyted/time_series_forecasting/main/PJME_hourly.csv"
