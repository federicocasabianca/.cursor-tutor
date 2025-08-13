-- Query Name: breakdown_seasonal_keywords_spain
-- Generated: 2024-06-13

SELECT
  query,
  COUNT(*) AS search_count
FROM
  `gtm-eduki-com.QE.events`
WHERE
  type = 'appearedInSearch'
  AND DATE(date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 180 DAY)
  AND world = 'es'
  AND (
    LOWER(query) LIKE '%verano%'
    OR LOWER(query) LIKE '%invierno%'
    OR LOWER(query) LIKE '%primavera%'
    OR LOWER(query) LIKE '%otoño%'
  )
GROUP BY
  query
ORDER BY
  search_count DESC
