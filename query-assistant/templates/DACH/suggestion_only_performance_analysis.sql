-- Suggestion-Only Sessions Performance Analysis
-- Analyzes CTR, CTR@K, CR/search, and GMV/session for sessions using ONLY search suggestions
-- Target: BigQuery, Project: gtm-eduki-com, Dataset: QE

WITH search_events AS (
  -- Count all appearedInSearch events (same logic as session_search_origin_analysis)
  SELECT
    session_id,
    user_id,
    world,
    COUNT(*) AS total_search_events
  FROM `gtm-eduki-com.QE.events`
  WHERE world IN ('de', 'es', 'it', 'gr')
    AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    AND type = 'appearedInSearch'
    AND (
      (world = 'de' AND (page_url LIKE 'https://eduki.com/de/suchergebnisse%' OR page_url LIKE '%Search%'))
      OR (world = 'es' AND page_url LIKE 'https://eduki.com/es/resultados-busqueda%')
      OR (world = 'it' AND page_url LIKE 'https://eduki.com/it/risultati-della-ricerca%')
      OR (world = 'gr' AND page_url LIKE 'https://eduki.com/gr/search-results%')
    )
    AND query != ''
    AND query IS NOT NULL
    AND user_device IN ('desktop', 'mobile', 'tablet')
  GROUP BY session_id, user_id, world
),

suggestion_events AS (
  -- Count all selectedSearchSuggestion events (same logic as session_search_origin_analysis)
  SELECT
    session_id,
    world,
    COUNT(*) AS total_suggestion_events
  FROM `gtm-eduki-com.QE.events`
  WHERE world IN ('de', 'es', 'it', 'gr')
    AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    AND type = 'selectedSearchSuggestion'
    AND user_device IN ('desktop', 'mobile', 'tablet')
  GROUP BY session_id, world
),

suggestion_only_sessions AS (
  -- Sessions that have both search events and suggestion events
  SELECT DISTINCT
    s.session_id,
    s.user_id,
    s.world
  FROM search_events s
  INNER JOIN suggestion_events sug 
    ON s.session_id = sug.session_id 
    AND s.world = sug.world
),

