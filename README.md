# Energy Intelligence Platform: Demand Forecasting, Peak Risk Scoring & Nuclear Capacity Analytics

## Business Problem

Energy companies, utilities, grid operators and consultants need to forecast electricity demand, identify peak-risk periods, understand baseload capacity and communicate analytical results to decision makers.

This project provides an end-to-end Python analytics and machine learning platform for that workflow.

## Why This Project Matters

Demand forecasting affects procurement, grid reliability, demand response, maintenance scheduling and market strategy. Peak-risk scoring turns forecasts into an operational signal. Nuclear capacity analytics adds a strategic baseload perspective. Executive reporting and dashboards make the outputs usable for business stakeholders.

## Main Features

- Electricity demand forecasting with a statistical baseline and XGBoost-style regression.
- Peak demand risk classification with Low, Medium and High labels.
- 2030 demand scenario simulator with AI/data center, blockchain, electrification and efficiency assumptions.
- Nuclear capacity analytics by country, region and reactor status.
- SQL analytical layer with reusable business queries.
- Streamlit dashboard for decision-making.
- NLTK text analysis for energy comments and report snippets.
- Offline deterministic GenAI-style executive report generation.
- PySpark and Databricks-ready ETL examples.

## Data Sources

Demand data:
- Preferred: PJM hourly energy consumption CSV such as `PJME_hourly.csv` or `PJM_Load_hourly.csv`.
- Alternative: EIA or other hourly demand CSV with timestamp and demand/load columns.
- Place the file in `data/raw/`.
- To download a public PJM hourly load CSV mirror used for this demo:

```bash
python -m src.data.download_real_data
```

The loader supports common column names such as `Datetime`, `datetime`, `PJME_MW`, `demand_mw`, `load_mw` and `MW`.
If the real demand file contains many years of history, the local pipeline uses the latest three years for fast laptop execution while preserving the full raw CSV in `data/raw/`.

Nuclear data:
- `data/raw/nuclear_capacity_sample.csv` is an IAEA PRIS/RDS-1 style sample schema.
- Replace it with an official IAEA PRIS/RDS-1 export when available.
- The included sample is calibrated as a 2025/2026-style planning dataset and includes operational plus under-construction capacity so the project can build 2030 scenarios.

NLP data:
- Optional `data/raw/energy_text_comments.csv`.
- If missing, the project uses a small set of analyst-style sample comments.

## Architecture

Raw data flows through cleaning, feature engineering, forecasting, classification, nuclear analytics, SQL table creation, NLP analysis, executive reporting and Streamlit dashboarding. The Spark folder shows how the ETL pattern can scale in PySpark or Databricks.

## Repository Structure

```text
energy-intelligence-platform/
├── data/
├── notebooks/
├── src/
├── sql/
├── spark/
├── models/
├── outputs/
├── docs/
├── tests/
├── README.md
├── requirements.txt
└── run_pipeline.py
```

## Setup

