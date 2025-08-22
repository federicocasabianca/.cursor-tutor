-- A/B Test Performance Summary Query
-- Target: BigQuery
-- Project: gtm-eduki-com
-- Dataset: QE
-- A/B Test: CVC with variants 'A: Original', 'B: Cart group', 'C: Cart on Preview'

WITH order_data AS (
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

session_events AS (
  SELECT 
    session_id,
    user_id,
    -- Extract A/B test variant using proper array handling
    CASE 
      WHEN EXISTS(
        SELECT 1 FROM UNNEST(ab_tests_key) AS k WITH OFFSET i 
        JOIN UNNEST(ab_tests_value) AS v WITH OFFSET j ON i = j 
        WHERE k = 'CVC' AND v = 'A: Original'
      ) THEN 'A: Original'
      WHEN EXISTS(
        SELECT 1 FROM UNNEST(ab_tests_key) AS k WITH OFFSET i 
        JOIN UNNEST(ab_tests_value) AS v WITH OFFSET j ON i = j 
        WHERE k = 'CVC' AND v = 'B: Cart group'
      ) THEN 'B: Cart group'
      WHEN EXISTS(
        SELECT 1 FROM UNNEST(ab_tests_key) AS k WITH OFFSET i 
        JOIN UNNEST(ab_tests_value) AS v WITH OFFSET j ON i = j 
        WHERE k = 'CVC' AND v = 'C: Cart on Preview'
      ) THEN 'C: Cart on Preview'
      ELSE 'Unknown'
    END AS ab_test_variant,
    
    -- Count different event types per session
    COUNTIF(type = 'appearedInSearch' AND page_url LIKE 'https://eduki.com/de/suchergebnisse%') AS searches,
    COUNTIF(type = 'click' AND page_url LIKE 'https://eduki.com/de/suchergebnisse%' AND source = 'search' AND internal_path = 'sp' AND item_id IS NOT NULL AND position IS NOT NULL) AS clicks_to_mp,
    COUNTIF(type = 'addToFavorites') AS add_to_favorites,
    COUNTIF(type = 'addToCart') AS add_to_cart,
    COUNTIF(type = 'purchase') AS purchases
    
  FROM `gtm-eduki-com.QE.events`
  WHERE date >= '2025-08-06'
    AND EXISTS(
      SELECT 1 FROM UNNEST(ab_tests_key) AS k WITH OFFSET i 
      JOIN UNNEST(ab_tests_value) AS v WITH OFFSET j ON i = j 
      WHERE k = 'CVC' AND v IN ('A: Original', 'B: Cart group', 'C: Cart on Preview')
    )
  GROUP BY session_id, user_id, ab_test_variant
),

session_gmv AS (
  SELECT 
    se.session_id,
    se.ab_test_variant,
    SUM(COALESCE(od.final_price, 0)) AS total_gmv
  FROM session_events se
  LEFT JOIN `gtm-eduki-com.QE.events` e ON se.session_id = e.session_id AND e.type = 'purchase' AND e.date >= '2025-08-06'
  LEFT JOIN order_data od ON CAST(e.purchase_id AS STRING) = CAST(od.number AS STRING)
  WHERE se.ab_test_variant != 'Unknown'
  GROUP BY se.session_id, se.ab_test_variant
),

variant_summary AS (
  SELECT 
    se.ab_test_variant,
    COUNT(DISTINCT se.session_id) AS total_sessions,
    COUNT(DISTINCT se.session_id) * 100.0 / SUM(COUNT(DISTINCT se.session_id)) OVER () AS percentage_of_sessions,
    SUM(se.searches) AS total_searches,
    SUM(se.clicks_to_mp) AS total_clicks_to_mp,
    SUM(se.add_to_favorites) AS total_add_to_favorites,
    SUM(se.add_to_cart) AS total_add_to_cart,
    SUM(se.purchases) AS total_purchases,
    COALESCE(SUM(sg.total_gmv), 0) AS total_gmv
  FROM session_events se
  LEFT JOIN session_gmv sg ON se.session_id = sg.session_id
  WHERE se.ab_test_variant != 'Unknown'
  GROUP BY se.ab_test_variant
)

SELECT 
  ab_test_variant,
  total_sessions,
  ROUND(percentage_of_sessions, 2) AS percentage_of_sessions,
  total_searches,
  -- Calculate rates using total_sessions as denominator
  ROUND(SAFE_DIVIDE(total_clicks_to_mp, total_searches) * 100, 2) AS CTR_to_MP,
  ROUND(SAFE_DIVIDE(total_add_to_favorites, total_sessions) * 100, 2) AS A2F_rate,
  ROUND(SAFE_DIVIDE(total_add_to_cart, total_sessions) * 100, 2) AS A2C_rate,
  ROUND(SAFE_DIVIDE(total_purchases, total_sessions) * 100, 2) AS conversion_rate,
  ROUND(SAFE_DIVIDE(total_gmv, total_sessions), 2) AS gmv_per_session
FROM variant_summary
ORDER BY 
  CASE ab_test_variant
    WHEN 'A: Original' THEN 1
    WHEN 'B: Cart group' THEN 2
    WHEN 'C: Cart on Preview' THEN 3
    ELSE 4
  END;
