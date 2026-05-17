# Interview Project Brief

## Simple Explanation

This project is an energy analytics platform. It forecasts electricity demand, identifies periods with high peak-risk, analyzes nuclear capacity as baseload supply, summarizes analyst comments with NLP, and generates an executive report for business stakeholders.

## 30-Second Pitch

I built an end-to-end energy intelligence platform that turns hourly electricity demand data into forecasts, peak-risk scores, SQL tables, dashboard views and executive reporting. It combines time-series forecasting, XGBoost-style machine learning, risk classification, nuclear capacity analytics, NLP and a mock GenAI report generator. The goal is to show how a data science consultant can move from raw data to business decisions.

## 2-Minute Pitch

The project starts with electricity demand data, preferably PJM hourly consumption data. The repository includes a downloader for a public PJM hourly load CSV mirror, and the pipeline can also ingest manually placed PJM/EIA files. It cleans the data, creates time-based, lag and rolling features, then trains two forecasting models: a statistical baseline and a tree-based ML model. It evaluates both using MAE, RMSE and MAPE. For longer-term planning, the nuclear module adds 2025-2030 capacity scenarios using current and under-construction capacity.

On top of the forecast features, the project defines peak-risk classes based on demand percentiles. A classifier predicts Low, Medium or High risk and produces a 0-100 score that business users can understand.

The platform also includes nuclear capacity analytics using an IAEA-style schema. This shows how nuclear baseload capacity supports reliability and strategic planning. A SQL layer creates business-ready tables and queries. A Streamlit dashboard presents the outputs, and an NLP module extracts themes from energy analyst comments. Finally, a deterministic GenAI-style report generator turns structured metrics into an executive summary.

## Technical Explanation

The pipeline uses pandas for ingestion, cleaning and feature engineering. Forecasting is handled by Exponential Smoothing and XGBoost regression. Peak risk uses a percentile labeling rule and a Random Forest classifier with a Logistic Regression baseline. Results are stored as CSV, joblib model files, SQLite tables, JSON metrics and PNG charts. PySpark scripts show how the ETL can scale in Databricks.

## Business Explanation

The business value is decision support. Forecasts help plan operations and procurement. Peak-risk scores help prioritize high-load windows. The 2030 demand scenario simulator helps leaders discuss how AI/data centers, blockchain, electrification and efficiency could change future peak demand. Nuclear analytics supports baseload planning. NLP summarizes qualitative analyst commentary. The executive report translates model results into actions, limitations and next steps.

## Why This Fits the Job Description

It demonstrates forecasting, scoring, pricing-readiness, SQL, dashboarding, reporting, PySpark/Databricks awareness, NLP and GenAI-style communication. It is structured like a consulting deliverable: technical enough for data scientists, but clear enough for business stakeholders.

## Mapping to Requirements

- Forecasting: demand forecasting models.
- Scoring: peak-risk classifier and 0-100 risk score.
- Strategic planning: interactive 2030 demand and nuclear capacity scenarios.
- Dashboards: Streamlit app.
- SQL: SQLite database and business query scripts.
- PySpark/Databricks: Spark ETL and notebook template.
- NLP: NLTK tokenization, stopword removal and keyword analysis.
- Generative AI: deterministic executive report generator.
- Reporting: README, model card and executive report.

## Model Explanations

Demand forecasting model: predicts future electricity demand using historical hourly patterns.

XGBoost model: uses calendar, lag and rolling demand features to capture nonlinear demand behavior.

2030 demand scenario module: projects average and peak demand using adjustable assumptions for structural growth, AI/data centers, electrification, blockchain and efficiency. It is a planning scenario, not an exact prediction.

Peak risk classifier: classifies periods as Low, Medium or High risk based on demand percentile thresholds.

Nuclear analytics module: aggregates capacity, generation and reactor status by country and region, then builds Low, Base and High capacity scenarios through 2030.

NLP module: converts analyst text into keywords and a simple sentiment-style score.

GenAI report generator: creates an executive narrative from metrics and summaries without requiring an API key.

## Data Pipeline

Raw data goes into `data/raw`. The pipeline cleans it, writes processed datasets to `data/processed`, trains models, saves metrics and figures, builds SQLite tables, runs SQL queries and creates a report.

## PySpark and Databricks Readiness

The Spark scripts show how the same cleaning and feature logic can run on larger datasets. In Databricks, paths would move to DBFS or Unity Catalog and outputs could be saved as Delta tables.

## Dashboard

The dashboard has pages for executive KPIs, demand forecasting, peak-risk scoring, nuclear analytics, NLP insights and the executive report.

## Strengths

- End-to-end and runnable.
- Business-oriented outputs.
- Multiple modeling techniques.
- Clear documentation for interviews.
- Offline GenAI-style reporting.

## Limitations

- The fallback demand data is synthetic and only for demonstration.
- The real PJM CSV mirror is suitable for portfolio demonstration; a client implementation should ingest directly from the client-approved PJM/EIA source.
- The 2030 nuclear view is a scenario model, not a guaranteed forecast.
- Nuclear data is an IAEA-style sample unless replaced with an export.
- Weather, holidays and outage data are not included.
- The GenAI module is deterministic by default.

## Possible Interview Questions and Strong Answers

Why did you choose this project?  
Because energy demand forecasting is a practical business problem where machine learning, risk scoring, analytics and communication all matter.

Why is this relevant to the position?  
It maps directly to forecasting, scoring, SQL, dashboards, reporting, NLP, GenAI and scalable data pipelines.

What is the difference between forecasting and classification in your project?  
Forecasting predicts a numeric demand value. Classification converts demand behavior into a risk category: Low, Medium or High.

Why did you use XGBoost?  
XGBoost performs well on tabular time-based features, handles nonlinear effects and is easy to explain through feature importance.

What does the peak risk score mean?  
It is a 0-100 score representing how likely a period is to be high-risk based on the classifier output.

How does Generative AI add value here?  
It turns model metrics and analytical outputs into a stakeholder-ready narrative, reducing manual reporting effort.

What would you improve with more time?  
I would add weather, holidays, outage data, market prices, automated retraining and model monitoring.

How would this scale in a real client environment?  
I would run ETL in Databricks with Delta tables, schedule model training jobs, store artifacts in a model registry and serve dashboard outputs from governed tables.

How would you explain this to a non-technical stakeholder?  
The platform estimates future electricity demand, flags risky peak periods and summarizes what the business should do next.

What are the limitations of your data?  
The project supports real PJM/EIA data, but the bundled fallback data is only for demonstration. Nuclear sample data should be replaced with current official exports.

How would you deploy this in production?  
Use scheduled data ingestion, Databricks jobs, MLflow tracking, validation checks, model monitoring, a governed SQL layer and a dashboard connected to production tables.

## How to Explain This Project in Simple Words

This project helps an energy company prepare for high electricity demand. It looks at past demand, predicts what may happen next, flags risky periods, shows how nuclear power contributes stable supply, and writes a clear business report from the results.
