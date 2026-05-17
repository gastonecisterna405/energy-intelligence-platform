# Deployment

## Streamlit Community Cloud

Recommended app path:

```text
src/dashboard/app.py
```

The dashboard reads prepared artifacts from:

- `data/processed/`
- `outputs/metrics/`
- `outputs/reports/`

Before pushing a refreshed version, run:

```bash
python -m src.data.download_real_data
python run_pipeline.py
python -m pytest
```

## PySpark

PySpark is optional for deployment. The dashboard does not need it.

Install Spark support locally only when needed:

```bash
pip install -r requirements-spark.txt
python spark/pyspark_etl.py
```
