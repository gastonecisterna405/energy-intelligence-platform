SELECT substr(datetime, 1, 7) AS month, AVG(demand_mw) AS avg_demand_mw
FROM demand_observations
GROUP BY month
ORDER BY month;

SELECT datetime, demand_mw
FROM demand_observations
ORDER BY demand_mw DESC
LIMIT 20;