```bash
cd energy-intelligence-platform
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the Full Pipeline

```bash
python run_pipeline.py
```

For real demand data, run this first:

```bash
python -m src.data.download_real_data
python run_pipeline.py
```

Expected outputs:
- `outputs/figures/*.png`
- `outputs/metrics/*.json` and SQL query CSVs
- `outputs/reports/executive_report.md`
- `models/*.joblib`
- `data/processed/*.csv`

## Run Individual Models

```bash
python -c "from src.data.make_dataset import build_processed_datasets; build_processed_datasets()"
python -c "import pandas as pd; from src.models.demand_forecasting_xgboost import train_xgboost_forecaster; train_xgboost_forecaster(pd.read_csv('data/processed/demand_features.csv'))"
```

## Exploratory Data Analysis

The main EDA notebook is:

```text
notebooks/01_data_exploration.ipynb
```

It includes data quality checks, missing values, distributions, time-series patterns, peak-risk investigation, outlier review, feature analysis, correlation analysis, lag diagnostics, time-based train/test split, a scikit-learn preprocessing pipeline, error analysis, feature importance, 2030 demand scenarios and nuclear capacity exploration.

## Run the Dashboard

```bash
streamlit run src/dashboard/app.py
```

Run `python run_pipeline.py` first so the dashboard has processed data, metrics and report artifacts.
The dashboard includes hover help on metrics and short explanations for each page.

## Modeling Approach

Demand forecasting:
- Exponential Smoothing baseline with hourly seasonality.
- XGBoost regressor using hour, day of week, month, weekend flag, demand lags and rolling averages.

Peak risk:
- High risk is demand above the 90th percentile.
- Medium risk is demand between the 75th and 90th percentiles.
- Low risk is all other periods.
- Logistic Regression is included as a baseline and Random Forest is used for the main classifier.

Nuclear capacity scenarios:
- Current operational capacity is treated as the 2025 base.
- Under-construction capacity is added gradually through 2030.
- Low, Base and High scenarios assume 40%, 70% and 100% of under-construction capacity is realized by 2030.
- These are planning scenarios, not guaranteed forecasts.

2030 demand scenarios:
- The dashboard includes an interactive scenario simulator.
- Users can adjust annual assumptions for structural demand growth, AI/data centers, electrification, blockchain/crypto load and efficiency offsets.
- The output is projected average demand and projected peak demand through 2030.
- This is a business planning tool, not a precise long-range hourly forecast.

## Metrics

Forecasting:
- MAE
- RMSE
- MAPE

Classification:
- Accuracy
- Macro precision
- Macro recall
- Macro F1
- Confusion matrix

## Results Summary

Results are generated locally because they depend on the dataset used. After running the pipeline, review:

- `outputs/metrics/demand_model_metrics.json`
- `outputs/metrics/peak_risk_metrics.json`
- `outputs/reports/executive_report.md`

The report summarizes forecast accuracy, high-risk periods, nuclear capacity insights and recommended actions.

## Generative AI Reporting

The report generator is offline by default. It behaves like a controlled GenAI reporting layer by converting structured metrics into executive language. It does not require an API key and does not make unverifiable claims.

The module can be extended later to call an approved LLM endpoint using an environment variable such as `OPENAI_API_KEY`.

## PySpark and Databricks Scalability

`spark/pyspark_etl.py` demonstrates SparkSession creation, raw CSV ingestion, cleaning, time feature creation, aggregation and Parquet output. `spark/databricks_notebook_template.py` shows the same workflow in Databricks notebook style, with comments for Delta table output.

## SQL Layer

The pipeline creates a SQLite database with:
- `demand_observations`
- `demand_forecasts`
- `peak_risk_scores`
- `nuclear_capacity`
- `nlp_comments`
- `model_metrics`

Reusable SQL files are stored in `sql/`, and query results are written to `outputs/metrics/`.

## Limitations

- Demand data comes from a public PJM historical dataset. It is useful for modeling demonstration, but not a live 2026 operating feed.
- Long-range demand to 2030 is modeled as scenarios because it depends on technology adoption, AI/data centers, electrification, efficiency, economic growth and policy.
- The bundled nuclear file is a documented IAEA-style 2025/2026 planning sample, not a live official PRIS export.
- 2030 nuclear capacity values are scenarios based on current and under-construction capacity, not exact predictions.
- Weather, holidays, outages and market prices are not included by default.
- Price-spike modeling is optional and should only be activated with real price data.

## Future Improvements

- Add weather and holiday features.
- Add electricity price and fuel market data.
- Track experiments with MLflow.
- Add drift monitoring and data quality checks.
- Deploy the dashboard against governed warehouse tables.
- Connect the report generator to an enterprise GenAI service.

## Interview Pitch

This project shows how I would approach a real energy analytics consulting problem: ingest demand data, engineer time-series features, forecast load, classify peak-risk periods, analyze nuclear baseload capacity, expose outputs through SQL and dashboards, and generate an executive report that business stakeholders can act on.
