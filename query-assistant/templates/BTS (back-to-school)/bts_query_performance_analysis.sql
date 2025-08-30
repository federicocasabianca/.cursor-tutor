-- Back-To-School (BTS) Query Performance Analysis (Device & User Filtered)
-- Period: 2025-08-24 to 2025-08-27
-- Project: gtm-eduki-com, Dataset: QE, Table: events
-- Focus: Desktop/tablet/mobile users only, excluding app and anonymous users

WITH regular_search_events AS (
  SELECT 
    date,
    session_id,
    query,
    time,
    user_id,
    user_device
  FROM `gtm-eduki-com.QE.events`
  WHERE date BETWEEN '2025-08-24' AND '2025-08-27'
    AND world = 'de'
    AND type = 'appearedInSearch'
    AND page_url LIKE 'https://eduki.com/de/suchergebnisse?query=%'
    AND query != ''
    AND user_device IN ('desktop', 'tablet', 'mobile')  -- Exclude app users
    AND user_id != 0  -- Exclude anonymous users
),

-- Get the first search per session per query to avoid duplicates
first_search_per_session_query AS (
  SELECT 
    date,
    session_id,
    query,
    user_id,
    user_device,
    MIN(time) AS first_search_time
  FROM regular_search_events
  GROUP BY date, session_id, query, user_id, user_device
),

-- Get order data
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

-- Get purchase events (also filter by device and user_id)
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
    AND user_device IN ('desktop', 'tablet', 'mobile')  -- Consistent filtering
    AND user_id != 0  -- Exclude anonymous users
),

-- Create base table with all searches (converting and non-converting)
all_searches AS (
  SELECT 
    fs.date,
    fs.query,
    fs.session_id,
    fs.user_id,
    fs.user_device,
    fs.first_search_time
  FROM first_search_per_session_query fs
),

-- Find valid conversions: purchases that happen AFTER search in same session
valid_conversions AS (
  SELECT 
    als.date,
    als.query,
    als.session_id,
    als.user_id,
    als.user_device,
    als.first_search_time,
    pe.purchase_id,
    pe.time as purchase_time,
    od.final_price,
    od.number as order_number,
    TIMESTAMP_DIFF(pe.time, als.first_search_time, SECOND) AS seconds_after_search
  FROM all_searches als
  INNER JOIN purchase_events pe ON als.date = pe.date 
    AND als.session_id = pe.session_id
    AND als.user_id = pe.user_id  -- Additional user matching
  INNER JOIN order_data od ON CAST(pe.purchase_id AS STRING) = CAST(od.number AS STRING)
    AND pe.user_id = od.user_id  -- Ensure purchase belongs to same user
  WHERE pe.time > als.first_search_time  -- Purchase MUST be after search
    AND TIMESTAMP_DIFF(pe.time, als.first_search_time, SECOND) > 0  -- Positive time difference
),

-- Calculate metrics per query
query_metrics AS (
  SELECT 
    als.date,
    als.query,
    COUNT(DISTINCT als.session_id) AS total_sessions,
    COUNT(DISTINCT vc.session_id) AS converting_sessions,
    COUNT(DISTINCT vc.order_number) AS total_orders,
    SUM(vc.final_price) AS total_gmv,
    AVG(vc.final_price) AS avg_order_value,
    AVG(vc.seconds_after_search) AS avg_seconds_to_conversion
  FROM all_searches als
  LEFT JOIN valid_conversions vc ON als.date = vc.date 
    AND als.query = vc.query 
    AND als.session_id = vc.session_id
    AND als.user_id = vc.user_id
  GROUP BY als.date, als.query
),

-- Calculate derived metrics and rank by conversion performance
ranked_queries AS (
  SELECT 
    qm.*,
    ROUND((qm.converting_sessions / qm.total_sessions) * 100, 2) AS conversion_rate,
    ROUND(COALESCE(qm.total_gmv, 0) / qm.total_sessions, 2) AS gmv_per_session,
    ROUND(COALESCE(qm.avg_order_value, 0), 2) AS aov,
    ROUND(COALESCE(qm.avg_seconds_to_conversion, 0) / 60, 2) AS avg_minutes_to_conversion,
    -- Rank by conversion performance instead of pure GMV
    ROW_NUMBER() OVER (
      PARTITION BY qm.date 
      ORDER BY qm.total_orders DESC, (qm.converting_sessions / qm.total_sessions) DESC, qm.total_sessions DESC
    ) AS performance_rank
  FROM query_metrics qm
  WHERE qm.total_sessions >= 3  -- Only include queries with meaningful volume
    AND qm.total_orders >= 1  -- Only queries that actually converted
)

-- Final results showing top performing queries by conversion metrics
SELECT 
  date AS day,
  performance_rank,
  query,
  total_sessions,
  converting_sessions,
  total_orders,
  conversion_rate,
  ROUND(COALESCE(total_gmv, 0), 2) AS total_gmv,
  gmv_per_session,
  aov,
  avg_minutes_to_conversion,
  -- Validation metrics
  ROUND(CASE 
    WHEN total_orders > 0 THEN total_gmv / total_orders 
    ELSE 0 
  END, 2) AS gmv_per_order,
  ROUND(CASE 
    WHEN converting_sessions > 0 THEN total_orders / converting_sessions 
    ELSE 0 
  END, 2) AS orders_per_converting_session
FROM ranked_queries
WHERE performance_rank <= 10  -- Top 10 best converting queries per day
ORDER BY date, performance_rank;