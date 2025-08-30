-- Back-To-School (BTS) Overall Performance Summary
-- Period: 2025-08-24 to 2025-08-27
-- Project: gtm-eduki-com, Dataset: QE, Table: events
-- Focus: Search ranking metrics, MRR, CTR@k analysis

WITH daily_sessions AS (
  SELECT 
    date,
    COUNT(DISTINCT session_id) AS total_sessions
  FROM `gtm-eduki-com.QE.events`
  WHERE date BETWEEN '2025-08-24' AND '2025-08-27'
    AND world = 'de'
  GROUP BY date
),

search_sessions AS (
  SELECT 
    date,
    session_id,
    COUNT(*) AS searches_count
  FROM `gtm-eduki-com.QE.events`
  WHERE date BETWEEN '2025-08-24' AND '2025-08-27'
    AND world = 'de'
    AND type = 'appearedInSearch'
    AND query != ''
  GROUP BY date, session_id
),

search_metrics AS (
  SELECT 
    date,
    COUNT(DISTINCT session_id) AS total_search_sessions,
    AVG(searches_count) AS avg_searches_per_session
  FROM search_sessions
  GROUP BY date
),

search_clicks AS (
  SELECT 
    date,
    session_id,
    position,
    item_id,
    item_price
  FROM `gtm-eduki-com.QE.events`
  WHERE date BETWEEN '2025-08-24' AND '2025-08-27'
    AND world = 'de'
    AND type = 'click'
    AND page_url LIKE 'https://eduki.com/de/suchergebnisse%'
    AND source = 'search'
    AND internal_path = 'sp'
    AND item_id IS NOT NULL
    AND item_price IS NOT NULL
    AND position IS NOT NULL
),

mrr_calculation AS (
  SELECT 
    date,
    session_id,
    MIN(position) AS first_click_position,
    CASE 
      WHEN MIN(position) > 0 THEN 1.0 / MIN(position)
      ELSE 0
    END AS reciprocal_rank
  FROM search_clicks
  WHERE position > 0
  GROUP BY date, session_id
),

mrr_metrics AS (
  SELECT 
    date,
    AVG(reciprocal_rank) AS mean_reciprocal_rank
  FROM mrr_calculation
  GROUP BY date
),

ctr_at_k AS (
  SELECT 
    date,
    COUNT(DISTINCT session_id) AS total_click_sessions,
    COUNT(DISTINCT CASE WHEN position = 1 THEN session_id END) AS clicks_at_1,
    COUNT(DISTINCT CASE WHEN position = 2 THEN session_id END) AS clicks_at_2,
    COUNT(DISTINCT CASE WHEN position = 3 THEN session_id END) AS clicks_at_3,
    COUNT(DISTINCT CASE WHEN position = 4 THEN session_id END) AS clicks_at_4,
    COUNT(DISTINCT CASE WHEN position = 5 THEN session_id END) AS clicks_at_5,
    COUNT(DISTINCT CASE WHEN position BETWEEN 6 AND 12 THEN session_id END) AS clicks_at_6_12,
    COUNT(DISTINCT CASE WHEN position BETWEEN 13 AND 19 THEN session_id END) AS clicks_at_13_19,
    COUNT(DISTINCT CASE WHEN position BETWEEN 20 AND 25 THEN session_id END) AS clicks_at_20_25,
    COUNT(DISTINCT CASE WHEN position > 25 THEN session_id END) AS clicks_at_25_plus
  FROM search_clicks
  GROUP BY date
),

order_data AS (
  SELECT 
    o.user_id, 
    o.number, 
    SUM(it.final_price) as final_price, 
    o.status, 
    o.created_at 
  FROM `gtm-eduki-com.lmp.orders` o 
  LEFT JOIN `gtm-eduki-com.lmp.order_items` it ON o.id = it.order_id 
  WHERE o.status NOT IN ('new', 'pending', 'cancelled') 
  GROUP BY o.user_id, o.number, o.status, o.created_at
),

purchase_events AS (
  SELECT 
    date,
    session_id,
    purchase_id,
    user_id,
    time
  FROM `gtm-eduki-com.QE.events`
  WHERE date BETWEEN '2025-08-24' AND '2025-08-27'
    AND world = 'de'
    AND type = 'purchase'
    AND purchase_id IS NOT NULL
),

search_pageviews AS (
  SELECT 
    date,
    session_id,
    time
  FROM `gtm-eduki-com.QE.events`
  WHERE date BETWEEN '2025-08-24' AND '2025-08-27'
    AND world = 'de'
    AND type = 'pageView'
    AND page_url LIKE 'https://eduki.com/de/suchergebnisse%'
),

