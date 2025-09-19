-- RANK6 A/B Test Analysis - Search Behavior Metrics (Improved Structure)
-- Focus on search query patterns and pre-purchase search behavior
-- Based on performance_metrics.sql structure with RANK6_efficiency analysis

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
  WHERE e.date >= '2025-09-01'
    AND e.world = 'de'
    AND e.user_device IN ('desktop', 'tablet', 'mobile')
),

mp_sessions AS (
  SELECT DISTINCT session_id, user_id
  FROM mp_events mp
  WHERE mp.page_url LIKE 'https://eduki.com/de/suchergebnisse%' OR mp.page_url like '%Search%'
          AND mp.query != '' AND mp.query IS NOT NULL
              AND mp.type = 'appearedInSearch'
              AND world = 'de'
),

ab_assign AS (
  -- Get RANK6 A/B test assignments
  SELECT
    s.session_id,
    s.user_id,
    ANY_VALUE(ab_value) AS variant
  FROM `gtm-eduki-com.QE.events` e
  INNER JOIN mp_sessions s USING (session_id, user_id)
  CROSS JOIN UNNEST(e.ab_tests_key)  AS ab_key WITH OFFSET key_offset
  CROSS JOIN UNNEST(e.ab_tests_value) AS ab_value WITH OFFSET value_offset
  WHERE e.date >= '2025-09-01'
    AND key_offset = value_offset
    AND ab_key = 'RANK6'
    AND ab_value IN ('A: Original', 'B')
    AND world = 'de'
  GROUP BY s.session_id, s.user_id
),

search_sessions AS (
    -- Get sessions that had at least one search (appearedInSearch event)
    SELECT DISTINCT
        aa.session_id,
        aa.variant
    FROM 
        ab_assign aa
    INNER JOIN 
        mp_events e 
        ON aa.session_id = e.session_id
    WHERE 
        e.type = 'appearedInSearch'
        AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse%'
        AND e.query != ''
        AND e.query IS NOT NULL
        AND e.world = 'de'
),

search_events AS (
    -- Get all search events for search sessions with sequence order
    SELECT 
        ss.session_id,
        ss.variant,
        e.query,
        e.time as search_time,
        ROW_NUMBER() OVER (PARTITION BY ss.session_id ORDER BY e.time) as query_sequence
    FROM 
        search_sessions ss
    INNER JOIN 
        mp_events e 
        ON ss.session_id = e.session_id
    WHERE 
        e.type = 'appearedInSearch'
        AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse%'
        AND e.query != ''
        AND e.query IS NOT NULL
        AND e.world = 'de'
),

query_pairs AS (
    -- Create pairs of consecutive queries for comparison
    SELECT 
        se1.session_id,
        se1.variant,
        se1.query_sequence,
        LOWER(TRIM(se1.query)) as current_query_normalized,
        LOWER(TRIM(se2.query)) as previous_query_normalized,
        se1.query as current_query_original,
        se2.query as previous_query_original
    FROM 
        search_events se1
    INNER JOIN 
        search_events se2 
        ON se1.session_id = se2.session_id 
        AND se1.variant = se2.variant
        AND se2.query_sequence = se1.query_sequence - 1  -- Previous query
    WHERE 
        se1.query_sequence > 1  -- Skip first query (no previous to compare)
),

query_refinement_analysis AS (
    -- Analyze word overlap between consecutive queries
    SELECT 
        session_id,
        variant,
        query_sequence,
        current_query_original,
        previous_query_original,
        current_query_normalized,
        previous_query_normalized,
        
        -- Split queries into word arrays and calculate overlap
        ARRAY_LENGTH(
            ARRAY(
                SELECT word 
                FROM UNNEST(SPLIT(current_query_normalized, ' ')) AS word
                WHERE word IN UNNEST(SPLIT(previous_query_normalized, ' '))
            )
        ) as common_words,
        
        ARRAY_LENGTH(SPLIT(current_query_normalized, ' ')) as current_word_count,
        ARRAY_LENGTH(SPLIT(previous_query_normalized, ' ')) as previous_word_count,
        
        -- Calculate similarity percentage based on word overlap
        CASE 
            WHEN ARRAY_LENGTH(SPLIT(current_query_normalized, ' ')) > 0 
            THEN ARRAY_LENGTH(
                ARRAY(
                    SELECT word 
                    FROM UNNEST(SPLIT(current_query_normalized, ' ')) AS word
                    WHERE word IN UNNEST(SPLIT(previous_query_normalized, ' '))
                )
            ) * 100.0 / GREATEST(
                ARRAY_LENGTH(SPLIT(current_query_normalized, ' ')),
                ARRAY_LENGTH(SPLIT(previous_query_normalized, ' '))
            )
            ELSE 0 
        END as similarity_percentage,
        
        -- Classify as refinement if similarity >= 80%
        CASE 
            WHEN ARRAY_LENGTH(SPLIT(current_query_normalized, ' ')) > 0 
                AND ARRAY_LENGTH(
                    ARRAY(
                        SELECT word 
                        FROM UNNEST(SPLIT(current_query_normalized, ' ')) AS word
                        WHERE word IN UNNEST(SPLIT(previous_query_normalized, ' '))
                    )
                ) * 100.0 / GREATEST(
                    ARRAY_LENGTH(SPLIT(current_query_normalized, ' ')),
                    ARRAY_LENGTH(SPLIT(previous_query_normalized, ' '))
                ) >= 80
            THEN 1 
            ELSE 0 
        END as is_refinement
        
    FROM query_pairs
),

