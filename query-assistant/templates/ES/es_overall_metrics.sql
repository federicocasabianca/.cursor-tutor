WITH total_sessions AS (
  SELECT 
    COUNT(DISTINCT session_id) as total_sessions
  FROM `gtm-eduki-com.QE.events`
  WHERE date >= '2025-08-01' 
    AND world = 'es'
),

search_sessions AS (
  SELECT 
    session_id,
    COUNT(*) as search_events
  FROM `gtm-eduki-com.QE.events`
  WHERE date >= '2025-08-01' 
    AND world = 'es'
    AND type = 'appearedInSearch' 
    AND page_url LIKE 'https://eduki.com/es/resultados-busqueda%'
  GROUP BY session_id
),

click_events AS (
  SELECT 
    session_id,
    position,
    COUNT(*) as clicks,
    CASE 
      WHEN position = 1 THEN 'position_1'
      WHEN position = 2 THEN 'position_2'
      WHEN position = 3 THEN 'position_3'
      WHEN position = 4 THEN 'position_4'
      WHEN position = 5 THEN 'position_5'
      WHEN position BETWEEN 6 AND 15 THEN 'position_6_15'
      WHEN position BETWEEN 16 AND 25 THEN 'position_16_25'
      WHEN position BETWEEN 26 AND 36 THEN 'position_26_36'
      ELSE 'other'
    END as position_group
  FROM `gtm-eduki-com.QE.events`
  WHERE date >= '2025-08-01' 
    AND world = 'es'
    AND type = 'click' 
    AND page_url LIKE 'https://eduki.com/es/resultados-busqueda%' 
    AND source = 'search'
    AND position IS NOT NULL
  GROUP BY session_id, position
),

session_purchases AS (
  -- Get all purchase events for search sessions and join with order data for AOV
  SELECT 
    rs.session_id,
    e.purchase_id,
    SUM(COALESCE(e.item_price, 0)) as session_gmv_events,
    -- Get order-level data for AOV calculation
    SUM(COALESCE(fo.final_price, 0)) as session_gmv_orders,
    COUNT(DISTINCT e.purchase_id) as order_count
  FROM 
    search_sessions rs
  INNER JOIN 
    `gtm-eduki-com.QE.events` e 
    ON rs.session_id = e.session_id
  LEFT JOIN (
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
  ) fo ON CAST(e.purchase_id AS STRING) = CAST(fo.number AS STRING)
  WHERE 
    e.date >= '2025-08-01'
    AND e.world = 'es'
    AND e.type = 'purchase'
  GROUP BY rs.session_id, e.purchase_id
),

session_metrics AS (
  SELECT 
    ss.session_id,
    ss.search_events,
    -- Click events for this session
    COUNT(DISTINCT ce.session_id) as has_clicks,
    -- Position-specific clicks
    SUM(CASE WHEN ce.position_group = 'position_1' THEN ce.clicks ELSE 0 END) as clicks_position_1,
    SUM(CASE WHEN ce.position_group = 'position_2' THEN ce.clicks ELSE 0 END) as clicks_position_2,
    SUM(CASE WHEN ce.position_group = 'position_3' THEN ce.clicks ELSE 0 END) as clicks_position_3,
    SUM(CASE WHEN ce.position_group = 'position_4' THEN ce.clicks ELSE 0 END) as clicks_position_4,
    SUM(CASE WHEN ce.position_group = 'position_5' THEN ce.clicks ELSE 0 END) as clicks_position_5,
    SUM(CASE WHEN ce.position_group = 'position_6_15' THEN ce.clicks ELSE 0 END) as clicks_position_6_15,
    SUM(CASE WHEN ce.position_group = 'position_16_25' THEN ce.clicks ELSE 0 END) as clicks_position_16_25,
    SUM(CASE WHEN ce.position_group = 'position_26_36' THEN ce.clicks ELSE 0 END) as clicks_position_26_36,
    -- Purchase events for this session
    COUNT(DISTINCT sp.session_id) as has_purchase,
    -- Revenue and order count for this session
    COALESCE(SUM(sp.session_gmv_orders), 0) as session_revenue,
    SUM(sp.order_count) as session_order_count
  FROM search_sessions ss
  LEFT JOIN click_events ce ON ss.session_id = ce.session_id
  LEFT JOIN session_purchases sp ON ss.session_id = sp.session_id
  GROUP BY ss.session_id, ss.search_events
),

