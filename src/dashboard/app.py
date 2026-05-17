"""Streamlit dashboard for the Energy Intelligence Platform."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import METRICS_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR, REPORTS_DIR
from src.features.demand_scenarios import build_demand_projection


def _read_csv(name: str) -> pd.DataFrame:
    path = PROCESSED_DATA_DIR / name
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _source_label() -> str:
    if (RAW_DATA_DIR / "PJM_Load_hourly.csv").exists() or (RAW_DATA_DIR / "PJME_hourly.csv").exists():
        return "Real PJM hourly demand CSV"
    return "Offline sample demand data"


def _apply_style() -> None:
    st.markdown(
        """
        <style>
        .block-container {padding-top: 3rem; max-width: 1280px;}
        div[data-testid="stMetric"] {
            background: #151922;
            border: 1px solid #293241;
            border-radius: 8px;
            padding: 16px 18px;
        }
        div[data-testid="stMetricLabel"] {font-size: 0.95rem;}
        div[data-testid="stMetricValue"] {font-size: 2rem;}
        .explain-box {
            background: #111827;
            border: 1px solid #2f3a4a;
            border-radius: 8px;
            padding: 14px 16px;
            margin: 8px 0 18px 0;
            color: #d8dee9;
        }
        .small-note {color: #aab4c0; font-size: 0.92rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _explain(text: str) -> None:
    st.markdown(f"<div class='explain-box'>{text}</div>", unsafe_allow_html=True)


def _help_panel(title: str, what: str, variables: list[str], sources: list[str], decision: str) -> None:
    with st.expander(title, expanded=False):
        st.markdown(f"**Qué estás viendo:** {what}")
        st.markdown("**Variables:**")
        for variable in variables:
            st.markdown(f"- {variable}")
        st.markdown("**Fuentes:**")
        for source in sources:
            st.markdown(f"- {source}")
        st.markdown(f"**Para qué ayuda:** {decision}")
        st.markdown(
            "**Cómo usar el gráfico:** arrastrá el mouse formando un rectángulo para hacer zoom. "
            "Doble click para volver a la vista completa. Podés activar o desactivar series desde la leyenda."
        )


def _plotly_layout(fig: go.Figure, y_title: str) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        height=460,
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
        xaxis=dict(title="", rangeslider=dict(visible=False)),
        yaxis=dict(title=y_title),
    )
    fig.update_xaxes(showspikes=True)
    fig.update_yaxes(showspikes=True)
    return fig


def _line_chart(df: pd.DataFrame, x: str, y: str | list[str], title: str, y_title: str) -> None:
    fig = px.line(df, x=x, y=y, title=title, markers=False)
    fig = _plotly_layout(fig, y_title)
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "scrollZoom": True})


def _scenario_line_chart(df: pd.DataFrame, x: str, y: str, color: str, title: str, y_title: str) -> None:
    fig = px.line(df, x=x, y=y, color=color, title=title, markers=True)
    fig = _plotly_layout(fig, y_title)
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "scrollZoom": True})


def _bar_chart(df: pd.DataFrame, x: str, y: str, title: str, y_title: str, color: str | None = None) -> None:
    fig = px.bar(df, x=x, y=y, color=color, title=title)
    fig = _plotly_layout(fig, y_title)
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "scrollZoom": True})


def _metric_cards(demand: pd.DataFrame, risk: pd.DataFrame, demand_metrics: dict) -> None:
    cols = st.columns(5)
    cols[0].metric(
        "Observations",
        f"{len(demand):,}",
        help="Number of hourly demand records used by the dashboard after cleaning.",
    )
    cols[1].metric(
        "Avg demand MW",
        f"{demand.get('demand_mw', pd.Series(dtype=float)).mean():,.0f}",
        help="Average electricity demand in megawatts across the analyzed period.",
    )
    cols[2].metric(
        "Peak demand MW",
        f"{demand.get('demand_mw', pd.Series(dtype=float)).max():,.0f}",
        help="Highest hourly demand observed in the cleaned dataset.",
    )
    cols[3].metric(
        "XGB MAPE",
        f"{demand_metrics.get('xgboost', {}).get('mape', 0):.2f}%",
        help="Mean Absolute Percentage Error. Lower is better. It shows the average percentage forecasting error.",
    )
    cols[4].metric(
        "High-risk periods",
        f"{(risk.get('predicted_risk_label', pd.Series(dtype=str)) == 'High').sum():,}",
        help="Number of hours classified as High peak-risk by the scoring model.",
    )


