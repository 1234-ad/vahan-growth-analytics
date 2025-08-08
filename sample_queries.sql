-- 1) Monthly aggregation
CREATE VIEW vw_monthly_registrations AS
SELECT
  DATE_TRUNC('month', date) AS period,
  vehicle_category,
  maker,
  SUM(count) AS total_count
FROM registrations
GROUP BY 1,2,3;

-- 2) YoY for monthly: compare same month last year
SELECT
  t.period,
  t.vehicle_category,
  t.maker,
  t.total_count,
  (t.total_count - ly.total_count) * 100.0 / NULLIF(ly.total_count,0) AS yoy_pct
FROM vw_monthly_registrations t
LEFT JOIN vw_monthly_registrations ly
  ON t.maker = ly.maker
  AND t.vehicle_category = ly.vehicle_category
  AND DATE_TRUNC('month', t.period - INTERVAL '12 months') = DATE_TRUNC('month', ly.period)
ORDER BY t.period DESC;

-- 3) QoQ (quarter-over-quarter)
SELECT
  t.period,
  t.vehicle_category,
  t.maker,
  t.total_count,
  (t.total_count - prev.total_count) * 100.0 / NULLIF(prev.total_count,0) AS qoq_pct
FROM (
  SELECT DATE_TRUNC('quarter', date) AS period, vehicle_category, maker, SUM(count) AS total_count
  FROM registrations
  GROUP BY 1,2,3
) t
LEFT JOIN (
  SELECT DATE_TRUNC('quarter', date) AS period, vehicle_category, maker, SUM(count) AS total_count
  FROM registrations
  GROUP BY 1,2,3
) prev
  ON t.maker = prev.maker
  AND t.vehicle_category = prev.vehicle_category
  AND t.period = prev.period + INTERVAL '3 months'
ORDER BY t.period DESC;
