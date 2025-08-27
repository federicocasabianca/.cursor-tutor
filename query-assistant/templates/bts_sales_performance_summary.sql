-- Back-To-School (BTS) Sales Period Performance Summary
-- Period: 2025-08-24 to 2025-08-27
-- Project: gtm-eduki-com, Dataset: QE, Table: events

WITH bts_pageviews AS (
  SELECT 
    date,
    session_id,
    page_url,
    CASE 
      WHEN page_url = 'https://eduki.com/de/suchergebnisse' THEN 'Generic Search'
      WHEN page_url = 'https://eduki.com/de/suchergebnisse?t=2971' THEN 'Schulstart Search'
      WHEN page_url = 'https://eduki.com/de/suchergebnisse?b=1&sale=1' THEN 'Bundle Search'
      WHEN page_url = 'https://eduki.com/de/suchergebnisse?prc=1&b=0' THEN 'Standalone Search'
      ELSE 'Other'
    END AS url_type
  FROM `gtm-eduki-com.QE.events`
  WHERE date BETWEEN '2025-08-24' AND '2025-08-27'
    AND world = 'de'
    AND type = 'pageView'
    AND page_url IN (
      'https://eduki.com/de/suchergebnisse',
      'https://eduki.com/de/suchergebnisse?t=2971',
      'https://eduki.com/de/suchergebnisse?b=1&sale=1',
      'https://eduki.com/de/suchergebnisse?prc=1&b=0'
    )
),

daily_totals AS (
  SELECT 
    date,
    COUNT(DISTINCT session_id) AS total_daily_sessions
  FROM `gtm-eduki-com.QE.events`
  WHERE date BETWEEN '2025-08-24' AND '2025-08-27'
    AND world = 'de'
    AND type = 'pageView'
  GROUP BY date
),

url_sessions AS (
  SELECT DISTINCT
    date,
    session_id,
    url_type
  FROM bts_pageviews
),

search_sessions_by_url_type AS (
  SELECT 
    us.date,
    us.url_type,
    us.session_id,
    COUNT(se.session_id) AS searches_count
  FROM url_sessions us
  LEFT JOIN (
    SELECT 
      date,
      session_id
    FROM `gtm-eduki-com.QE.events`
    WHERE date BETWEEN '2025-08-24' AND '2025-08-27'
      AND world = 'de'
      AND type = 'appearedInSearch'
      AND query != ''
  ) se ON us.date = se.date AND us.session_id = se.session_id
  GROUP BY us.date, us.url_type, us.session_id
),

search_per_session_metrics AS (
  SELECT 
    date,
    url_type,
    AVG(searches_count) AS avg_searches_per_session
  FROM search_sessions_by_url_type
  GROUP BY date, url_type
),

click_events AS (
  SELECT 
    date,
    session_id,
    item_id,
    item_price,
    position
  FROM `gtm-eduki-com.QE.events`
  WHERE date BETWEEN '2025-08-24' AND '2025-08-27'
    AND world = 'de'
    AND type = 'click'
    AND source = 'search'
    AND internal_path = 'sp'
    AND item_id IS NOT NULL
    AND item_price IS NOT NULL
    AND position IS NOT NULL
),

ctr_metrics AS (
  SELECT 
    us.date,
    us.url_type,
    COUNT(DISTINCT CASE WHEN ce.session_id IS NOT NULL THEN ce.session_id END) AS sessions_with_clicks,
    COUNT(CASE WHEN ce.session_id IS NOT NULL THEN ce.session_id END) AS total_clicks_to_mp
  FROM url_sessions us
  LEFT JOIN click_events ce ON us.date = ce.date AND us.session_id = ce.session_id
  GROUP BY us.date, us.url_type
),

add_to_cart_events AS (
  SELECT 
    date,
    session_id,
    item_id,
    item_price,
    position
  FROM `gtm-eduki-com.QE.events`
  WHERE date BETWEEN '2025-08-24' AND '2025-08-27'
    AND world = 'de'
    AND type = 'addToCart'
    AND item_id IS NOT NULL
    AND item_price IS NOT NULL
    AND position IS NOT NULL
),

