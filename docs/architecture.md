# Architecture

The project is organized as a small production-style analytics platform.

1. `src/data` loads raw demand, nuclear and text data, then writes clean CSVs to `data/processed`.
2. `src/features` creates time, lag, rolling and nuclear aggregation features.
3. `src/models` trains a statistical demand baseline, an XGBoost-style regressor and a peak-risk classifier.
4. `src/sql` builds a SQLite analytical layer and runs business queries.
5. `src/nlp` converts unstructured energy comments into keyword and sentiment-style indicators.
6. `src/reports` generates an offline executive report from model outputs.
7. `src/dashboard/app.py` serves the Streamlit decision dashboard.
8. `spark/` shows how the ETL logic can scale in PySpark or Databricks.

The default pipeline is deterministic and runs offline. Real PJM/EIA demand data can be added to `data/raw/`.
