/*
• High priority (add now):
•	Query Success Rate (define once; use for many tests)
•	MRR & CTR@k distribution (not just an overall CTR)
•	Time to Relevant Result
•	Refinement Rate + Frustration Score
•	Result Re-evaluation Rate
•	Purchase from Top-5 (or Top-N)
•	Zero Results Rate (daily)
•	Conversion Lag
*/ 
-- RANK5 A/B Test Analysis with MRR and CTR@k Distribution
-- Search intent logic A/B test with MRR and position-based metrics

WITH rank5_sessions AS (
    -- Get all sessions in the RANK5 A/B test with their variants
    SELECT DISTINCT
        session_id,
        ab_value as variant
    FROM 
        `gtm-eduki-com.QE.events`,
        UNNEST(ab_tests_key) AS ab_key WITH OFFSET key_pos,
        UNNEST(ab_tests_value) AS ab_value WITH OFFSET value_pos
    WHERE 
        date >= '2025-09-01'
        AND world = 'de'
        AND user_device IN ('desktop', 'tablet', 'mobile')
        AND ab_key = 'RANK6'
        AND key_pos = value_pos
        AND ab_value IN ('A: Original', 'B')
),

search_click_events AS (
    -- Get click events after search for MRR and CTR@k calculation
    SELECT 
        rs.session_id,
        rs.variant,
        e.query,
        e.position,
        e.time as event_time,
        e.item_id,
        ROW_NUMBER() OVER (
            PARTITION BY rs.session_id, rs.variant, e.query 
            ORDER BY e.time
        ) as click_rank_per_query
    FROM 
        rank5_sessions rs
    INNER JOIN 
        `gtm-eduki-com.QE.events` e 
        ON rs.session_id = e.session_id
    WHERE 
        e.date >= '2025-09-01'
        AND e.world = 'de'
        AND e.user_device IN ('desktop', 'tablet', 'mobile')
        AND e.type = 'click'
        AND e.source = 'search'
        AND e.query != ''
        AND e.query IS NOT NULL
        AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse%'
        AND e.position IS NOT NULL
        AND e.position <= 36
),

purchase_events AS (
    -- Get purchase events to match with clicks
    SELECT 
        rs.session_id,
        rs.variant,
        e.time as purchase_time,
        e.item_id
    FROM 
        rank5_sessions rs
    INNER JOIN 
        `gtm-eduki-com.QE.events` e 
        ON rs.session_id = e.session_id
    WHERE 
        e.date >= '2025-09-01'
        AND e.world = 'de'
        AND e.user_device IN ('desktop', 'tablet', 'mobile')
        AND e.type = 'purchase'
        AND e.item_id IS NOT NULL
),

clicks_with_purchases AS (
    -- Match clicks with subsequent purchases of the same item
    SELECT 
        sce.session_id,
        sce.variant,
        sce.query,
        sce.position,
        sce.event_time as click_time,
        sce.item_id,
        sce.click_rank_per_query,
        -- Check if this clicked item was later purchased
        CASE 
            WHEN pe.item_id IS NOT NULL AND pe.purchase_time > sce.event_time 
            THEN 1 
            ELSE 0 
        END as led_to_purchase
    FROM search_click_events sce
    LEFT JOIN purchase_events pe 
        ON sce.session_id = pe.session_id 
        AND sce.variant = pe.variant
        AND sce.item_id = pe.item_id
        AND pe.purchase_time > sce.event_time  -- Purchase must be after click
),

first_clicks_per_query AS (
    -- Get first clicks per query for MRR calculation
    SELECT 
        session_id,
        variant,
        query,
        position,
        led_to_purchase,
        -- Calculate reciprocal rank (1/position) for MRR
        CASE 
            WHEN position > 0 THEN 1.0 / position 
            ELSE 0 
        END as reciprocal_rank
    FROM clicks_with_purchases
    WHERE click_rank_per_query = 1  -- First click per query
),

session_mrr AS (
    -- Calculate MRR per session
    SELECT 
        session_id,
        variant,
        -- MRR for clicks: average of (1/position) for first clicks
        AVG(reciprocal_rank) as session_mrr_click,
        -- MRR for purchases: average of (1/position) for first clicks that led to purchases
        AVG(CASE WHEN led_to_purchase = 1 THEN reciprocal_rank ELSE NULL END) as session_mrr_purchase
    FROM first_clicks_per_query
    GROUP BY session_id, variant
),