final_metrics AS (
  SELECT 
    'es' as world,
    ABS(DATE_DIFF('2025-08-01', CURRENT_DATE(), DAY)) as number_of_days,
    ts.total_sessions,
    COUNT(DISTINCT sm.session_id) as total_search_sessions,
    COUNT(DISTINCT CASE WHEN sm.has_clicks > 0 THEN sm.session_id END) as click_sessions,
    
    -- CTR SRP to MP (Click-through rate from search results page to material page)
    ROUND(
      (COUNT(DISTINCT CASE WHEN sm.has_clicks > 0 THEN sm.session_id END) / 
       NULLIF(COUNT(DISTINCT sm.session_id), 0)) * 100, 2
    ) as ctr_srp_to_mp,
    
    -- CTR@k for different positions (using total_search_sessions as denominator)
    ROUND(
      (SUM(sm.clicks_position_1) / NULLIF(COUNT(DISTINCT sm.session_id), 0)) * 100, 2
    ) as ctr_position_1,
    
    ROUND(
      (SUM(sm.clicks_position_2) / NULLIF(COUNT(DISTINCT sm.session_id), 0)) * 100, 2
    ) as ctr_position_2,
    
    ROUND(
      (SUM(sm.clicks_position_3) / NULLIF(COUNT(DISTINCT sm.session_id), 0)) * 100, 2
    ) as ctr_position_3,
    
    ROUND(
      (SUM(sm.clicks_position_4) / NULLIF(COUNT(DISTINCT sm.session_id), 0)) * 100, 2
    ) as ctr_position_4,
    
    ROUND(
      (SUM(sm.clicks_position_5) / NULLIF(COUNT(DISTINCT sm.session_id), 0)) * 100, 2
    ) as ctr_position_5,
    
    ROUND(
      (SUM(sm.clicks_position_6_15) / NULLIF(COUNT(DISTINCT sm.session_id), 0)) * 100, 2
    ) as ctr_position_6_15,
    
    ROUND(
      (SUM(sm.clicks_position_16_25) / NULLIF(COUNT(DISTINCT sm.session_id), 0)) * 100, 2
    ) as ctr_position_16_25,
    
    ROUND(
      (SUM(sm.clicks_position_26_36) / NULLIF(COUNT(DISTINCT sm.session_id), 0)) * 100, 2
    ) as ctr_position_26_36,
    
    -- Conversion Rate (CR) - based on search sessions
    ROUND(
      (COUNT(DISTINCT CASE WHEN sm.has_purchase > 0 THEN sm.session_id END) / 
       NULLIF(COUNT(DISTINCT sm.session_id), 0)) * 100, 2
    ) as conversion_rate,
    
    -- Average Order Value (AOV) - Total Revenue / Total Number of Orders
    ROUND(
      CASE 
        WHEN SUM(sm.session_order_count) > 0 
        THEN COALESCE(SUM(sm.session_revenue), 0) / SUM(sm.session_order_count)
        ELSE 0 
      END, 2
    ) as aov,
    
    -- GMV per session - Total Revenue / Total Sessions (not just search sessions)
    ROUND(
      SUM(sm.session_revenue) / NULLIF(ts.total_sessions, 0), 2
    ) as gmv_per_session
    
  FROM total_sessions ts
  CROSS JOIN session_metrics sm
  GROUP BY ts.total_sessions
)

SELECT 
  world,
  number_of_days,
  total_sessions,
  total_search_sessions,
  click_sessions,
  ctr_srp_to_mp,
  ctr_position_1,
  ctr_position_2,
  ctr_position_3,
  ctr_position_4,
  ctr_position_5,
  ctr_position_6_15,
  ctr_position_16_25,
  ctr_position_26_36,
  conversion_rate,
  aov,
  gmv_per_session
FROM final_metrics