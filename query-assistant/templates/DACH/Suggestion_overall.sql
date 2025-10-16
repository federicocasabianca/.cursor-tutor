-- =========================
-- PARÁMETROS
-- =========================
-- Search Origin Analysis - Session metrics for suggestions vs typed queries
-- =========================
DECLARE tz STRING DEFAULT 'Europe/Madrid';
DECLARE START_DATE DATE DEFAULT '2025-10-03';
DECLARE END_DATE DATE DEFAULT CURRENT_DATE(tz);
DECLARE EVT_SUGGESTION_SELECTED STRING DEFAULT 'selectedSearchSuggestion';

-- =========================
-- QUERY
-- =========================
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
    e.time
  FROM `gtm-eduki-com.QE.events` e
  WHERE e.date BETWEEN START_DATE AND END_DATE
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

search_events AS (
  -- Count all appearedInSearch events
  SELECT
    s.session_id,
    s.user_id,
    mp.world,
    COUNT(*) AS total_search_events
  FROM mp_events mp
  INNER JOIN mp_sessions s USING (session_id, user_id)
  WHERE mp.type = 'appearedInSearch'
    AND (
      (mp.world = 'de' AND (mp.page_url LIKE 'https://eduki.com/de/suchergebnisse%' OR mp.page_url LIKE '%Search%'))
      OR (mp.world = 'es' AND mp.page_url LIKE 'https://eduki.com/es/resultados-busqueda%')
      OR (mp.world = 'it' AND mp.page_url LIKE 'https://eduki.com/it/risultati-della-ricerca%')
      OR (mp.world = 'gr' AND mp.page_url LIKE 'https://eduki.com/gr/search-results%')
    )
    AND mp.query != ''
    AND mp.query IS NOT NULL
  GROUP BY session_id, user_id, world
),

suggestion_events AS (
  -- Count all selectedSearchSuggestion events
  SELECT
    s.session_id,
    s.user_id,
    mp.world,
    COUNT(*) AS total_suggestion_events
  FROM mp_events mp
  INNER JOIN mp_sessions s USING (session_id, user_id)
  WHERE mp.type = EVT_SUGGESTION_SELECTED
  GROUP BY session_id, user_id, world
),

world_stats AS (
  SELECT
    s.world,
    COUNT(DISTINCT s.session_id) AS total_search_sessions,
    SUM(s.total_search_events) AS total_search_events,
    SUM(COALESCE(sug.total_suggestion_events, 0)) AS total_suggestion_events,
    SUM(s.total_search_events) - SUM(COALESCE(sug.total_suggestion_events, 0)) AS total_typed_events
  FROM search_events s
  LEFT JOIN suggestion_events sug 
    ON s.session_id = sug.session_id 
    AND s.user_id = sug.user_id
    AND s.world = sug.world
  GROUP BY s.world
)

SELECT
  world,
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
FROM world_stats
ORDER BY world;