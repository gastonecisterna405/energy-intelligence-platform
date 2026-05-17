CREATE TABLE IF NOT EXISTS demand_observations (
    datetime TEXT PRIMARY KEY,
    demand_mw REAL
);

CREATE TABLE IF NOT EXISTS demand_forecasts (
    datetime TEXT,
    actual_demand_mw REAL,
    predicted_demand_mw REAL,
    model TEXT
);

CREATE TABLE IF NOT EXISTS peak_risk_scores (
    datetime TEXT,
    demand_mw REAL,
    actual_risk_label TEXT,
    predicted_risk_label TEXT,
    risk_score REAL
);

CREATE TABLE IF NOT EXISTS nuclear_capacity (
    country TEXT,
    region TEXT,
    status TEXT,
    reactor_count INTEGER,
    capacity_mw REAL,
    annual_generation_gwh REAL,
    nuclear_share_pct REAL
);
