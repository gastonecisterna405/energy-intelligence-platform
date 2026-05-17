SELECT predicted_risk_label, COUNT(*) AS periods
FROM peak_risk_scores
GROUP BY predicted_risk_label;

SELECT substr(datetime, 1, 7) AS month, COUNT(*) AS high_risk_periods
FROM peak_risk_scores
WHERE predicted_risk_label = 'High'
GROUP BY month
ORDER BY month;