def _prepare_datetime(df: pd.DataFrame, column: str = "datetime") -> pd.DataFrame:
    prepared = df.copy()
    if not prepared.empty and column in prepared.columns:
        prepared[column] = pd.to_datetime(prepared[column])
    return prepared


def _date_filter(df: pd.DataFrame, label: str) -> pd.DataFrame:
    if df.empty or "datetime" not in df.columns:
        return df
    min_date = df["datetime"].min().date()
    max_date = df["datetime"].max().date()
    selected = st.sidebar.date_input(label, value=(min_date, max_date), min_value=min_date, max_value=max_date)
    if isinstance(selected, tuple) and len(selected) == 2:
        start, end = selected
        return df[(df["datetime"].dt.date >= start) & (df["datetime"].dt.date <= end)]
    return df


def _custom_demand_projection(demand: pd.DataFrame) -> pd.DataFrame:
    st.subheader("Scenario assumptions", help="Move these assumptions to simulate different 2030 demand outcomes.")
    c1, c2 = st.columns(2)
    structural = c1.slider("Structural demand growth % per year", 0.0, 4.0, 1.0, 0.1, help="Population, economic activity and normal electricity demand growth.")
    ai = c1.slider("AI / data center growth % per year", 0.0, 5.0, 1.2, 0.1, help="Extra demand from AI compute, cloud infrastructure and data centers.")
    electrification = c2.slider("Electrification growth % per year", 0.0, 4.0, 0.8, 0.1, help="Extra demand from EVs, heat pumps, industrial electrification and new electric loads.")
    blockchain = c2.slider("Blockchain / crypto load % per year", 0.0, 3.0, 0.3, 0.1, help="Optional extra demand from energy-intensive blockchain or crypto mining activity.")
    efficiency = st.slider("Efficiency offset % per year", -3.0, 0.0, -0.6, 0.1, help="Demand reduction from efficiency, better equipment, smart grids and demand response.")
    scenarios = {
        "Custom": {
            "structural_growth_pct": structural,
            "ai_data_center_pct": ai,
            "electrification_pct": electrification,
            "blockchain_pct": blockchain,
            "efficiency_offset_pct": efficiency,
        }
    }
    return build_demand_projection(demand, scenarios=scenarios)


