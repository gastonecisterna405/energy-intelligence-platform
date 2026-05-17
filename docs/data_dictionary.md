# Data Dictionary

## demand_observations

- `datetime`: Hourly timestamp.
- `demand_mw`: Electricity demand in megawatts.

Real-data note: when `data/raw/PJM_Load_hourly.csv` is present, these records come from the public PJM hourly load CSV used by the demo. For fast local execution, the processed dataset may use the most recent three years.

## demand_forecasts

- `datetime`: Forecasted timestamp.
- `actual_demand_mw`: Observed demand.
- `predicted_demand_mw`: Model prediction.
- `model`: Model name.

## demand_projection_2030

- `scenario`: Conservative, Base, Accelerated or Custom in the dashboard.
- `year`: Projection year.
- `anchor_year`: Last historical year used as the starting reference.
- `projected_avg_demand_mw`: Scenario average demand in megawatts.
- `projected_peak_demand_mw`: Scenario peak demand in megawatts.
- `structural_growth_pct`: Normal annual demand growth assumption.
- `ai_data_center_pct`: Additional annual demand assumption from AI and data centers.
- `electrification_pct`: Additional annual demand assumption from EVs, heat pumps and industrial electrification.
- `blockchain_pct`: Additional annual demand assumption from blockchain or crypto mining load.
- `efficiency_offset_pct`: Annual demand reduction from efficiency and demand response.

## peak_risk_scores

- `datetime`: Scored timestamp.
- `demand_mw`: Observed demand.
- `actual_risk_label`: Label from percentile rule.
- `predicted_risk_label`: Classifier output.
- `risk_score`: Probability-style high-risk score from 0 to 100.

## nuclear_capacity

- `country`: Country name.
- `region`: Region grouping.
- `status`: Operational, under construction, shutdown or related status.
- `reactor_count`: Number of reactors.
- `capacity_mw`: Installed nuclear capacity.
- `annual_generation_gwh`: Annual generation estimate.
- `nuclear_share_pct`: Nuclear share of electricity generation.

## nuclear_capacity_projection_2030

- `country`: Country name.
- `region`: Region grouping.
- `year`: Scenario year from 2025 to 2030.
- `scenario`: Low, Base or High realization assumption.
- `projected_capacity_mw`: Scenario capacity in megawatts.
- `current_capacity_mw`: Operational or restarting capacity used as the base.
- `under_construction_capacity_mw`: Capacity treated as potential additions by 2030.

## nlp_comments

- `comment`: Analyst comment or report snippet.
- `label`: Simple category used for explanation and aggregation.
