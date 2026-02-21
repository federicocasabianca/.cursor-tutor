# Generate Query

## User Prompt
Check the click through rate of the 'recommendation' material cards.

## Expected Query Output
- Common filters `world = 'de' AND session_id is not null AND user_id is not null`
- Filter by Before change `date between '2026-01-01' AND '2026-01-22'`
- Filter by After change `date between '2026-01-23' AND CURRENT_DATE()`
- Click event: `type='click' AND item_id is not null AND internal_path = 'recommendations'`
- Return: 
-- Total click events coming from `internal_path='recommendation'` BEFORE and AFTER the change
-- % of clicks vs the total unique sessions BEFORE and AFTER the change
-- Group by the page_url field

## Environment
Target: BigQuery
Project: `gtm-eduki-com`
Dataset: `QE`
---

## BigQuery SQL

```sql
-- Recommendation material cards: CTR by page (Home Page, Personalization)
-- Filters: world='de', session_id not null, user_id not null
-- Periods: Before (2026-01-01 to 2026-01-22), After (2026-01-23 to CURRENT_DATE)
-- Click event: type='click' AND item_id IS NOT NULL AND internal_path = 'recommendations'
--
-- Home Page: total_sessions = pageView + page_url='https://eduki.com/de'
-- Personalization: total_sessions = pageView + page_url='https://eduki.com/de/empfehlungen'
-- CTR = click_sessions / total_sessions (click_sessions = sessions with recommendation click on that page)

WITH base_events AS (
  SELECT
    session_id,
    type,
    page_url,
    date,
    CASE
      WHEN date BETWEEN '2026-01-01' AND '2026-01-22' THEN 'BEFORE'
      WHEN date >= '2026-01-23' AND date <= CURRENT_DATE() THEN 'AFTER'
    END AS period
  FROM `gtm-eduki-com.QE.events`
  WHERE world = 'de'
    AND session_id IS NOT NULL
    AND user_id IS NOT NULL
    AND (
      (date BETWEEN '2026-01-01' AND '2026-01-22')
      OR (date >= '2026-01-23' AND date <= CURRENT_DATE())
    )
),

-- Total sessions per page (pageView)
-- Home Page: page_url = 'https://eduki.com/de'
-- Personalization: page_url = 'https://eduki.com/de/empfehlungen'
page_sessions AS (
  SELECT session_id, period, 'Home Page' AS page_name
  FROM base_events
  WHERE type = 'pageView' AND page_url = 'https://eduki.com/de'
  UNION DISTINCT
  SELECT session_id, period, 'Personalization' AS page_name
  FROM base_events
  WHERE type = 'pageView' AND page_url = 'https://eduki.com/de/empfehlungen'
),

-- Click sessions per page (recommendation clicks scoped to page)
-- Same click definition: type='click', item_id not null, internal_path='recommendations'
click_sessions AS (
  SELECT session_id, period, 'Home Page' AS page_name
  FROM base_events
  WHERE type = 'click'
    AND item_id IS NOT NULL
    AND internal_path = 'recommendations'
    AND page_url = 'https://eduki.com/de'
  UNION DISTINCT
  SELECT session_id, period, 'Personalization' AS page_name
  FROM base_events
  WHERE type = 'click'
    AND item_id IS NOT NULL
    AND internal_path = 'recommendations'
    AND page_url = 'https://eduki.com/de/empfehlungen'
),

-- Aggregates: total sessions and click sessions per page, per period
totals AS (
  SELECT
    p.period,
    p.page_name,
    COUNT(DISTINCT p.session_id) AS total_sessions,
    COUNT(DISTINCT c.session_id) AS click_sessions
  FROM page_sessions p
  LEFT JOIN click_sessions c
    ON p.session_id = c.session_id AND p.period = c.period AND p.page_name = c.page_name
  GROUP BY p.period, p.page_name
)

-- Output: CTR (total count + %) for BEFORE and AFTER
SELECT
  page_name,
  period,
  total_sessions,
  click_sessions,
  ROUND(100.0 * click_sessions / NULLIF(total_sessions, 0), 2) AS ctr_pct
FROM totals
ORDER BY page_name, period;
```