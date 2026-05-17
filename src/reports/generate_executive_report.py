"""Offline-first executive report generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import REPORTS_DIR
from src.reports.report_templates import REPORT_TEMPLATE


def mock_genai_report(context: dict) -> str:
    """Generate deterministic GenAI-style business narrative from structured outputs."""
    demand_metrics = context.get("demand_metrics", {})
    risk_metrics = context.get("risk_metrics", {})
    nuclear_summary = context.get("nuclear_summary", {})
    nuclear_projection = context.get("nuclear_projection", pd.DataFrame())
    demand_projection = context.get("demand_projection", pd.DataFrame())
    top_terms = context.get("top_terms", pd.DataFrame())
    high_risk_count = context.get("high_risk_count", 0)

    best_mape = demand_metrics.get("xgboost", {}).get("mape", 0)
    baseline_mape = demand_metrics.get("statsmodels", {}).get("mape", 0)
    top_country = "not available"
    if nuclear_summary.get("by_country") is not None and not nuclear_summary["by_country"].empty:
        top_country = nuclear_summary["by_country"].iloc[0]["country"]
    terms = ", ".join(top_terms["term"].head(6).tolist()) if not top_terms.empty else "demand, risk, reliability"
    base_2030 = 0
    if not nuclear_projection.empty:
        base_2030 = nuclear_projection[
            (nuclear_projection["scenario"] == "Base") & (nuclear_projection["year"] == nuclear_projection["year"].max())
        ]["projected_capacity_mw"].sum()
    demand_peak_2030 = 0
    if not demand_projection.empty:
        base_demand_2030 = demand_projection[
            (demand_projection["scenario"] == "Base") & (demand_projection["year"] == demand_projection["year"].max())
        ]
        if not base_demand_2030.empty:
            demand_peak_2030 = base_demand_2030.iloc[0]["projected_peak_demand_mw"]

    return REPORT_TEMPLATE.format(
        executive_summary=(
            f"The platform forecasts electricity demand, scores peak-risk periods and connects these results "
            f"to nuclear capacity analytics. The tree-based demand model achieved a MAPE of {best_mape:.2f}% "
            f"versus {baseline_mape:.2f}% for the statistical baseline. The current scoring output identifies "
            f"{high_risk_count} high-risk periods in the test horizon. The Base demand scenario estimates a "
            f"2030 peak demand of approximately {demand_peak_2030:,.0f} MW."
        ),
        key_findings=(
            f"- Peak-risk periods concentrate where demand features show elevated recent load and seasonal pressure.\n"
            f"- Nuclear capacity analysis shows {top_country} as the largest capacity contributor in the sample.\n"
            f"- Base nuclear capacity scenario reaches approximately {base_2030:,.0f} MW by 2030 in the covered countries.\n"
            f"- Analyst text keywords highlight: {terms}."
        ),
        model_results=(
            f"- Forecasting metrics: MAE {demand_metrics.get('xgboost', {}).get('mae', 0):,.0f} MW, "
            f"RMSE {demand_metrics.get('xgboost', {}).get('rmse', 0):,.0f} MW, "
            f"MAPE {best_mape:.2f}%.\n"
            f"- Peak-risk classifier macro F1: {risk_metrics.get('f1_macro', 0):.3f}.\n"
            f"- Outputs are saved for SQL, dashboarding and stakeholder reporting."
        ),
        business_implications=(
            "Forecasts support operational planning, procurement timing and demand-response decisions. "
            "Peak-risk scores translate technical demand predictions into an action-oriented signal for business users. "
            "Nuclear analytics adds a baseload-capacity view for strategic planning, especially when discussing 2030 capacity scenarios."
        ),
        recommended_actions=(
            "- Review high-risk windows before weekly operations meetings.\n"
            "- Pair forecasts with weather and outage data in a production version.\n"
            "- Use nuclear capacity summaries and 2030 scenarios when discussing baseload reliability and long-term supply strategy."
        ),
        limitations=(
            "The bundled nuclear dataset is a documented IAEA-style sample unless replaced with a current PRIS/RDS-1 export. "
            "The offline demand sample is for demonstration only; production use should ingest verified PJM/EIA data. "
            "The default report generator is deterministic and does not call an external GenAI API."
        ),
        next_steps=(
            "Add weather, holiday, outage and market-price features; schedule the pipeline in Databricks; "
            "monitor model drift; and connect the report generator to an approved enterprise LLM endpoint."
        ),
    )


def generate_executive_report(context: dict, output_path: Path | None = None) -> str:
    """Write an executive report to outputs/reports/executive_report.md."""
    report = mock_genai_report(context)
    output_path = output_path or REPORTS_DIR / "executive_report.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    return report
