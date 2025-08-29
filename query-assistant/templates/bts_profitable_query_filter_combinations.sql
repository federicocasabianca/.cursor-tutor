-- Back-To-School (BTS) Most Profitable Query + Filter Combinations
-- Period: 2025-08-24 to 2025-08-27
-- Project: gtm-eduki-com, Dataset: QE, Table: events
-- Focus: Identify most profitable search query and filter combinations per day

WITH regular_search_events AS (
  SELECT 
    date,
    session_id,
    page_url,
    time,
    query,
    query_params_key,
    query_params_value
  FROM `gtm-eduki-com.QE.events`
  WHERE date BETWEEN '2025-08-24' AND '2025-08-27'
    AND world = 'de'
    AND type = 'appearedInSearch'
    AND page_url LIKE 'https://eduki.com/de/suchergebnisse?query=%'
    AND query != ''
),

-- Extract filters applied with each search query
query_filter_combinations AS (
  SELECT 
    rse.date,
    rse.session_id,
    rse.query,
    rse.time,
    rse.page_url,
    param_key AS filter_type,
    param_value AS filter_value,
    CASE
      WHEN param_key = 't' THEN 'Subject'
      WHEN param_key = 'c' THEN 'Class Grade'
      WHEN param_key = 'prc' THEN 'Price'
      WHEN param_key = 's' THEN 'Sorting'
      WHEN param_key = 'sale' THEN 'Sale'
      WHEN param_key = 'mt' THEN 'Material Type'
      WHEN param_key = 'b' THEN 'Materialumfang'
      WHEN param_key = 'f' THEN 'Materialformat'
      WHEN param_key = 'ft' THEN 'Dateiformat'
      WHEN param_key = 'ly' THEN 'Learning Years'
      WHEN param_key = 'tj' THEN 'Tag'
      WHEN param_key = 'tp' THEN 'Seiten'
      ELSE param_key
    END AS filter_name
  FROM regular_search_events rse
  CROSS JOIN UNNEST(rse.query_params_key) AS param_key WITH OFFSET i
  CROSS JOIN UNNEST(rse.query_params_value) AS param_value WITH OFFSET j
  WHERE i = j  -- Match key with corresponding value
    AND param_key IN ('t', 'c', 'prc', 's', 'sale', 'mt', 'b', 'f', 'ft', 'ly', 'tj', 'tp')
    AND param_key != 'query'  -- Exclude the query parameter itself
),

-- Create combinations of query + all filters used in that search
session_query_filter_combinations AS (
  SELECT 
    qfc.date,
    qfc.session_id,
    qfc.query,
    qfc.time,
    STRING_AGG(
      CONCAT(qfc.filter_name, ':', qfc.filter_value), 
      ' | ' 
      ORDER BY qfc.filter_name
    ) AS filters_applied,
    COUNT(DISTINCT qfc.filter_type) AS num_filters_applied
  FROM query_filter_combinations qfc
  GROUP BY qfc.date, qfc.session_id, qfc.query, qfc.time
),

-- Also include searches without any filters
searches_without_filters AS (
  SELECT 
    rse.date,
    rse.session_id,
    rse.query,
    rse.time,
    'No Filters' AS filters_applied,
    0 AS num_filters_applied
  FROM regular_search_events rse
  WHERE ARRAY_LENGTH(rse.query_params_key) = 1  -- Only has 'query' parameter
    OR NOT EXISTS (
      SELECT 1 
      FROM UNNEST(rse.query_params_key) AS param_key
      WHERE param_key IN ('t', 'c', 'prc', 's', 'sale', 'mt', 'b', 'f', 'ft', 'ly', 'tj', 'tp')
    )
),

-- Combine all query + filter combinations
all_query_combinations AS (
  SELECT * FROM session_query_filter_combinations
  UNION ALL
  SELECT * FROM searches_without_filters
),

-- Get order data for revenue calculations
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

-- Track purchases that happen after these query + filter combinations
purchase_events AS (
  SELECT 
    date,
    session_id,
    purchase_id,
    time
  FROM `gtm-eduki-com.QE.events`
  WHERE date BETWEEN '2025-08-24' AND '2025-08-27'
    AND world = 'de'
    AND type = 'purchase'
    AND purchase_id IS NOT NULL
),

-- Calculate profitability metrics for each query + filter combination
combination_metrics AS (
  SELECT 
    aqc.date,
    aqc.query,
    aqc.filters_applied,
    aqc.num_filters_applied,
    COUNT(DISTINCT aqc.session_id) AS total_sessions,
    COUNT(DISTINCT CASE WHEN pe.session_id IS NOT NULL THEN aqc.session_id END) AS converting_sessions,
    SUM(CASE WHEN pe.session_id IS NOT NULL THEN od.final_price END) AS total_gmv,
    AVG(CASE WHEN pe.session_id IS NOT NULL THEN od.final_price END) AS avg_order_value
  FROM all_query_combinations aqc
  LEFT JOIN purchase_events pe ON aqc.date = pe.date 
    AND aqc.session_id = pe.session_id 
    AND pe.time > aqc.time  -- Purchase after the search
  LEFT JOIN order_data od ON CAST(pe.purchase_id AS STRING) = CAST(od.number AS STRING)
  GROUP BY aqc.date, aqc.query, aqc.filters_applied, aqc.num_filters_applied
),

-- Calculate derived metrics and rank by profitability
ranked_combinations AS (
  SELECT 
    cm.*,
    ROUND((cm.converting_sessions / cm.total_sessions) * 100, 2) AS conversion_rate,
    ROUND(COALESCE(cm.total_gmv, 0) / cm.total_sessions, 2) AS gmv_per_session,
    ROUND(COALESCE(cm.avg_order_value, 0), 2) AS aov,
    ROW_NUMBER() OVER (
      PARTITION BY cm.date 
      ORDER BY COALESCE(cm.total_gmv, 0) DESC, cm.total_sessions DESC
    ) AS profit_rank
  FROM combination_metrics cm
  WHERE cm.total_sessions >= 3  -- Only include combinations with meaningful volume
)

-- Final results showing top profitable combinations per day
SELECT 
  date AS day,
  profit_rank,
  query,
  filters_applied,
  num_filters_applied,
  total_sessions,
  converting_sessions,
  conversion_rate,
  ROUND(total_gmv, 2) AS total_gmv,
  gmv_per_session,
  aov,
  -- Calculate profit score (weighted combination of GMV and conversion rate)
  ROUND(
    (COALESCE(total_gmv, 0) * 0.7) + 
    (conversion_rate * total_sessions * 0.3), 
    2
  ) AS profit_score
FROM ranked_combinations
WHERE profit_rank <= 10  -- Top 10 most profitable combinations per day
ORDER BY date, profit_rank;
