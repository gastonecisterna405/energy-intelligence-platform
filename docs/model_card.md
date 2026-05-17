# Model Card

## Demand Forecasting

Models:
- Statistical baseline: Exponential Smoothing with hourly seasonality when `statsmodels` is available.
- Tree model: XGBoost regressor when `xgboost` is installed, with a scikit-learn fallback.

Features:
- Hour, day of week, month, year, weekend flag, business-hour flag.
- Lag demand: 1, 2, 24, 48 and 168 hours.
- Rolling mean demand: 6, 24 and 168 hours.

Metrics:
- MAE, RMSE and MAPE.

## Peak Risk Scoring

Labels:
- High: demand at or above the 90th percentile.
- Medium: demand from the 75th to 90th percentile.
- Low: all other periods.

Models:
- Logistic Regression baseline.
- Random Forest classifier.

Metrics:
- Accuracy, macro precision, macro recall, macro F1 and confusion matrix.

## Limitations

The sample fallback demand data is not a substitute for operational load data. A production model should include weather, holidays, outage information, demand-response events and market conditions.

The 2030 nuclear capacity module is a scenario model. It should be described as strategic planning support, not as a precise forecast. A production version should ingest current PRIS/RDS-1 exports and project schedules.