all_clicks_for_ctr AS (
    -- Get all clicks (not just first) for CTR@k distribution
    SELECT 
        session_id,
        variant,
        position
    FROM clicks_with_purchases  -- Use the enhanced click data
),

session_ctr_distribution AS (
    -- Calculate CTR@k distribution per session
    SELECT 
        session_id,
        variant,
        -- Count clicks by position ranges
        SUM(CASE WHEN position = 1 THEN 1 ELSE 0 END) as clicks_pos_1,
        SUM(CASE WHEN position = 2 THEN 1 ELSE 0 END) as clicks_pos_2,
        SUM(CASE WHEN position = 3 THEN 1 ELSE 0 END) as clicks_pos_3,
        SUM(CASE WHEN position = 4 THEN 1 ELSE 0 END) as clicks_pos_4,
        SUM(CASE WHEN position = 5 THEN 1 ELSE 0 END) as clicks_pos_5,
        SUM(CASE WHEN position BETWEEN 6 AND 12 THEN 1 ELSE 0 END) as clicks_pos_6_12,
        SUM(CASE WHEN position BETWEEN 13 AND 24 THEN 1 ELSE 0 END) as clicks_pos_13_24,
        SUM(CASE WHEN position BETWEEN 25 AND 36 THEN 1 ELSE 0 END) as clicks_pos_25_36,
        COUNT(*) as total_clicks
    FROM all_clicks_for_ctr
    GROUP BY session_id, variant
)

-- Final analysis with MRR and CTR@k distribution
SELECT 
    CASE 
        WHEN rs.variant = 'A: Original' THEN 'Elastic-Now'
        WHEN rs.variant = 'B' THEN 'Elastic-Intent'
        ELSE rs.variant
    END as variant_description,

    -- Basic session metrics
    COUNT(DISTINCT rs.session_id) as total_sessions,
    
    -- Percentage distribution
    ROUND(
        COUNT(DISTINCT rs.session_id) * 100.0 / 
        SUM(COUNT(DISTINCT rs.session_id)) OVER(), 2
    ) as percentage_share,
    
    -- MRR Metrics
    ROUND(AVG(sm.session_mrr_click), 4) as mrr_click,
    ROUND(AVG(sm.session_mrr_purchase), 4) as mrr_purchase,
    
    -- CTR@k Distribution (percentage of clicks at each position range)
    ROUND(
        SUM(scd.clicks_pos_1) * 100.0 / NULLIF(SUM(scd.total_clicks), 0), 2
    ) as ctr_pos_1_percentage,
    
    ROUND(
        SUM(scd.clicks_pos_2) * 100.0 / NULLIF(SUM(scd.total_clicks), 0), 2
    ) as ctr_pos_2_percentage,
    
    ROUND(
        SUM(scd.clicks_pos_3) * 100.0 / NULLIF(SUM(scd.total_clicks), 0), 2
    ) as ctr_pos_3_percentage,
    
    ROUND(
        SUM(scd.clicks_pos_4) * 100.0 / NULLIF(SUM(scd.total_clicks), 0), 2
    ) as ctr_pos_4_percentage,
    
    ROUND(
        SUM(scd.clicks_pos_5) * 100.0 / NULLIF(SUM(scd.total_clicks), 0), 2
    ) as ctr_pos_5_percentage,
    
    ROUND(
        SUM(scd.clicks_pos_6_12) * 100.0 / NULLIF(SUM(scd.total_clicks), 0), 2
    ) as ctr_pos_6_12_percentage,
    
    ROUND(
        SUM(scd.clicks_pos_13_24) * 100.0 / NULLIF(SUM(scd.total_clicks), 0), 2
    ) as ctr_pos_13_24_percentage,
    
    ROUND(
        SUM(scd.clicks_pos_25_36) * 100.0 / NULLIF(SUM(scd.total_clicks), 0), 2
    ) as ctr_pos_25_36_percentage,
    
    -- Additional context metrics
    -- SUM(scd.total_clicks) as total_clicks_analyzed,
    -- COUNT(DISTINCT sm.session_id) as sessions_with_mrr_data

FROM 
    rank5_sessions rs
LEFT JOIN 
    session_mrr sm ON rs.session_id = sm.session_id AND rs.variant = sm.variant
LEFT JOIN 
    session_ctr_distribution scd ON rs.session_id = scd.session_id AND rs.variant = scd.variant
GROUP BY 
    rs.variant
ORDER BY 
    rs.variant;