-- DSR A/B Test - Suggestion-Only Sessions Performance Analysis
-- Analyzes CTR, CTR@K, CR/search, and GMV/session for sessions using ONLY search suggestions
-- Split by DSR A/B test variants
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
    e.query,
    e.time,
    e.position,
    e.source,
    e.internal_path,
    e.ab_tests_key,
    e.ab_tests_value
  FROM `gtm-eduki-com.QE.events` e
  WHERE e.date >= '2025-10-03'
    AND e.world IN ('de', 'es', 'it', 'gr')
    AND e.user_device IN ('desktop', 'mobile', 'tablet')
),

mp_sessions AS (
  SELECT DISTINCT session_id, user_id
  FROM mp_events mp
  WHERE (
    (mp.world = 'de' AND mp.page_url LIKE 'https://eduki.com/de/suchergebnisse%')
    OR (mp.world = 'es' AND mp.page_url LIKE 'https://eduki.com/es/resultados-busqueda%')
    OR (mp.world = 'it' AND mp.page_url LIKE 'https://eduki.com/it/risultati-della-ricerca%')
    OR (mp.world = 'gr' AND mp.page_url LIKE 'https://eduki.com/gr/search-results%')
    OR mp.page_url LIKE '%Search%'
  )
    AND mp.query != '' AND mp.query IS NOT NULL
    AND mp.type = 'appearedInSearch'
    AND mp.world IN ('de', 'es', 'it', 'gr')
),

ab_assign AS (
  -- Get DSR A/B test assignments
  SELECT
    s.session_id,
    s.user_id,
    ANY_VALUE(ab_value) AS variant
  FROM `gtm-eduki-com.QE.events` e
  INNER JOIN mp_sessions s USING (session_id, user_id)
  CROSS JOIN UNNEST(e.ab_tests_key)  AS ab_key WITH OFFSET key_offset
  CROSS JOIN UNNEST(e.ab_tests_value) AS ab_value WITH OFFSET value_offset
  WHERE e.date >= '2025-10-03'
    AND key_offset = value_offset
    AND ab_key = 'DSR2'
    AND e.world IN ('de', 'es', 'it', 'gr')
  GROUP BY s.session_id, s.user_id
),

search_events AS (
  -- Count all appearedInSearch events
  SELECT
    session_id,
    user_id,
    world,
    variant,
    COUNT(*) AS total_search_events
  FROM mp_events
  INNER JOIN ab_assign USING (session_id, user_id)
  WHERE type = 'appearedInSearch'
    AND (
      (world = 'de' AND (page_url LIKE 'https://eduki.com/de/suchergebnisse%' OR page_url LIKE '%Search%'))
      OR (world = 'es' AND page_url LIKE 'https://eduki.com/es/resultados-busqueda%')
      OR (world = 'it' AND page_url LIKE 'https://eduki.com/it/risultati-della-ricerca%')
      OR (world = 'gr' AND page_url LIKE 'https://eduki.com/gr/search-results%')
    )
    AND query != ''
    AND query IS NOT NULL
  GROUP BY session_id, user_id, world, variant
),

suggestion_events AS (
  -- Count all selectedSearchSuggestion events
  SELECT
    session_id,
    user_id,
    world,
    variant,
    COUNT(*) AS total_suggestion_events
  FROM mp_events
  INNER JOIN ab_assign USING (session_id, user_id)
  WHERE type = 'selectedSearchSuggestion'
  GROUP BY session_id, user_id, world, variant
),

suggestion_only_sessions AS (
  -- Sessions that have both search events and suggestion events, with A/B test assignment
  SELECT DISTINCT
    s.session_id,
    s.user_id,
    s.world,
    s.variant
  FROM search_events s
  INNER JOIN suggestion_events sug 
    ON s.session_id = sug.session_id 
    AND s.user_id = sug.user_id
    AND s.world = sug.world
    AND s.variant = sug.variant
),

