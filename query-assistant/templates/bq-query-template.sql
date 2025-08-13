-- Query Name: {{query_name}}
-- Generated: {{date}}

SELECT
  query,
  COUNT(*) as frequency
FROM
  `dookie-data.QE.events`
WHERE
  type = 'search'
  AND DATE BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) AND CURRENT_DATE()
  AND EXISTS (
    SELECT 1 FROM UNNEST(ab_tests.key) AS k WITH OFFSET i
    JOIN UNNEST(ab_tests.value) AS v WITH OFFSET j
    ON i = j
    WHERE k = 'DES' AND v IN ('A', 'B')
  )
GROUP BY
  query
ORDER BY
  frequency DESC
LIMIT 20;
