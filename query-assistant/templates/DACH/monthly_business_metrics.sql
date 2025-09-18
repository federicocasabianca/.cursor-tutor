-- Monthly Business Metrics Analysis
-- Shows CVR, AOV, CVR/search, GMV/session for June, July, August (excluding Aug 24-27)
-- Target: BigQuery, Project: gtm-eduki-com, Dataset: QE

WITH mp_events AS (
  SELECT
    e.session_id,
    e.user_id,
    e.date AS d_local,
    e.os,
    e.page_url,
    e.type,
    e.purchase_id,
    e.world,
    e.query
  FROM `gtm-eduki-com.QE.events` e
  WHERE e.date >= '2024-06-01'
    AND e.date < '2024-09-01'
    AND NOT (e.date >= '2024-08-24' AND e.date <= '2024-08-27')
),

mp_sessions AS (
  SELECT DISTINCT session_id, user_id
  FROM mp_events mp
  WHERE mp.page_url LIKE 'https://eduki.com/de/suchergebnisse%' OR mp.page_url like '%Search%'
          AND mp.query != '' AND mp.query IS NOT NULL
              AND mp.type = 'appearedInSearch'
              AND world = 'de'
),

session_features AS (
  SELECT
    m.session_id,
    m.user_id,
    DATE_TRUNC(m.d_local, MONTH) AS month,
    ANY_VALUE(m.world) AS world,
    os as platform
  FROM mp_events m
    inner join mp_sessions s USING (session_id, user_id)
  GROUP BY m.session_id, m.user_id, DATE_TRUNC(m.d_local, MONTH), os
),

purchase_map AS (
  -- Orders seen in any event of those sessions, within the window
  SELECT DISTINCT
    s.session_id,
    s.user_id,
    CAST(e.purchase_id AS STRING) AS order_number
  FROM `gtm-eduki-com.QE.events` e
  inner JOIN mp_sessions s USING (session_id, user_id)
  WHERE e.date >= '2024-06-01'
    AND e.date < '2024-09-01'
    AND NOT (e.date >= '2024-08-24' AND e.date <= '2024-08-27')
    AND e.purchase_id IS NOT NULL
),

orders AS (
  SELECT
    CAST(o.number AS STRING) AS order_number,
    o.user_id,
    SUM(it.final_price) AS gmv
  FROM `gtm-eduki-com.lmp.orders` o
  LEFT JOIN `gtm-eduki-com.lmp.order_items` it
    ON o.id = it.order_id
  WHERE o.status NOT IN ('new','pending','cancelled')
  GROUP BY order_number, o.user_id
),

session_revenue AS (
  SELECT
    sf.session_id,
    sf.user_id,
    COUNT(DISTINCT o.order_number) AS orders,
    SUM(o.gmv) AS gmv
  FROM session_features sf
  LEFT JOIN purchase_map pm USING (session_id, user_id)
  LEFT JOIN orders o
    ON o.order_number = pm.order_number
   AND o.user_id = pm.user_id
  GROUP BY sf.session_id, sf.user_id
),

sessions AS (
  SELECT
    sf.session_id, sf.user_id, sf.month, sf.platform, sf.world,
    COALESCE(sr.orders, 0) AS orders,
    COALESCE(sr.gmv, 0) AS gmv
  FROM session_features sf
  LEFT JOIN session_revenue sr USING (session_id, user_id)
)

SELECT
  month,
  COUNT(DISTINCT session_id) AS sessions,
  SUM(orders) AS orders,
  SUM(gmv) AS gmv,
  ROUND(SAFE_DIVIDE(SUM(orders), COUNT(DISTINCT session_id)) * 100, 2) AS cvr_percent,
  ROUND(SAFE_DIVIDE(SUM(gmv), NULLIF(SUM(orders),0)), 2) AS aov,
  ROUND(SAFE_DIVIDE(COUNT(DISTINCT CASE WHEN orders > 0 THEN session_id END), COUNT(DISTINCT session_id)) * 100, 2) AS cvr_per_search,
  ROUND(SAFE_DIVIDE(SUM(gmv), COUNT(DISTINCT session_id)), 2) AS gmv_per_session
FROM sessions
WHERE world = 'de'
GROUP BY month
ORDER BY month;