session_clicks AS (
  -- Calculate CTR metrics for suggestion-only sessions by variant
  SELECT
    s.session_id,
    s.world,
    s.variant,
    COUNT(CASE WHEN e.type = 'click' 
          AND (
            (e.world = 'de' AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse?query=%')
            OR (e.world = 'es' AND e.page_url LIKE 'https://eduki.com/es/resultados-busqueda?query=%')
            OR (e.world = 'it' AND e.page_url LIKE 'https://eduki.com/it/risultati-della-ricerca?query=%')
            OR (e.world = 'gr' AND e.page_url LIKE 'https://eduki.com/gr/search-results?query=%')
          )
          AND e.source = 'search' THEN 1 END) AS total_clicks,
    COUNT(CASE WHEN e.type = 'click' 
          AND (
            (e.world = 'de' AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse?query=%')
            OR (e.world = 'es' AND e.page_url LIKE 'https://eduki.com/es/resultados-busqueda?query=%')
            OR (e.world = 'it' AND e.page_url LIKE 'https://eduki.com/it/risultati-della-ricerca?query=%')
            OR (e.world = 'gr' AND e.page_url LIKE 'https://eduki.com/gr/search-results?query=%')
          )
          AND e.source = 'search'
          AND e.position = 1 THEN 1 END) AS clicks_at_1,
    COUNT(CASE WHEN e.type = 'click' 
          AND (
            (e.world = 'de' AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse?query=%')
            OR (e.world = 'es' AND e.page_url LIKE 'https://eduki.com/es/resultados-busqueda?query=%')
            OR (e.world = 'it' AND e.page_url LIKE 'https://eduki.com/it/risultati-della-ricerca?query=%')
            OR (e.world = 'gr' AND e.page_url LIKE 'https://eduki.com/gr/search-results?query=%')
          )
          AND e.source = 'search'
          AND e.position = 2 THEN 1 END) AS clicks_at_2,
    COUNT(CASE WHEN e.type = 'click' 
          AND (
            (e.world = 'de' AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse?query=%')
            OR (e.world = 'es' AND e.page_url LIKE 'https://eduki.com/es/resultados-busqueda?query=%')
            OR (e.world = 'it' AND e.page_url LIKE 'https://eduki.com/it/risultati-della-ricerca?query=%')
            OR (e.world = 'gr' AND e.page_url LIKE 'https://eduki.com/gr/search-results?query=%')
          )
          AND e.source = 'search'
          AND e.position = 3 THEN 1 END) AS clicks_at_3,
    COUNT(CASE WHEN e.type = 'click' 
          AND (
            (e.world = 'de' AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse?query=%')
            OR (e.world = 'es' AND e.page_url LIKE 'https://eduki.com/es/resultados-busqueda?query=%')
            OR (e.world = 'it' AND e.page_url LIKE 'https://eduki.com/it/risultati-della-ricerca?query=%')
            OR (e.world = 'gr' AND e.page_url LIKE 'https://eduki.com/gr/search-results?query=%')
          )
          AND e.source = 'search'
          AND e.position = 4 THEN 1 END) AS clicks_at_4,
    COUNT(CASE WHEN e.type = 'click' 
          AND (
            (e.world = 'de' AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse?query=%')
            OR (e.world = 'es' AND e.page_url LIKE 'https://eduki.com/es/resultados-busqueda?query=%')
            OR (e.world = 'it' AND e.page_url LIKE 'https://eduki.com/it/risultati-della-ricerca?query=%')
            OR (e.world = 'gr' AND e.page_url LIKE 'https://eduki.com/gr/search-results?query=%')
          )
          AND e.source = 'search'
          AND e.position = 5 THEN 1 END) AS clicks_at_5,
    COUNT(CASE WHEN e.type = 'click' 
          AND (
            (e.world = 'de' AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse?query=%')
            OR (e.world = 'es' AND e.page_url LIKE 'https://eduki.com/es/resultados-busqueda?query=%')
            OR (e.world = 'it' AND e.page_url LIKE 'https://eduki.com/it/risultati-della-ricerca?query=%')
            OR (e.world = 'gr' AND e.page_url LIKE 'https://eduki.com/gr/search-results?query=%')
          )
          AND e.source = 'search'
          AND e.position BETWEEN 6 AND 12 THEN 1 END) AS clicks_at_6_12,
    COUNT(CASE WHEN e.type = 'appearedInSearch' THEN 1 END) AS total_searches
  FROM suggestion_only_sessions s
  LEFT JOIN mp_events e
    ON s.session_id = e.session_id
    AND s.world = e.world
  WHERE e.d_local >= '2025-10-03'
  GROUP BY s.session_id, s.world, s.variant
),

purchase_map AS (
  -- Orders seen in any event of those sessions, within the window
  SELECT DISTINCT
    s.session_id,
    s.user_id,
    CAST(e.purchase_id AS STRING) AS order_number
  FROM `gtm-eduki-com.QE.events` e
  INNER JOIN suggestion_only_sessions s USING (session_id, user_id)
  WHERE e.date >= '2025-10-03'
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
    s.session_id,
    s.user_id,
    s.variant,
    COUNT(DISTINCT o.order_number) AS orders,
    SUM(o.gmv) AS gmv
  FROM suggestion_only_sessions s
  LEFT JOIN purchase_map pm USING (session_id, user_id)
  LEFT JOIN orders o
    ON o.order_number = pm.order_number
   AND o.user_id = pm.user_id
  GROUP BY s.session_id, s.user_id, s.variant
),

variant_performance AS (
  SELECT
    c.world,
    c.variant,
    COUNT(DISTINCT c.session_id) AS total_suggestion_search_sessions,
    SUM(c.total_searches) AS total_searches,
    SUM(c.total_clicks) AS total_clicks,
    SUM(c.clicks_at_1) AS clicks_at_1,
    SUM(c.clicks_at_2) AS clicks_at_2,
    SUM(c.clicks_at_3) AS clicks_at_3,
    SUM(c.clicks_at_4) AS clicks_at_4,
    SUM(c.clicks_at_5) AS clicks_at_5,
    SUM(c.clicks_at_6_12) AS clicks_at_6_12,
    COUNT(DISTINCT CASE WHEN r.orders > 0 THEN c.session_id END) AS sessions_with_purchases,
    SUM(COALESCE(r.gmv, 0)) AS total_gmv,
    SUM(COALESCE(r.orders, 0)) AS total_orders
  FROM session_clicks c
  LEFT JOIN session_revenue r ON c.session_id = r.session_id AND c.variant = r.variant
  GROUP BY c.world, c.variant
)

SELECT
  world,
  variant,
  total_suggestion_search_sessions,
  ROUND((total_clicks * 100.0 / total_searches), 2) AS ctr_overall,
  ROUND((clicks_at_1 * 100.0 / total_searches), 2) AS ctr_at_1,
  ROUND((clicks_at_2 * 100.0 / total_searches), 2) AS ctr_at_2,
  ROUND((clicks_at_3 * 100.0 / total_searches), 2) AS ctr_at_3,
  ROUND((clicks_at_4 * 100.0 / total_searches), 2) AS ctr_at_4,
  ROUND((clicks_at_5 * 100.0 / total_searches), 2) AS ctr_at_5,
  ROUND((clicks_at_6_12 * 100.0 / total_searches), 2) AS ctr_at_6_12,
  ROUND((sessions_with_purchases * 100.0 / total_suggestion_search_sessions), 2) AS cr_per_search,
  ROUND((total_gmv / total_suggestion_search_sessions), 2) AS gmv_per_session,
  ROUND(SAFE_DIVIDE(total_gmv, NULLIF(total_orders, 0)), 2) AS aov
FROM variant_performance
ORDER BY world, variant;