time_to_convert AS (
  SELECT 
    spv.date,
    spv.session_id,
    MIN(spv.time) AS first_search_pageview_time,
    MIN(pe.time) AS purchase_time,
    TIMESTAMP_DIFF(MIN(pe.time), MIN(spv.time), MINUTE) AS minutes_to_convert
  FROM search_pageviews spv
  JOIN purchase_events pe ON spv.date = pe.date AND spv.session_id = pe.session_id
  GROUP BY spv.date, spv.session_id
),

conversion_metrics AS (
  SELECT 
    pe.date,
    COUNT(DISTINCT pe.session_id) AS converting_sessions,
    SUM(od.final_price) AS total_gmv,
    AVG(od.final_price) AS avg_order_value,
    AVG(ttc.minutes_to_convert) AS avg_time_to_convert_minutes
  FROM purchase_events pe
  JOIN order_data od ON CAST(pe.purchase_id AS STRING) = CAST(od.number AS STRING)
  LEFT JOIN time_to_convert ttc ON pe.date = ttc.date AND pe.session_id = ttc.session_id
  GROUP BY pe.date
)

SELECT 
  ds.date AS day,
  ds.total_sessions,
  COALESCE(sm.total_search_sessions, 0) AS total_search_sessions,
  ROUND(COALESCE(sm.avg_searches_per_session, 0), 2) AS searches_per_session,
  ROUND(COALESCE(mrr.mean_reciprocal_rank, 0), 4) AS mrr,
  CONCAT(
    'CTR@1: ', ROUND(CASE WHEN COALESCE(sm.total_search_sessions, 0) > 0 THEN (COALESCE(ctr.clicks_at_1, 0) / sm.total_search_sessions) * 100 ELSE 0 END, 2), '%, ',
    'CTR@2: ', ROUND(CASE WHEN COALESCE(sm.total_search_sessions, 0) > 0 THEN (COALESCE(ctr.clicks_at_2, 0) / sm.total_search_sessions) * 100 ELSE 0 END, 2), '%, ',
    'CTR@3: ', ROUND(CASE WHEN COALESCE(sm.total_search_sessions, 0) > 0 THEN (COALESCE(ctr.clicks_at_3, 0) / sm.total_search_sessions) * 100 ELSE 0 END, 2), '%, ',
    'CTR@4: ', ROUND(CASE WHEN COALESCE(sm.total_search_sessions, 0) > 0 THEN (COALESCE(ctr.clicks_at_4, 0) / sm.total_search_sessions) * 100 ELSE 0 END, 2), '%, ',
    'CTR@5: ', ROUND(CASE WHEN COALESCE(sm.total_search_sessions, 0) > 0 THEN (COALESCE(ctr.clicks_at_5, 0) / sm.total_search_sessions) * 100 ELSE 0 END, 2), '%, ',
    'CTR@6-12: ', ROUND(CASE WHEN COALESCE(sm.total_search_sessions, 0) > 0 THEN (COALESCE(ctr.clicks_at_6_12, 0) / sm.total_search_sessions) * 100 ELSE 0 END, 2), '%, ',
    'CTR@13-19: ', ROUND(CASE WHEN COALESCE(sm.total_search_sessions, 0) > 0 THEN (COALESCE(ctr.clicks_at_13_19, 0) / sm.total_search_sessions) * 100 ELSE 0 END, 2), '%, ',
    'CTR@20-25: ', ROUND(CASE WHEN COALESCE(sm.total_search_sessions, 0) > 0 THEN (COALESCE(ctr.clicks_at_20_25, 0) / sm.total_search_sessions) * 100 ELSE 0 END, 2), '%, ',
    'CTR@25+: ', ROUND(CASE WHEN COALESCE(sm.total_search_sessions, 0) > 0 THEN (COALESCE(ctr.clicks_at_25_plus, 0) / sm.total_search_sessions) * 100 ELSE 0 END, 2), '%'
  ) AS ctr_at_k,
  ROUND((COALESCE(cm.converting_sessions, 0) / ds.total_sessions) * 100, 2) AS conversion_rate,
  ROUND(COALESCE(cm.avg_time_to_convert_minutes, 0), 2) AS avg_time_to_convert_minutes,
  ROUND(COALESCE(cm.total_gmv, 0) / ds.total_sessions, 2) AS gmv_per_session,
  ROUND(COALESCE(cm.avg_order_value, 0), 2) AS aov
FROM daily_sessions ds
LEFT JOIN search_metrics sm ON ds.date = sm.date
LEFT JOIN mrr_metrics mrr ON ds.date = mrr.date
LEFT JOIN ctr_at_k ctr ON ds.date = ctr.date
LEFT JOIN conversion_metrics cm ON ds.date = cm.date
ORDER BY ds.date;
