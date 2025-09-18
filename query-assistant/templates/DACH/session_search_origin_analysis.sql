-- Session Search Origin Analysis
-- Analyzes the percentage of sessions originated from suggestions vs typed queries
-- Target: BigQuery, Project: gtm-eduki-com, Dataset: QE

WITH search_events AS (
  -- Count all appearedInSearch events
  SELECT
    session_id,
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
  GROUP BY session_id, world
),

suggestion_events AS (
  -- Count all selectedSearchSuggestion events
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

period_stats AS (
  SELECT
    s.world,
    COUNT(DISTINCT s.session_id) AS total_search_sessions,
    SUM(s.total_search_events) AS total_search_events,
    SUM(COALESCE(sug.total_suggestion_events, 0)) AS total_suggestion_events,
    SUM(s.total_search_events) - SUM(COALESCE(sug.total_suggestion_events, 0)) AS total_typed_events
  FROM search_events s
  LEFT JOIN suggestion_events sug 
    ON s.session_id = sug.session_id 
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
FROM period_stats
ORDER BY world;
