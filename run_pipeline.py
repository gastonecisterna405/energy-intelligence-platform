"""Run the full Energy Intelligence Platform pipeline."""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("outputs") / ".matplotlib"))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.config import FIGURES_DIR, METRICS_DIR, PROCESSED_DATA_DIR
from src.data.make_dataset import build_processed_datasets
from src.features.demand_scenarios import annual_demand_summary, build_demand_projection
from src.features.nuclear_features import build_nuclear_capacity_projection, summarize_nuclear_capacity
from src.models.demand_forecasting_statsmodels import train_statsmodels_baseline
from src.models.demand_forecasting_xgboost import train_xgboost_forecaster
from src.models.model_evaluation import save_json
from src.models.peak_risk_classifier import train_peak_risk_classifier
from src.nlp.energy_text_analysis import analyze_energy_text
from src.reports.generate_executive_report import generate_executive_report
from src.sql.build_database import build_sqlite_database
from src.sql.run_business_queries import run_business_queries


def _save_line_plot(df: pd.DataFrame, x: str, y: str, title: str, path) -> None:
    plt.figure(figsize=(12, 5))
    sns.lineplot(data=df, x=x, y=y)
    plt.title(title)
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def save_figures(demand: pd.DataFrame, forecasts: pd.DataFrame, risk: pd.DataFrame, nuclear_summary: dict, nlp_terms: pd.DataFrame) -> None:
    """Create expected visual outputs."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    _save_line_plot(demand.tail(24 * 30), "datetime", "demand_mw", "Demand Time Series", FIGURES_DIR / "demand_time_series.png")

    plt.figure(figsize=(12, 5))
    plot_forecast = forecasts.tail(24 * 14)
    plt.plot(pd.to_datetime(plot_forecast["datetime"]), plot_forecast["actual_demand_mw"], label="Actual")
    plt.plot(pd.to_datetime(plot_forecast["datetime"]), plot_forecast["predicted_demand_mw"], label="Predicted")
    plt.title("Actual vs Predicted Demand")
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "actual_vs_predicted_demand.png")
    plt.close()

    plt.figure(figsize=(8, 5))
    sns.countplot(data=risk, x="predicted_risk_label", order=["Low", "Medium", "High"])
    plt.title("Peak Risk Distribution")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "peak_risk_distribution.png")
    plt.close()

    plt.figure(figsize=(10, 5))
    sns.barplot(data=nuclear_summary["by_country"].head(10), x="capacity_mw", y="country")
    plt.title("Nuclear Capacity by Country")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "nuclear_capacity_by_country.png")
    plt.close()

    plt.figure(figsize=(9, 5))
    sns.barplot(data=nuclear_summary["by_region"], x="capacity_mw", y="region")
    plt.title("Nuclear Capacity by Region")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "nuclear_capacity_by_region.png")
    plt.close()

    plt.figure(figsize=(10, 5))
    sns.barplot(data=nlp_terms.head(15), x="frequency", y="term")
    plt.title("NLP Top Energy Terms")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "nlp_top_terms.png")
    plt.close()


def main() -> None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    print("[1/9] Loading raw demand data...")
    print("[2/9] Cleaning data...")
    print("[3/9] Building time features...")
    datasets = build_processed_datasets()
    demand = datasets["demand"]
    demand_features = datasets["demand_features"]
    nuclear = datasets["nuclear"]
    comments = datasets["comments"]

    print("[4/9] Training demand forecasting model...")
    annual_demand_summary(demand).to_csv(PROCESSED_DATA_DIR / "annual_demand_summary.csv", index=False)
    demand_projection = build_demand_projection(demand)
    demand_projection.to_csv(PROCESSED_DATA_DIR / "demand_projection_2030.csv", index=False)
    stats_forecast, stats_metrics = train_statsmodels_baseline(demand)
    xgb_forecast, xgb_metrics, _ = train_xgboost_forecaster(demand_features)
    xgb_forecast.to_csv(PROCESSED_DATA_DIR / "demand_forecasts.csv", index=False)
    demand_metrics = {"statsmodels": stats_metrics, "xgboost": xgb_metrics}
    save_json(demand_metrics, METRICS_DIR / "demand_model_metrics.json")

    print("[5/9] Training peak risk classifier...")
    risk_scores, risk_metrics, _ = train_peak_risk_classifier(demand_features)
    risk_scores.to_csv(PROCESSED_DATA_DIR / "peak_risk_scores.csv", index=False)
    save_json(risk_metrics, METRICS_DIR / "peak_risk_metrics.json")

    print("[6/9] Running nuclear analytics...")
    nuclear_summary = summarize_nuclear_capacity(nuclear)
    for name, frame in nuclear_summary.items():
        frame.to_csv(PROCESSED_DATA_DIR / f"nuclear_{name}.csv", index=False)
    nuclear_projection = build_nuclear_capacity_projection(nuclear)
    nuclear_projection.to_csv(PROCESSED_DATA_DIR / "nuclear_capacity_projection_2030.csv", index=False)

    print("[7/9] Building SQL database...")
    model_metrics = pd.DataFrame(
        [
            {"model": "statsmodels_baseline", **stats_metrics},
            {"model": "xgboost_demand_model", **xgb_metrics},
            {"model": "peak_risk_classifier", "f1_macro": risk_metrics["f1_macro"], "accuracy": risk_metrics["accuracy"]},
        ]
    )
    model_metrics.to_csv(PROCESSED_DATA_DIR / "model_metrics.csv", index=False)
    db_path = build_sqlite_database()
    run_business_queries(db_path)

    print("[8/9] Running NLP analysis...")
    nlp_results = analyze_energy_text(comments)
    top_terms = nlp_results["top_terms"]
    top_terms.to_csv(METRICS_DIR / "nlp_top_terms.csv", index=False)
    save_json(
        {
            "sentiment_score": nlp_results["sentiment_score"],
            "positive_term_hits": nlp_results["positive_term_hits"],
            "negative_term_hits": nlp_results["negative_term_hits"],
        },
        METRICS_DIR / "nlp_summary.json",
    )

    save_figures(demand, xgb_forecast, risk_scores, nuclear_summary, top_terms)

    print("[9/9] Generating executive report...")
    context = {
        "demand_metrics": demand_metrics,
        "risk_metrics": risk_metrics,
        "nuclear_summary": nuclear_summary,
        "nuclear_projection": nuclear_projection,
        "demand_projection": demand_projection,
        "top_terms": top_terms,
        "high_risk_count": int((risk_scores["predicted_risk_label"] == "High").sum()),
    }
    generate_executive_report(context)
    print("Pipeline complete. Outputs are available in outputs/, models/ and data/processed/.")


if __name__ == "__main__":
    main()
