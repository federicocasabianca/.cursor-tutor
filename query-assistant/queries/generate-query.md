# Generate Query

## User Prompt
Pull the time where search queries where executed

## Expected Query Output
- Filter by world `world = 'de'`
- Event is `type:"pageView"` and `page_url = 'https://eduki.com/de/suchergebnisse?query%'` and `session_id is not null` 
- Return: time and query.

## Environment
Target: BigQuery
Project: `gtm-eduki-com`
Dataset: `QE`

## Generated Query

```sql
WITH search_events AS (
  SELECT 
    time,
    query,
    EXTRACT(HOUR FROM time) AS hour
  FROM `gtm-eduki-com.QE.events`
  WHERE world = 'de'
    AND type = 'pageView'
    AND page_url LIKE 'https://eduki.com/de/suchergebnisse?query%'
    AND session_id IS NOT NULL
),

time_periods AS (
  SELECT 
    CASE 
      WHEN hour >= 6 AND hour < 8 THEN 'Early Morning (6-8)'
      WHEN hour >= 8 AND hour < 12 THEN 'Morning (8-12)'
      WHEN hour >= 12 AND hour < 14 THEN 'Midday (12-14)'
      WHEN hour >= 14 AND hour < 16 THEN 'Afternoon (14-16)'
      WHEN hour >= 16 AND hour < 20 THEN 'Evening (16-20)'
      WHEN hour >= 20 AND hour < 24 THEN 'Night (20-24)'
      ELSE 'Late Night (0-6)'
    END AS time_period,
    time,
    query
  FROM search_events
)

SELECT 
  time_period,
  COUNT(*) AS search_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM time_periods
GROUP BY time_period
ORDER BY 
  CASE time_period
    WHEN 'Early Morning (6-8)' THEN 1
    WHEN 'Morning (8-12)' THEN 2
    WHEN 'Midday (12-14)' THEN 3
    WHEN 'Afternoon (14-16)' THEN 4
    WHEN 'Evening (16-20)' THEN 5
    WHEN 'Night (20-24)' THEN 6
    WHEN 'Late Night (0-6)' THEN 7
  END
```