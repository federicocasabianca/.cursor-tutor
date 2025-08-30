-- Back-To-School (BTS) Filter Usage Analysis
-- Period: 2025-08-24 to 2025-08-27
-- Project: gtm-eduki-com, Dataset: QE, Table: events
-- Focus: Filter usage patterns after specific search page visits

WITH initial_search_pageviews AS (
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
    END AS initial_search_type
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

  UNION ALL

  -- Add Regular Search events (actual query searches)
  SELECT 
    date,
    session_id,
    page_url,
    time,
    'Regular Search' AS initial_search_type
  FROM `gtm-eduki-com.QE.events`
  WHERE date BETWEEN '2025-08-24' AND '2025-08-27'
    AND world = 'de'
    AND type = 'appearedInSearch'
    AND page_url LIKE 'https://eduki.com/de/suchergebnisse?query=%'
    AND query != ''
),

-- Get the first search pageview per session for each search type
first_search_per_session AS (
  SELECT 
    date,
    session_id,
    initial_search_type,
    MIN(time) AS first_search_time
  FROM initial_search_pageviews
  GROUP BY date, session_id, initial_search_type
),

-- Find subsequent search pageviews with filters in the same session
filter_search_events AS (
  SELECT 
    e.date,
    e.session_id,
    e.page_url,
    e.time,
    e.query_params_key,
    fs.initial_search_type,
    fs.first_search_time
  FROM `gtm-eduki-com.QE.events` e
  JOIN first_search_per_session fs ON e.date = fs.date 
    AND e.session_id = fs.session_id
  WHERE e.date BETWEEN '2025-08-24' AND '2025-08-27'
    AND e.world = 'de'
    AND e.type = 'pageView'
    AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse%'
    AND e.time > fs.first_search_time  -- Only events after the initial search
    AND ARRAY_LENGTH(e.query_params_key) > 0  -- Has query parameters
),

-- Extract individual filters used
filter_usage AS (
  SELECT 
    fse.date,
    fse.session_id,
    fse.initial_search_type,
    fse.page_url,
    fse.time,
    param_key AS filter_type
  FROM filter_search_events fse
  CROSS JOIN UNNEST(fse.query_params_key) AS param_key
  WHERE param_key IN ('t', 'c', 'prc', 's', 'sale', 'mt', 'b', 'f', 'ft', 'ly', 'tj', 'tp')
),

-- Add filter names and create session-level filter summary
filter_sessions AS (
  SELECT 
    fu.date,
    fu.session_id,
    fu.initial_search_type,
    fu.filter_type,
    CASE
      WHEN fu.filter_type = 't' THEN 'Subject'
      WHEN fu.filter_type = 'c' THEN 'Class Grade'
      WHEN fu.filter_type = 'prc' THEN 'Price'
      WHEN fu.filter_type = 's' THEN 'Sorting'
      WHEN fu.filter_type = 'sale' THEN 'Sale'
      WHEN fu.filter_type = 'mt' THEN 'Material Type'
      WHEN fu.filter_type = 'b' THEN 'Materialumfang'
      WHEN fu.filter_type = 'f' THEN 'Materialformat'
      WHEN fu.filter_type = 'ft' THEN 'Dateiformat'
      WHEN fu.filter_type = 'ly' THEN 'Learning Years'
      WHEN fu.filter_type = 'tj' THEN 'Tag'
      WHEN fu.filter_type = 'tp' THEN 'Seiten'
      ELSE fu.filter_type
    END AS filter_name,
    MIN(fu.time) AS first_filter_time
  FROM filter_usage fu
  GROUP BY fu.date, fu.session_id, fu.initial_search_type, fu.filter_type
),

-- Count total sessions that started with each search type
total_sessions_per_search_type AS (
  SELECT 
    date,
    initial_search_type,
    COUNT(DISTINCT session_id) AS total_sessions
  FROM first_search_per_session
  GROUP BY date, initial_search_type
),

-- Calculate filter usage metrics
filter_metrics AS (
  SELECT 
    fs.date,
    fs.initial_search_type,
    fs.filter_type,
    fs.filter_name,
    COUNT(DISTINCT fs.session_id) AS sessions_using_filter,
    COUNT(*) AS total_filter_applications
  FROM filter_sessions fs
  GROUP BY fs.date, fs.initial_search_type, fs.filter_type, fs.filter_name
),

-- Get order data for conversion analysis
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

-- Track conversions from filter-using sessions
filter_conversions AS (
  SELECT 
    fs.date,
    fs.initial_search_type,
    fs.filter_type,
    fs.filter_name,
    COUNT(DISTINCT CASE WHEN pe.session_id IS NOT NULL THEN fs.session_id END) AS converting_sessions,
    SUM(CASE WHEN pe.session_id IS NOT NULL THEN od.final_price END) AS total_gmv
  FROM filter_sessions fs
  LEFT JOIN `gtm-eduki-com.QE.events` pe ON fs.date = pe.date 
    AND fs.session_id = pe.session_id 
    AND pe.type = 'purchase'
    AND pe.time > fs.first_filter_time
  LEFT JOIN order_data od ON CAST(pe.purchase_id AS STRING) = CAST(od.number AS STRING)
  GROUP BY fs.date, fs.initial_search_type, fs.filter_type, fs.filter_name
)

-- Final results with comprehensive filter usage analysis
SELECT 
  fm.date AS day,
  fm.initial_search_type,
  fm.filter_name,
  fm.filter_type,
  ts.total_sessions AS total_sessions_for_search_type,
  fm.sessions_using_filter,
  fm.total_filter_applications,
  ROUND((fm.sessions_using_filter / ts.total_sessions) * 100, 2) AS filter_usage_percentage,
  ROUND(fm.total_filter_applications / fm.sessions_using_filter, 2) AS avg_applications_per_session,
  COALESCE(fc.converting_sessions, 0) AS filter_converting_sessions,
  ROUND(CASE 
    WHEN fm.sessions_using_filter > 0 
    THEN (COALESCE(fc.converting_sessions, 0) / fm.sessions_using_filter) * 100 
    ELSE 0 
  END, 2) AS filter_conversion_rate,
  ROUND(COALESCE(fc.total_gmv, 0), 2) AS filter_total_gmv,
  ROUND(CASE 
    WHEN fm.sessions_using_filter > 0 
    THEN COALESCE(fc.total_gmv, 0) / fm.sessions_using_filter 
    ELSE 0 
  END, 2) AS gmv_per_filter_session
FROM filter_metrics fm
JOIN total_sessions_per_search_type ts ON fm.date = ts.date 
  AND fm.initial_search_type = ts.initial_search_type
LEFT JOIN filter_conversions fc ON fm.date = fc.date 
  AND fm.initial_search_type = fc.initial_search_type
  AND fm.filter_type = fc.filter_type
ORDER BY fm.date, fm.initial_search_type, fm.sessions_using_filter DESC;