def main() -> None:
    st.set_page_config(page_title="Energy Intelligence Platform", layout="wide")
    _apply_style()

    st.sidebar.title("Energy Intelligence")
    st.sidebar.caption(f"Data source: {_source_label()}")
    page = st.sidebar.radio(
        "Dashboard pages",
        [
            "Executive Overview",
            "Demand Forecasting",
            "Peak Risk Scoring",
            "2030 Demand Scenarios",
            "Nuclear Capacity Analytics",
            "NLP Energy Text Insights",
            "Executive Report",
        ],
    )
    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Tip: hover over metric labels or chart titles when available. The help icons explain the business meaning."
    )

    demand = _prepare_datetime(_read_csv("demand_clean.csv"))
    forecasts = _prepare_datetime(_read_csv("demand_forecasts.csv"))
    risk = _prepare_datetime(_read_csv("peak_risk_scores.csv"))
    nuclear = _read_csv("nuclear_capacity.csv")
    nuclear_projection = _read_csv("nuclear_capacity_projection_2030.csv")
    demand_projection = _read_csv("demand_projection_2030.csv")
    comments = _read_csv("nlp_comments.csv")
    demand_metrics = _read_json(METRICS_DIR / "demand_model_metrics.json")
    risk_metrics = _read_json(METRICS_DIR / "peak_risk_metrics.json")

    st.title("Energy Intelligence Platform")
    st.caption("Demand forecasting, peak-risk scoring, nuclear capacity analytics and executive reporting.")

    if page == "Executive Overview":
        _explain(
            "This page answers the basic business question: how much electricity demand are we analyzing, "
            "how high did it get, how accurate is the demand model, and how many hours look risky?"
        )
        filtered_demand = _date_filter(demand, "Filter demand period")
        filtered_risk = risk[risk["datetime"].isin(filtered_demand["datetime"])] if not risk.empty else risk
        _metric_cards(filtered_demand, filtered_risk, demand_metrics)
        if not filtered_demand.empty:
            demand_plot = filtered_demand.copy()
            st.subheader("Hourly electricity demand", help="Line chart of demand over time. Peaks are hours when the grid needed more power.")
            _line_chart(demand_plot, "datetime", "demand_mw", "Hourly electricity demand", "Demand MW")
            _help_panel(
                "Qué estoy viendo en Executive Overview",
                "Una vista histórica de la demanda eléctrica horaria y los indicadores principales del período filtrado.",
                [
                    "`Observations`: cantidad de horas analizadas.",
                    "`Avg demand MW`: demanda promedio del período.",
                    "`Peak demand MW`: máximo consumo horario observado.",
                    "`XGB MAPE`: error porcentual promedio del modelo XGBoost.",
                    "`High-risk periods`: horas clasificadas como alto riesgo de pico.",
                ],
                ["PJM East hourly electricity demand CSV descargado en `data/raw/PJME_hourly.csv`."],
                "Sirve para entender la magnitud del sistema eléctrico, ver estacionalidad y detectar si el período elegido tiene más presión de demanda.",
            )

    elif page == "Demand Forecasting":
        _explain(
            "This page compares observed demand against the machine learning forecast. "
            "The goal is not only to predict demand, but to measure forecast error clearly."
        )
        if not forecasts.empty:
            filtered_forecasts = _date_filter(forecasts, "Filter forecast period")
            st.subheader("Actual vs predicted demand", help="Actual demand is what happened. Predicted demand is the model estimate.")
            forecast_plot = filtered_forecasts.rename(
                columns={"actual_demand_mw": "Actual demand MW", "predicted_demand_mw": "Predicted demand MW"}
            )
            _line_chart(forecast_plot, "datetime", ["Actual demand MW", "Predicted demand MW"], "Actual vs predicted demand", "Demand MW")
            _help_panel(
                "Qué estoy viendo en Demand Forecasting",
                "Una comparación entre la demanda real y la demanda estimada por el modelo.",
                [
                    "`Actual demand MW`: consumo real observado.",
                    "`Predicted demand MW`: estimación generada por el modelo.",
                    "`MAE`: error promedio en MW.",
                    "`RMSE`: error que penaliza más los errores grandes.",
                    "`MAPE`: error porcentual promedio.",
                ],
                ["PJM East hourly demand para entrenamiento y evaluación.", "Features de calendario, rezagos y medias móviles."],
                "Ayuda a evaluar si el modelo puede anticipar demanda con suficiente precisión para planificación operativa.",
            )
        cols = st.columns(3)
        xgb = demand_metrics.get("xgboost", {})
        cols[0].metric("MAE", f"{xgb.get('mae', 0):,.0f} MW", help="Average absolute error in megawatts.")
        cols[1].metric("RMSE", f"{xgb.get('rmse', 0):,.0f} MW", help="Error metric that penalizes large mistakes more heavily.")
        cols[2].metric("MAPE", f"{xgb.get('mape', 0):.2f}%", help="Average percentage error. Easier to explain to non-technical stakeholders.")
        st.dataframe(pd.DataFrame(demand_metrics).T, use_container_width=True)

    elif page == "Peak Risk Scoring":
        _explain(
            "This page converts demand behavior into a business-friendly risk signal. "
            "Low, Medium and High are based on demand percentiles, and the risk score ranges from 0 to 100."
        )
        if not risk.empty:
            filtered_risk = _date_filter(risk, "Filter risk period")
            left, right = st.columns([1, 2])
            with left:
                st.subheader("Risk distribution", help="How many forecast periods fall into each risk category.")
                risk_counts = (
                    filtered_risk["predicted_risk_label"]
                    .value_counts()
                    .reindex(["Low", "Medium", "High"])
                    .fillna(0)
                    .rename_axis("risk_label")
                    .reset_index(name="periods")
                )
                _bar_chart(risk_counts, "risk_label", "periods", "Risk distribution", "Periods", color="risk_label")
            with right:
                st.subheader("Highest-risk hours", help="Periods the model considers most likely to be peak-risk.")
                st.dataframe(filtered_risk.sort_values("risk_score", ascending=False).head(25), use_container_width=True)
            _help_panel(
                "Qué estoy viendo en Peak Risk Scoring",
                "Una clasificación de horas según riesgo de pico de demanda.",
                [
                    "`Low`: demanda esperada normal.",
                    "`Medium`: demanda elevada, por encima del percentil 75.",
                    "`High`: demanda crítica, cerca del percentil 90 o superior.",
                    "`risk_score`: probabilidad aproximada de estar en alto riesgo, de 0 a 100.",
                ],
                ["Demanda PJM procesada.", "Modelo Random Forest entrenado con variables de tiempo, rezagos y medias móviles."],
                "Ayuda a priorizar horas donde conviene activar monitoreo, respuesta de demanda, compras o capacidad flexible.",
            )
        cols = st.columns(4)
        cols[0].metric("Accuracy", f"{risk_metrics.get('accuracy', 0):.3f}", help="Share of periods classified correctly.")
        cols[1].metric("Precision", f"{risk_metrics.get('precision_macro', 0):.3f}", help="How reliable the predicted classes are.")
        cols[2].metric("Recall", f"{risk_metrics.get('recall_macro', 0):.3f}", help="How well the model finds each actual risk class.")
        cols[3].metric("F1", f"{risk_metrics.get('f1_macro', 0):.3f}", help="Balanced score combining precision and recall.")

    elif page == "2030 Demand Scenarios":
        _explain(
            "This page is the forward-looking business story. It does not claim to know the future exactly. "
            "It lets you test how demand could evolve by 2030 under assumptions about AI/data centers, blockchain, electrification, "
            "normal growth and efficiency."
        )
        if not demand.empty:
            custom_projection = _custom_demand_projection(demand)
            default_projection = demand_projection.copy()
            if not default_projection.empty:
                st.subheader("Default scenarios to 2030", help="Conservative, Base and Accelerated scenarios generated by the pipeline.")
                default_plot = default_projection.rename(
                    columns={"projected_peak_demand_mw": "Projected peak demand MW", "scenario": "Scenario"}
                )
                _scenario_line_chart(
                    default_plot,
                    "year",
                    "Projected peak demand MW",
                    "Scenario",
                    "Default 2030 peak demand scenarios",
                    "Peak demand MW",
                )

            st.subheader("Custom 2030 result", help="Projected average and peak demand under the assumptions selected above.")
            if not custom_projection.empty:
                result_2030 = custom_projection[custom_projection["year"] == 2030].iloc[0]
                net_growth = result_2030["net_avg_growth_pct"]
                peak_growth = result_2030["net_peak_growth_pct"]
                cols = st.columns(4)
                cols[0].metric("Projected avg demand 2030", f"{result_2030['projected_avg_demand_mw']:,.0f} MW")
                cols[1].metric("Projected peak demand 2030", f"{result_2030['projected_peak_demand_mw']:,.0f} MW")
                cols[2].metric("Net avg growth", f"{net_growth:.1f}% / year")
                cols[3].metric("Net peak growth", f"{peak_growth:.1f}% / year")
                custom_plot = custom_projection.rename(
                    columns={
                        "projected_avg_demand_mw": "Average demand MW",
                        "projected_peak_demand_mw": "Peak demand MW",
                    }
                )
                _line_chart(custom_plot, "year", ["Average demand MW", "Peak demand MW"], "Custom demand projection to 2030", "Demand MW")
                _help_panel(
                    "Qué estoy viendo en 2030 Demand Scenarios",
                    "Un simulador de escenarios. No es una predicción exacta: muestra cómo cambiaría la demanda si se cumplen ciertos supuestos.",
                    [
                        "`Structural demand growth`: crecimiento normal por población, economía e industria.",
                        "`AI / data centers`: demanda adicional por IA, cloud y centros de datos.",
                        "`Electrification`: demanda adicional por autos eléctricos, bombas de calor e industria electrificada.",
                        "`Blockchain / crypto load`: cargas intensivas opcionales de minería o blockchain.",
                        "`Efficiency offset`: reducción por eficiencia, smart grids y respuesta de demanda.",
                        "`Projected avg demand`: demanda promedio esperada.",
                        "`Projected peak demand`: máxima demanda que el sistema debería poder cubrir.",
                    ],
                    ["Demanda histórica PJM como punto de partida.", "Supuestos editables definidos en el dashboard."],
                    "Ayuda a discutir planeamiento 2030: cuánta capacidad, red, contratos o generación flexible podría necesitarse.",
                )
                st.dataframe(custom_projection, use_container_width=True)

    elif page == "Nuclear Capacity Analytics":
        _explain(
            "This page is strategic planning context. It shows how nuclear capacity contributes stable baseload supply "
            "by country, region and reactor status. The 2030 view is a scenario based on current and under-construction capacity, not a guaranteed forecast."
        )
        if not nuclear.empty:
            by_country = nuclear.groupby("country")["capacity_mw"].sum().sort_values(ascending=False).head(15)
            by_region = nuclear.groupby("region")["capacity_mw"].sum().sort_values(ascending=False)
            by_status = nuclear.groupby("status")["reactor_count"].sum().sort_values(ascending=False)
            c1, c2 = st.columns(2)
            c1.subheader("Capacity by country", help="Installed nuclear capacity in megawatts by country.")
            c1.plotly_chart(
                _plotly_layout(px.bar(by_country.reset_index(), x="country", y="capacity_mw", title="Capacity by country"), "Capacity MW"),
                use_container_width=True,
                config={"displaylogo": False, "scrollZoom": True},
            )
            c2.subheader("Capacity by region", help="Regional comparison of installed nuclear capacity.")
            c2.plotly_chart(
                _plotly_layout(px.bar(by_region.reset_index(), x="region", y="capacity_mw", title="Capacity by region"), "Capacity MW"),
                use_container_width=True,
                config={"displaylogo": False, "scrollZoom": True},
            )
            st.subheader("Reactors by status", help="Operational, under construction, shutdown or related status.")
            status_df = by_status.rename_axis("status").reset_index(name="reactor_count")
            _bar_chart(status_df, "status", "reactor_count", "Reactors by status", "Reactors")
            if not nuclear_projection.empty:
                st.subheader("Capacity scenarios to 2030", help="Scenario view: Low, Base and High assumptions for how much under-construction capacity is added by 2030.")
                projection_plot = (
                    nuclear_projection.groupby(["year", "scenario"], as_index=False)["projected_capacity_mw"].sum()
                    .rename(columns={"scenario": "Scenario", "projected_capacity_mw": "Projected capacity MW"})
                )
                fig = px.line(projection_plot, x="year", y="Projected capacity MW", color="Scenario", title="Nuclear capacity scenarios to 2030")
                st.plotly_chart(_plotly_layout(fig, "Capacity MW"), use_container_width=True, config={"displaylogo": False, "scrollZoom": True})
                _help_panel(
                    "Qué estoy viendo en Nuclear Capacity Analytics",
                    "Capacidad nuclear instalada y escenarios de capacidad hacia 2030.",
                    [
                        "`capacity_mw`: potencia nuclear instalada.",
                        "`reactor_count`: cantidad de reactores.",
                        "`status`: operativo, en construcción o cerrado.",
                        "`Low/Base/High`: supuestos de cuánto de la capacidad en construcción entra en operación hacia 2030.",
                    ],
                    ["Archivo IAEA-style `data/raw/nuclear_capacity_sample.csv`.", "Estructura preparada para reemplazar por PRIS/RDS-1 oficial."],
                    "Ayuda a discutir cuánta capacidad firme de base podría apoyar el sistema frente a crecimiento de demanda.",
                )
            st.dataframe(nuclear, use_container_width=True)

    elif page == "NLP Energy Text Insights":
        _explain(
            "This page shows how unstructured analyst comments can become structured signals: keywords, themes and a simple sentiment-style score."
        )
        top_terms_path = METRICS_DIR / "nlp_top_terms.csv"
        top_terms = pd.read_csv(top_terms_path) if top_terms_path.exists() else pd.DataFrame()
        if not top_terms.empty:
            st.subheader("Most frequent energy terms", help="Common words after tokenization, lowercasing and stopword removal.")
            _bar_chart(top_terms, "term", "frequency", "Most frequent energy terms", "Frequency")
            _help_panel(
                "Qué estoy viendo en NLP Energy Text Insights",
                "Una transformación simple de comentarios de analistas en palabras frecuentes y señales textuales.",
                [
                    "`term`: palabra relevante después de limpiar el texto.",
                    "`frequency`: cantidad de apariciones.",
                    "`label`: categoría manual del comentario, por ejemplo risk, support o mitigation.",
                ],
                ["Comentarios energéticos sintéticos o `data/raw/energy_text_comments.csv` si se agrega uno real."],
                "Ayuda a mostrar cómo comentarios no estructurados pueden resumirse para reportes ejecutivos.",
            )
        st.subheader("Source comments")
        st.dataframe(comments, use_container_width=True)

    elif page == "Executive Report":
        _explain(
            "This page is the business narrative generated from the model outputs. "
            "It is deterministic by default, so it works offline without an API key."
        )
        report_path = REPORTS_DIR / "executive_report.md"
        st.markdown(report_path.read_text(encoding="utf-8") if report_path.exists() else "Run the pipeline to generate the report.")
        st.button("Regenerate report", disabled=True, help="Run python run_pipeline.py to regenerate report artifacts.")


if __name__ == "__main__":
    main()
