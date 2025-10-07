-- DSR A/B Test - Session Search Origin Analysis
-- Analyzes the percentage of sessions originated from suggestions vs typed queries by DSR variant
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

variant_stats AS (
  SELECT
    s.world,
    s.variant,
    COUNT(DISTINCT s.session_id) AS total_search_sessions,
    SUM(s.total_search_events) AS total_search_events,
    SUM(COALESCE(sug.total_suggestion_events, 0)) AS total_suggestion_events,
    SUM(s.total_search_events) - SUM(COALESCE(sug.total_suggestion_events, 0)) AS total_typed_events
  FROM search_events s
  LEFT JOIN suggestion_events sug 
    ON s.session_id = sug.session_id 
    AND s.user_id = sug.user_id
    AND s.world = sug.world
    AND s.variant = sug.variant
  GROUP BY s.world, s.variant
)

SELECT
  world,
  variant,
  total_search_sessions,
  total_search_events,
  total_suggestion_events,
  total_typed_events,
  ROUND(
    (total_suggestion_events * 100.0 / total_search_events), 2
  ) AS pct_searches_with_suggestions,
  ROUND(
    (total_typed_events * 100.0 / total_search_events), 2
  ) AS pct_searches_with_typed_queries
FROM variant_stats
ORDER BY world, variant;
