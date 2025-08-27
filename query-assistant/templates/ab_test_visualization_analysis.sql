WITH 
-- Order data for GMV and AOV calculations
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

-- Filter events for the A/B test and time period
filtered_events AS (
  SELECT 
    session_id,
    user_id,
    type,
    extra,
    page_url,
    time,
    purchase_id,
    ab_tests_key,
    ab_tests_value
  FROM `gtm-eduki-com.QE.events`
  WHERE date >= '2025-08-06'
    AND world = 'de'
    AND EXISTS(
      SELECT 1 
      FROM UNNEST(ab_tests_key) AS k WITH OFFSET i 
      JOIN UNNEST(ab_tests_value) AS v WITH OFFSET j ON i = j 
      WHERE k = 'CVC' AND v IN ('B: Cart group', 'C: Cart on Preview')
    )
),

-- Extract A/B test variant for each session
session_variants AS (
  SELECT DISTINCT
    session_id,
    CASE 
      WHEN EXISTS(
        SELECT 1 
        FROM UNNEST(ab_tests_key) AS k WITH OFFSET i 
        JOIN UNNEST(ab_tests_value) AS v WITH OFFSET j ON i = j 
        WHERE k = 'CVC' AND v = 'B: Cart group'
      ) THEN 'B: Cart group'
      WHEN EXISTS(
        SELECT 1 
        FROM UNNEST(ab_tests_key) AS k WITH OFFSET i 
        JOIN UNNEST(ab_tests_value) AS v WITH OFFSET j ON i = j 
        WHERE k = 'CVC' AND v = 'C: Cart on Preview'
      ) THEN 'C: Cart on Preview'
    END AS variant
  FROM filtered_events
  WHERE EXISTS(
    SELECT 1 
    FROM UNNEST(ab_tests_key) AS k WITH OFFSET i 
    JOIN UNNEST(ab_tests_value) AS v WITH OFFSET j ON i = j 
    WHERE k = 'CVC' AND v IN ('B: Cart group', 'C: Cart on Preview')
  )
),

-- Get visualization type events
visualization_events AS (
  SELECT 
    session_id,
    extra AS visualization_type
  FROM filtered_events
  WHERE extra IN ('"listView"', '"gridView"')
),

-- Calculate session-level metrics
session_metrics AS (
  SELECT 
    sv.session_id,
    sv.variant,
    ve.visualization_type,
    
    -- Add to favorites from search page
    COUNTIF(fe.type = 'addToFavorites' AND fe.page_url LIKE 'https://eduki.com/de/suchergebnisse%') AS add_to_favorites,
    
    -- Remove from favorites from search page
    COUNTIF(fe.type = 'removeFromFavorites' AND fe.page_url LIKE 'https://eduki.com/de/suchergebnisse%') AS remove_from_favorites,
    
    -- Add to cart from search page
    COUNTIF(fe.type = 'addToCart' AND fe.page_url LIKE 'https://eduki.com/de/suchergebnisse%') AS add_to_cart,
    

    
    -- Get timestamps for conversion analysis
    ARRAY_AGG(
      CASE WHEN fe.type = 'addToFavorites' AND fe.page_url LIKE 'https://eduki.com/de/suchergebnisse%' 
           THEN fe.time END 
      IGNORE NULLS
    ) AS favorites_times,
    
    ARRAY_AGG(
      CASE WHEN fe.type = 'addToCart' AND fe.page_url LIKE 'https://eduki.com/de/suchergebnisse%' 
           THEN fe.time END 
      IGNORE NULLS
    ) AS cart_times,
    
    ARRAY_AGG(
      CASE WHEN fe.type = 'purchase' 
           THEN fe.time END 
      IGNORE NULLS
    ) AS purchase_times
    
  FROM session_variants sv
  LEFT JOIN visualization_events ve ON sv.session_id = ve.session_id
  LEFT JOIN filtered_events fe ON sv.session_id = fe.session_id
  WHERE ve.visualization_type IS NOT NULL
  GROUP BY sv.session_id, sv.variant, ve.visualization_type
),