session_clicks AS (
  -- Calculate CTR metrics for suggestion-only sessions
  SELECT
    s.session_id,
    s.world,
    COUNT(CASE WHEN e.type = 'click' 
          AND (
            (e.world = 'de' AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse?query=%')
            OR (e.world = 'es' AND e.page_url LIKE 'https://eduki.com/es/resultados-busqueda?query=%')
            OR (e.world = 'it' AND e.page_url LIKE 'https://eduki.com/it/risultati-della-ricerca?query=%')
            OR (e.world = 'gr' AND e.page_url LIKE 'https://eduki.com/gr/search-results?query=%')
          )
          AND e.internal_path = 'sp'
          AND e.source = 'search' THEN 1 END) AS total_clicks,
    COUNT(CASE WHEN e.type = 'click' 
          AND (
            (e.world = 'de' AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse?query=%')
            OR (e.world = 'es' AND e.page_url LIKE 'https://eduki.com/es/resultados-busqueda?query=%')
            OR (e.world = 'it' AND e.page_url LIKE 'https://eduki.com/it/risultati-della-ricerca?query=%')
            OR (e.world = 'gr' AND e.page_url LIKE 'https://eduki.com/gr/search-results?query=%')
          )
          AND e.internal_path = 'sp'
          AND e.source = 'search'
          AND e.position = 1 THEN 1 END) AS clicks_at_1,
    COUNT(CASE WHEN e.type = 'click' 
          AND (
            (e.world = 'de' AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse?query=%')
            OR (e.world = 'es' AND e.page_url LIKE 'https://eduki.com/es/resultados-busqueda?query=%')
            OR (e.world = 'it' AND e.page_url LIKE 'https://eduki.com/it/risultati-della-ricerca?query=%')
            OR (e.world = 'gr' AND e.page_url LIKE 'https://eduki.com/gr/search-results?query=%')
          )
          AND e.internal_path = 'sp'
          AND e.source = 'search'
          AND e.position = 2 THEN 1 END) AS clicks_at_2,
    COUNT(CASE WHEN e.type = 'click' 
          AND (
            (e.world = 'de' AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse?query=%')
            OR (e.world = 'es' AND e.page_url LIKE 'https://eduki.com/es/resultados-busqueda?query=%')
            OR (e.world = 'it' AND e.page_url LIKE 'https://eduki.com/it/risultati-della-ricerca?query=%')
            OR (e.world = 'gr' AND e.page_url LIKE 'https://eduki.com/gr/search-results?query=%')
          )
          AND e.internal_path = 'sp'
          AND e.source = 'search'
          AND e.position = 3 THEN 1 END) AS clicks_at_3,
    COUNT(CASE WHEN e.type = 'click' 
          AND (
            (e.world = 'de' AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse?query=%')
            OR (e.world = 'es' AND e.page_url LIKE 'https://eduki.com/es/resultados-busqueda?query=%')
            OR (e.world = 'it' AND e.page_url LIKE 'https://eduki.com/it/risultati-della-ricerca?query=%')
            OR (e.world = 'gr' AND e.page_url LIKE 'https://eduki.com/gr/search-results?query=%')
          )
          AND e.internal_path = 'sp'
          AND e.source = 'search'
          AND e.position = 4 THEN 1 END) AS clicks_at_4,
    COUNT(CASE WHEN e.type = 'click' 
          AND (
            (e.world = 'de' AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse?query=%')
            OR (e.world = 'es' AND e.page_url LIKE 'https://eduki.com/es/resultados-busqueda?query=%')
            OR (e.world = 'it' AND e.page_url LIKE 'https://eduki.com/it/risultati-della-ricerca?query=%')
            OR (e.world = 'gr' AND e.page_url LIKE 'https://eduki.com/gr/search-results?query=%')
          )
          AND e.internal_path = 'sp'
          AND e.source = 'search'
          AND e.position = 5 THEN 1 END) AS clicks_at_5,
    COUNT(CASE WHEN e.type = 'click' 
          AND (
            (e.world = 'de' AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse?query=%')
            OR (e.world = 'es' AND e.page_url LIKE 'https://eduki.com/es/resultados-busqueda?query=%')
            OR (e.world = 'it' AND e.page_url LIKE 'https://eduki.com/it/risultati-della-ricerca?query=%')
            OR (e.world = 'gr' AND e.page_url LIKE 'https://eduki.com/gr/search-results?query=%')
          )
          AND e.internal_path = 'sp'
          AND e.source = 'search'
          AND e.position BETWEEN 6 AND 12 THEN 1 END) AS clicks_at_6_12,
    COUNT(CASE WHEN e.type = 'appearedInSearch' THEN 1 END) AS total_searches
  FROM suggestion_only_sessions s
  LEFT JOIN `gtm-eduki-com.QE.events` e
    ON s.session_id = e.session_id
    AND s.world = e.world
    AND e.world IN ('de', 'es', 'it', 'gr')
    AND e.date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  GROUP BY s.session_id, s.world
),

purchase_map AS (
  -- Orders seen in any event of those sessions, within the window
  SELECT DISTINCT
    s.session_id,
    s.user_id,
    CAST(e.purchase_id AS STRING) AS order_number
  FROM `gtm-eduki-com.QE.events` e
  INNER JOIN suggestion_only_sessions s USING (session_id, user_id)
  WHERE e.date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
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
    COUNT(DISTINCT o.order_number) AS orders,
    SUM(o.gmv) AS gmv
  FROM suggestion_only_sessions s
  LEFT JOIN purchase_map pm USING (session_id, user_id)
  LEFT JOIN orders o
    ON o.order_number = pm.order_number
   AND o.user_id = pm.user_id
  GROUP BY s.session_id, s.user_id
),

period_performance AS (
  SELECT
    c.world,
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
  LEFT JOIN session_revenue r ON c.session_id = r.session_id
  GROUP BY c.world
)

SELECT
  world,
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
FROM period_performance
ORDER BY world;