add_to_cart_metrics AS (
  SELECT 
    us.date,
    us.url_type,
    COUNT(DISTINCT CASE WHEN atc.session_id IS NOT NULL THEN atc.session_id END) AS sessions_with_add_to_cart,
    COUNT(CASE WHEN atc.session_id IS NOT NULL THEN atc.session_id END) AS total_add_to_cart
  FROM url_sessions us
  LEFT JOIN add_to_cart_events atc ON us.date = atc.date AND us.session_id = atc.session_id
  GROUP BY us.date, us.url_type
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

pageview_events AS (
  SELECT 
    date,
    session_id,
    page_url,
    time,
    CASE 
      WHEN page_url = 'https://eduki.com/de/suchergebnisse' THEN 'Generic Search'
      WHEN page_url = 'https://eduki.com/de/suchergebnisse?t=2971' THEN 'Schulstart Search'
      WHEN page_url = 'https://eduki.com/de/suchergebnisse?b=1&sale=1' THEN 'Bundle Search'
      WHEN page_url = 'https://eduki.com/de/suchergebnisse?prc=1&b=0' THEN 'Standalone Search'
      ELSE 'Other'
    END AS url_type
  FROM `gtm-eduki-com.QE.events`
  WHERE date BETWEEN '2025-08-24' AND '2025-08-27'
    AND world = 'de'
    AND type = 'pageView'
    AND page_url IN (
      'https://eduki.com/de/suchergebnisse',
      'https://eduki.com/de/suchergebnisse?t=2971',
      'https://eduki.com/de/suchergebnisse?b=1&sale=1',
      'https://eduki.com/de/suchergebnisse?prc=1&b=0'
    )
),

time_to_convert AS (
  SELECT 
    pv.date,
    pv.url_type,
    pv.session_id,
    MIN(pv.time) AS first_pageview_time,
    MIN(pe.time) AS purchase_time,
    TIMESTAMP_DIFF(MIN(pe.time), MIN(pv.time), MINUTE) AS minutes_to_convert
  FROM pageview_events pv
  LEFT JOIN purchase_events pe ON pv.date = pe.date AND pv.session_id = pe.session_id
  WHERE pe.session_id IS NOT NULL  -- Only sessions that converted
  GROUP BY pv.date, pv.url_type, pv.session_id
),

conversion_metrics AS (
  SELECT 
    us.date,
    us.url_type,
    COUNT(DISTINCT CASE WHEN pe.session_id IS NOT NULL THEN pe.session_id END) AS converting_sessions,
    SUM(CASE WHEN pe.session_id IS NOT NULL THEN od.final_price END) AS total_gmv,
    AVG(CASE WHEN pe.session_id IS NOT NULL THEN od.final_price END) AS avg_order_value,
    AVG(ttc.minutes_to_convert) AS avg_time_to_convert_minutes
  FROM url_sessions us
  LEFT JOIN purchase_events pe ON us.date = pe.date AND us.session_id = pe.session_id
  LEFT JOIN order_data od ON CAST(pe.purchase_id AS STRING) = CAST(od.number AS STRING)
  LEFT JOIN time_to_convert ttc ON us.date = ttc.date AND us.url_type = ttc.url_type AND us.session_id = ttc.session_id
  GROUP BY us.date, us.url_type
),

url_metrics AS (
  SELECT 
    date,
    url_type,
    COUNT(DISTINCT session_id) AS total_sessions,
    COUNT(*) AS total_clicks_urls
  FROM bts_pageviews
  GROUP BY date, url_type
)

SELECT 
  um.date AS day,
  um.url_type,
  um.total_sessions,
  um.total_clicks_urls,
  ROUND((um.total_sessions / dt.total_daily_sessions) * 100, 2) AS percentage_of_sessions,
  ROUND(COALESCE(sps.avg_searches_per_session, 0), 2) AS search_per_session,
  ROUND((COALESCE(ctr.sessions_with_clicks, 0) / um.total_sessions) * 100, 2) AS ctr_search_to_mp,
  ROUND((COALESCE(atc.sessions_with_add_to_cart, 0) / um.total_sessions) * 100, 2) AS add_to_cart_ratio,
  ROUND((COALESCE(cm.converting_sessions, 0) / um.total_sessions) * 100, 2) AS conversion_rate,
  ROUND(COALESCE(cm.avg_time_to_convert_minutes, 0), 2) AS avg_time_to_convert_minutes,
  ROUND(COALESCE(cm.total_gmv, 0) / um.total_sessions, 2) AS gmv_per_session,
  ROUND(COALESCE(cm.avg_order_value, 0), 2) AS aov
FROM url_metrics um
JOIN daily_totals dt ON um.date = dt.date
LEFT JOIN search_per_session_metrics sps ON um.date = sps.date AND um.url_type = sps.url_type
LEFT JOIN ctr_metrics ctr ON um.date = ctr.date AND um.url_type = ctr.url_type
LEFT JOIN add_to_cart_metrics atc ON um.date = atc.date AND um.url_type = atc.url_type
LEFT JOIN conversion_metrics cm ON um.date = cm.date AND um.url_type = cm.url_type
ORDER BY um.date, um.total_sessions DESC;