session_refinement_metrics AS (
    -- Calculate refinement rate per session
    SELECT 
        session_id,
        variant,
        COUNT(*) as total_query_comparisons,
        SUM(is_refinement) as total_refinements,
        CASE 
            WHEN COUNT(*) > 0 
            THEN SUM(is_refinement) * 100.0 / COUNT(*)
            ELSE 0 
        END as session_refinement_rate
    FROM query_refinement_analysis
    GROUP BY session_id, variant
),

frustration_score_analysis AS (
    -- Calculate frustration score for ALL users with 3+ refinements (no login restriction)
    SELECT 
        aa.session_id,
        aa.variant,
        aa.user_id,
        COALESCE(srm.total_refinements, 0) as user_refinements,
        CASE 
            WHEN COALESCE(srm.total_refinements, 0) >= 3 
            THEN 1 
            ELSE 0 
        END as is_frustrated_user
    FROM 
        ab_assign aa
    LEFT JOIN 
        session_refinement_metrics srm 
        ON aa.session_id = srm.session_id 
        AND aa.variant = srm.variant
),

variant_frustration_metrics AS (
    -- Aggregate frustration metrics per variant
    SELECT 
        variant,
        COUNT(DISTINCT user_id) as total_users,
        SUM(is_frustrated_user) as frustrated_users,
        CASE 
            WHEN COUNT(DISTINCT user_id) > 0 
            THEN SUM(is_frustrated_user) * 100.0 / COUNT(DISTINCT user_id)
            ELSE 0 
        END as frustration_score_percentage
    FROM frustration_score_analysis
    GROUP BY variant
),

queries_per_search_session AS (
    -- Count queries per search session
    SELECT 
        session_id,
        variant,
        COUNT(*) as total_queries_in_session
    FROM search_events
    GROUP BY session_id, variant
),

purchase_events AS (
    -- Get purchase events for search sessions
    SELECT 
        ss.session_id,
        ss.variant,
        e.time as purchase_time
    FROM 
        search_sessions ss
    INNER JOIN 
        mp_events e 
        ON ss.session_id = e.session_id
    WHERE 
        e.type = 'purchase'
),

searches_before_purchase AS (
    -- Count searches before each purchase
    SELECT 
        se.session_id,
        se.variant,
        pe.purchase_time,
        COUNT(*) as searches_before_this_purchase
    FROM 
        search_events se
    INNER JOIN 
        purchase_events pe 
        ON se.session_id = pe.session_id 
        AND se.variant = pe.variant
        AND se.search_time < pe.purchase_time  -- Search must be before purchase
    GROUP BY se.session_id, se.variant, pe.purchase_time
),

session_searches_before_purchase AS (
    -- Get average searches before purchase per session
    SELECT 
        session_id,
        variant,
        AVG(searches_before_this_purchase) as avg_searches_before_purchase
    FROM searches_before_purchase
    GROUP BY session_id, variant
)

-- Final analysis
SELECT 
    CASE 
        WHEN aa.variant = 'A: Original' THEN 'Elastic-Now'
        WHEN aa.variant = 'B' THEN 'Elastic-Intent'
        ELSE aa.variant
    END as variant_description,

    -- Basic session metrics
    COUNT(DISTINCT aa.session_id) as total_sessions,
    
    -- Percentage distribution
    ROUND(
        COUNT(DISTINCT aa.session_id) * 100.0 / 
        SUM(COUNT(DISTINCT aa.session_id)) OVER(), 2
    ) as percentage_share,
    
    -- Search session metrics
    COUNT(DISTINCT ss.session_id) as search_sessions,
    ROUND(
        COUNT(DISTINCT ss.session_id) * 100.0 / COUNT(DISTINCT aa.session_id), 2
    ) as sessions_with_queries_percentage,
    
    -- Queries per search session
    ROUND(AVG(qpss.total_queries_in_session), 2) as avg_queries_per_search_session,
    
    -- Searches before purchasing
    ROUND(AVG(ssbp.avg_searches_before_purchase), 2) as avg_searches_before_purchase,
    
    -- Query refinement metrics 
    ROUND(AVG(srm.session_refinement_rate), 2) as avg_refinement_rate_percentage,
    ROUND(
        COUNT(DISTINCT srm.session_id) * 100.0 / COUNT(DISTINCT ss.session_id), 2
    ) as sessions_with_refinements_percentage,

    -- Frustration Score metrics (now for ALL users, not just logged-in)
    ROUND(MAX(vfm.frustration_score_percentage),2) as search_frustration_score_percentage

FROM 
    ab_assign aa
LEFT JOIN 
    search_sessions ss ON aa.session_id = ss.session_id AND aa.variant = ss.variant
LEFT JOIN 
    queries_per_search_session qpss ON ss.session_id = qpss.session_id AND ss.variant = qpss.variant
LEFT JOIN 
    session_searches_before_purchase ssbp ON ss.session_id = ssbp.session_id AND ss.variant = ssbp.variant
LEFT JOIN 
    session_refinement_metrics srm ON ss.session_id = srm.session_id AND ss.variant = srm.variant
LEFT JOIN 
    variant_frustration_metrics vfm ON aa.variant = vfm.variant
GROUP BY 
    aa.variant
ORDER BY 
    aa.variant;