-- Calculate session-level GMV separately to avoid JOIN issues
session_gmv AS (
  SELECT 
    sv.session_id,
    sv.variant,
    ve.visualization_type,
    SUM(od.final_price) AS total_session_gmv
  FROM session_variants sv
  LEFT JOIN visualization_events ve ON sv.session_id = ve.session_id
  LEFT JOIN filtered_events fe ON sv.session_id = fe.session_id AND fe.type = 'purchase'
  LEFT JOIN order_data od ON CAST(fe.purchase_id AS STRING) = CAST(od.number AS STRING)
  WHERE ve.visualization_type IS NOT NULL
  GROUP BY sv.session_id, sv.variant, ve.visualization_type
),

-- Calculate individual order values for AOV
individual_orders AS (
  SELECT 
    sv.variant,
    ve.visualization_type,
    od.final_price
  FROM session_variants sv
  LEFT JOIN visualization_events ve ON sv.session_id = ve.session_id
  LEFT JOIN filtered_events fe ON sv.session_id = fe.session_id AND fe.type = 'purchase'
  LEFT JOIN order_data od ON CAST(fe.purchase_id AS STRING) = CAST(od.number AS STRING)
  WHERE ve.visualization_type IS NOT NULL 
    AND od.final_price IS NOT NULL
),

-- Calculate conversion times
conversion_metrics AS (
  SELECT 
    sm.session_id,
    sm.variant,
    sm.visualization_type,
    sm.add_to_favorites,
    sm.remove_from_favorites,
    sm.add_to_cart,
    COALESCE(sg.total_session_gmv, 0) AS session_gmv,
    
    -- Time to conversion after adding to favorites (in minutes)
    CASE 
      WHEN ARRAY_LENGTH(favorites_times) > 0 AND ARRAY_LENGTH(purchase_times) > 0
      THEN (
        SELECT MIN(DATETIME_DIFF(purchase_time, favorite_time, MINUTE))
        FROM UNNEST(sm.purchase_times) AS purchase_time
        CROSS JOIN UNNEST(sm.favorites_times) AS favorite_time
        WHERE purchase_time > favorite_time
      )
    END AS conversion_after_favorites_minutes,
    
    -- Time to conversion after adding to cart (in minutes)
    CASE 
      WHEN ARRAY_LENGTH(sm.cart_times) > 0 AND ARRAY_LENGTH(sm.purchase_times) > 0
      THEN (
        SELECT MIN(DATETIME_DIFF(purchase_time, cart_time, MINUTE))
        FROM UNNEST(sm.purchase_times) AS purchase_time
        CROSS JOIN UNNEST(sm.cart_times) AS cart_time
        WHERE purchase_time > cart_time
      )
    END AS conversion_after_cart_minutes
    
  FROM session_metrics sm
  LEFT JOIN session_gmv sg ON sm.session_id = sg.session_id 
    AND sm.variant = sg.variant 
    AND sm.visualization_type = sg.visualization_type
)

-- Final aggregated results
SELECT 
  cm.variant,
  cm.visualization_type,
  COUNT(*) AS total_number_visualization_type,
  
  -- Total sessions calculation (sessions with any visualization type)
  (SELECT COUNT(DISTINCT sv.session_id) 
   FROM session_variants sv 
   JOIN visualization_events ve ON sv.session_id = ve.session_id 
   WHERE sv.variant = cm.variant) AS total_sessions,
  
  -- Percentage of sessions
  ROUND(
    COUNT(*) * 100.0 / 
    (SELECT COUNT(DISTINCT sv.session_id) 
     FROM session_variants sv 
     JOIN visualization_events ve ON sv.session_id = ve.session_id 
     WHERE sv.variant = cm.variant), 
    2
  ) AS percentage_of_sessions,
  
  -- Aggregate metrics
  SUM(cm.add_to_favorites) AS add2Favorites,
  SUM(cm.remove_from_favorites) AS removeFromFavorites,
  SUM(cm.add_to_cart) AS add2Cart,
  
  -- Average conversion times
  ROUND(AVG(cm.conversion_after_favorites_minutes), 2) AS conversion_after_favorites,
  ROUND(AVG(cm.conversion_after_cart_minutes), 2) AS conversion_after_cart,
  
  -- CORRECTED GMV and AOV calculations
  ROUND(SUM(cm.session_gmv) / COUNT(DISTINCT cm.session_id), 2) AS gmv_per_session,
  ROUND((SELECT AVG(io.final_price) 
         FROM individual_orders io 
         WHERE io.variant = cm.variant 
           AND io.visualization_type = cm.visualization_type), 2) AS aov

FROM conversion_metrics cm
GROUP BY cm.variant, cm.visualization_type
ORDER BY cm.variant, cm.visualization_type;
