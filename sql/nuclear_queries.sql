SELECT country, SUM(capacity_mw) AS capacity_mw
FROM nuclear_capacity
GROUP BY country
ORDER BY capacity_mw DESC;

SELECT region, SUM(capacity_mw) AS capacity_mw, SUM(reactor_count) AS reactors
FROM nuclear_capacity
GROUP BY region
ORDER BY capacity_mw DESC;
