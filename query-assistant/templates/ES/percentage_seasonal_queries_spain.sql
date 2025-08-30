-- Query Name: percentage_seasonal_queries_spain
-- Generated: 2024-06-13

WITH total_queries AS (
  SELECT COUNT(*) AS total
  FROM `gtm-eduki-com.QE.events`
  WHERE
    world = 'es'
    AND type = 'appearedInSearch'
    AND DATE(date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 180 DAY)
),
seasonal_queries AS (
  SELECT COUNT(*) AS seasonal_total
  FROM `gtm-eduki-com.QE.events`
  WHERE
    world = 'es'
    AND type = 'appearedInSearch'
    AND DATE(date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 180 DAY)
    AND (
      LOWER(query) LIKE '%verano%'
      OR LOWER(query) LIKE '%invierno%'
      OR LOWER(query) LIKE '%primavera%'
      OR LOWER(query) LIKE '%otoño%'
    )
)
SELECT
  total_queries.total AS total_search_queries,
  seasonal_queries.seasonal_total AS seasonal_search_queries,
  ROUND(100 * seasonal_queries.seasonal_total / total_queries.total, 2) AS seasonal_percentage
FROM
  total_queries,
  seasonal_queries
