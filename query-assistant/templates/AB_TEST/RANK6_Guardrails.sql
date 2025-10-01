-- RANK6 A/B Test Analysis - Comprehensive Metrics
-- Analysis including: New Query Rate, Time to Purchase, Filters Usage, Session Duration, and Bounce Rate
-- Optimized for performance with proper date filtering and reduced data scans

WITH rank6_sessions AS (
    -- Get all sessions in the RANK6 A/B test with their variants
    SELECT DISTINCT
        session_id,
        user_id,
        ab_value as variant
    FROM 
        `gtm-eduki-com.QE.events`,
        UNNEST(ab_tests_key) AS ab_key WITH OFFSET key_pos,
        UNNEST(ab_tests_value) AS ab_value WITH OFFSET value_pos
    WHERE 
        date >= '2025-09-01'
        AND date <= CURRENT_DATE()
        AND world = 'de'
        AND user_device IN ('desktop', 'tablet', 'mobile')
        AND ab_key = 'RANK6'
        AND key_pos = value_pos
        AND ab_value IN ('A: Original', 'B')
),

-- ==================== 1. NEW QUERY RATE METRICS ====================
all_queries_with_variants AS (
    -- Get all search queries with their timestamps and variants
    SELECT 
        rs.variant,
        e.query,
        e.time as query_time,
        LOWER(TRIM(e.query)) as normalized_query
    FROM 
        rank6_sessions rs
    INNER JOIN 
        `gtm-eduki-com.QE.events` e 
        ON rs.session_id = e.session_id
    WHERE 
        e.date >= '2025-09-01'
        AND e.date <= CURRENT_DATE()
        AND e.world = 'de'
        AND e.user_device IN ('desktop', 'tablet', 'mobile')
        AND e.type = 'appearedInSearch'
        AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse%'
        AND e.query != ''
        AND e.query IS NOT NULL
),

recent_queries_for_analysis AS (
    -- Filter queries from last 7 days for new query rate calculation
    SELECT 
        variant,
        query,
        query_time,
        normalized_query
    FROM all_queries_with_variants
    WHERE query_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
),

new_query_analysis AS (
    -- Efficiently determine if each recent query is new using EXISTS
    SELECT 
        rqfa.variant,
        rqfa.query,
        rqfa.query_time,
        rqfa.normalized_query,
        
        CASE 
            WHEN EXISTS(
                SELECT 1
                FROM all_queries_with_variants aqv
                WHERE aqv.variant = rqfa.variant
                    AND aqv.normalized_query = rqfa.normalized_query
                    AND aqv.query_time < rqfa.query_time
                    AND aqv.query_time >= TIMESTAMP_SUB(rqfa.query_time, INTERVAL 7 DAY)
            ) THEN 0  -- Not new (exact match found)
            ELSE 1  -- New query
        END as is_new_query
        
    FROM recent_queries_for_analysis rqfa
),

-- ==================== 2. TIME TO PURCHASE METRICS ====================
time_to_purchase_base AS (
    -- Get purchase and search events for time calculation
    SELECT
        rs.session_id,
        rs.user_id,
        rs.variant,
        MIN(CASE WHEN e.type = 'purchase' THEN e.time END) AS first_purchase_ts,
        MIN(CASE WHEN (
            e.page_url LIKE '%https://eduki.com/de/suchergebnisse%' OR
            e.page_url = 'Search'
        ) THEN e.time END) AS first_search_ts
    FROM rank6_sessions rs
    JOIN `gtm-eduki-com.QE.events` e
        ON e.session_id = rs.session_id
    WHERE e.date >= '2025-09-01'
        AND e.date <= CURRENT_DATE()
        AND e.world = 'de'
        AND e.user_device IN ('desktop', 'tablet', 'mobile')
        AND (
            e.page_url LIKE '%https://eduki.com/de/suchergebnisse%' OR
            e.page_url = 'Search' OR
            e.type = 'purchase'
        )
    GROUP BY rs.session_id, rs.user_id, rs.variant
        
),

time_to_purchase_calc AS (
    -- Calculate time differences for sessions with both search and purchase
    SELECT
        variant,
        session_id,
        user_id,
        first_search_ts,
        first_purchase_ts,
        TIMESTAMP_DIFF(first_purchase_ts, first_search_ts, SECOND) AS seconds_to_first_purchase
    FROM time_to_purchase_base
    WHERE first_purchase_ts IS NOT NULL
        AND first_search_ts IS NOT NULL
        AND first_purchase_ts > first_search_ts
),

-- ==================== 3. FILTERS METRICS ====================
filter_sessions AS (
    -- Sessions that applied filters
    SELECT DISTINCT 
        rs.user_id, 
        rs.session_id,
        rs.variant
    FROM rank6_sessions rs
    JOIN `gtm-eduki-com.QE.events` e
        ON e.session_id = rs.session_id
    WHERE 
        e.type = 'appearedInSearch'
        AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse%'
        AND e.version = 0.0
        AND e.world = 'de'
        AND e.date >= '2025-09-01'
        AND e.date <= CURRENT_DATE()
        AND EXISTS(
            SELECT 1
            FROM UNNEST(e.query_params_key) key
            WHERE key IN ('t', 'c', 'prc', 's', 'sale', 'mt', 'b', 'f', 'ft', 'ly', 'tj', 'tp')
        )
),

-- ==================== 4. SESSION DURATION METRICS ====================
session_duration_base AS (
    -- Material page events for duration calculation
    SELECT
        rs.session_id,
        rs.user_id,
        rs.variant,
        e.type,
        e.page_url,
        e.date,
        e.time,
        e.os,
        CASE 
            WHEN REGEXP_CONTAINS(COALESCE(e.os,''), r'(?i)android|ios|ipad')
            THEN 'App' 
            ELSE 'Web' 
        END AS platform
    FROM rank6_sessions rs
    JOIN `gtm-eduki-com.QE.events` e
        ON rs.session_id = e.session_id
    WHERE e.date >= '2025-09-01'
        AND e.date <= CURRENT_DATE()
        AND e.world = 'de'
        AND e.user_device IN ('desktop', 'tablet', 'mobile')
        AND (
            e.page_url LIKE '%https://eduki.com/de/suchergebnisse%' OR
            e.page_url = 'Search'
        )
),

session_duration_calc AS (
    -- Calculate per-session duration
    SELECT
        session_id,
        user_id,
        variant,
        platform,
        MIN(date) AS session_date,
        SAFE.TIMESTAMP_DIFF(
            TIMESTAMP(MAX(time)),
            TIMESTAMP(MIN(time)),
            SECOND
        ) AS session_duration_sec
    FROM session_duration_base
    GROUP BY session_id, user_id, variant, platform
),

-- ==================== 5. BOUNCE RATE METRICS ====================
bounce_rate_base AS (
    -- Get events that indicate user engagement
    SELECT 
        rs.session_id,
        rs.user_id,
        rs.variant,
        e.type,
        e.source,
        e.query,
        e.page_url,
        e.item_id,
        e.extra,
        CASE 
            WHEN e.type = 'click' 
                AND e.source = 'search' 
                AND e.query != '' 
                AND e.query IS NOT NULL 
                AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse%'
            THEN 1 ELSE 0 
        END as clicked_material,
        
        CASE WHEN e.type = 'addToFavorites' 
            AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse%'
            AND e.item_id IS NOT NULL
        THEN 1 ELSE 0 
        END as added_to_favorites,
        
        CASE WHEN e.type = 'addToCart'
            AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse%'
            AND e.item_id IS NOT NULL
        THEN 1 ELSE 0 
        END as added_to_cart,
        
        CASE WHEN e.type = 'download-purchased-material-click'
            AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse%'
            AND e.extra LIKE '%"materialId"%'
        THEN 1 ELSE 0 
        END as downloaded_material,
        
        CASE WHEN EXISTS(
            SELECT 1
            FROM UNNEST(e.query_params_key) key,
                 UNNEST(e.query_params_value) value
            WHERE key = 's' AND value IS NOT NULL
        )
        THEN 1 ELSE 0 
        END as applied_sorting
        
    FROM rank6_sessions rs
    JOIN `gtm-eduki-com.QE.events` e
        ON rs.session_id = e.session_id
    WHERE e.date >= '2025-09-01'
        AND e.world = 'de'
        AND e.user_device IN ('desktop', 'tablet', 'mobile')
        ),

bounce_rate_calc AS (
    -- Aggregate engagement per session
    SELECT
        session_id,
        user_id,
        variant,
        MAX(clicked_material) as has_clicked_material,
        MAX(added_to_favorites) as has_added_to_favorites,
        MAX(added_to_cart) as has_added_to_cart,
        MAX(downloaded_material) as has_downloaded_material,
        MAX(applied_sorting) as has_applied_sorting
    FROM bounce_rate_base
    GROUP BY session_id, user_id, variant
),

bounce_rate_with_filters AS (
    -- Combine with filter usage to determine bounce
    SELECT
        brc.session_id,
        brc.user_id,
        brc.variant,
        brc.has_clicked_material,
        brc.has_added_to_favorites,
        brc.has_added_to_cart,
        brc.has_downloaded_material,
        brc.has_applied_sorting,
        CASE WHEN fs.session_id IS NOT NULL THEN 1 ELSE 0 END as has_applied_filters,
        
        -- Bounce if no engagement occurred
        CASE WHEN 
            brc.has_clicked_material = 0 
            AND brc.has_added_to_favorites = 0
            AND brc.has_added_to_cart = 0
            AND brc.has_downloaded_material = 0
            AND brc.has_applied_sorting = 0
            AND fs.session_id IS NULL
        THEN 1 ELSE 0 
        END as is_bounced
        
    FROM bounce_rate_calc brc
    LEFT JOIN filter_sessions fs
        ON brc.session_id = fs.session_id
),

-- ==================== FINAL METRICS AGGREGATION ====================
new_query_metrics AS (
    SELECT 
        variant,
        COUNT(*) as total_queries_analyzed,
        SUM(is_new_query) as new_queries_count,
        ROUND(
            CASE 
                WHEN COUNT(*) > 0 
                THEN SUM(is_new_query) * 100.0 / COUNT(*)
                ELSE 0 
            END, 2
        ) as new_query_rate_percentage
    FROM new_query_analysis
    GROUP BY variant
),

time_to_purchase_metrics AS (
    SELECT
        variant,
        COUNT(*) as sessions_with_purchase,
        COUNT(DISTINCT user_id) as users_with_purchase,
        ROUND(AVG(seconds_to_first_purchase), 2) as avg_seconds_to_first_purchase,
        COUNTIF(seconds_to_first_purchase <= 120) as sessions_le_2m,
        COUNTIF(seconds_to_first_purchase <= 600) as sessions_le_10m,
        COUNTIF(seconds_to_first_purchase <= 1200) as sessions_le_20m,
        COUNTIF(seconds_to_first_purchase > 1200) as sessions_gt_20m
    FROM time_to_purchase_calc
    GROUP BY variant
),

filters_metrics AS (
    SELECT
        fs.variant,
        COUNT(DISTINCT fs.user_id) as users_with_filters,
        COUNT(DISTINCT fs.session_id) as sessions_with_filters
    FROM filter_sessions fs
    GROUP BY fs.variant
),

session_duration_metrics AS (
    SELECT
        variant,
        COUNT(DISTINCT session_id) as sessions_measured,
        COUNT(DISTINCT user_id) as users_measured,
        ROUND(AVG(session_duration_sec), 2) as avg_session_duration_sec
    FROM session_duration_calc
    GROUP BY variant
),

bounce_rate_metrics AS (
    SELECT
        variant,
        COUNT(DISTINCT session_id) as total_search_sessions,
        SUM(is_bounced) as bounced_sessions,
        ROUND(
            CASE 
                WHEN COUNT(DISTINCT session_id) > 0 
                THEN SUM(is_bounced) * 100.0 / COUNT(DISTINCT session_id)
 ELSE 0 
            END, 2
        ) as bounce_rate_percentage
    FROM bounce_rate_with_filters
    GROUP BY variant
)

-- Final comprehensive analysis
SELECT 
    CASE 
        WHEN rs.variant = 'A: Original' THEN 'Elastic-Now'
        WHEN rs.variant = 'B' THEN 'Elastic-Intent'
        ELSE rs.variant
    END as variant_description,
    
    -- New Query Rate Metrics
    COALESCE(nqm.total_queries_analyzed, 0) as total_queries_analyzed,
    COALESCE(nqm.new_queries_count, 0) as new_queries_count,
    COALESCE(nqm.new_query_rate_percentage, 0) as new_query_rate_percentage,
    
    -- Time to Purchase Metrics
    COALESCE(ttpm.sessions_with_purchase, 0) as sessions_with_purchase,
    COALESCE(ttpm.users_with_purchase, 0) as users_with_purchase,
    COALESCE(ttpm.avg_seconds_to_first_purchase, 0) as avg_seconds_to_first_purchase,
    COALESCE(ttpm.sessions_le_2m, 0) as sessions_le_2min,
    COALESCE(ttpm.sessions_le_10m, 0) as sessions_le_10min,
    COALESCE(ttpm.sessions_le_20m, 0) as sessions_le_20min,
    COALESCE(ttpm.sessions_gt_20m, 0) as sessions_gt_20min,
    
    -- Filters Metrics
    COALESCE(fm.users_with_filters, 0) as users_with_filters,
    COALESCE(fm.sessions_with_filters, 0) as sessions_with_filters,
    
    -- Session Duration Metrics
    COALESCE(sdm.sessions_measured, 0) as sessions_measured,
    COALESCE(sdm.users_measured, 0) as users_measured,
    COALESCE(sdm.avg_session_duration_sec, 0) as avg_session_duration_sec,
    
    -- Bounce Rate Metrics
    COALESCE(brm.total_search_sessions, 0) as total_search_sessions,
    COALESCE(brm.bounced_sessions, 0) as bounced_sessions,
    COALESCE(brm.bounce_rate_percentage, 0) as bounce_rate_percentage

FROM (
    SELECT DISTINCT variant FROM rank6_sessions
) rs
LEFT JOIN new_query_metrics nqm ON rs.variant = nqm.variant
LEFT JOIN time_to_purchase_metrics ttpm ON rs.variant = ttpm.variant
LEFT JOIN filters_metrics fm ON rs.variant = fm.variant
LEFT JOIN session_duration_metrics sdm ON rs.variant = sdm.variant
LEFT JOIN bounce_rate_metrics brm ON rs.variant = brm.variant

ORDER BY rs.variant;