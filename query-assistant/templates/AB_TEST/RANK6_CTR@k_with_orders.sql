-- RANK6 A/B Test Analysis with MRR and CTR@k Distribution (Using Orders)
-- Search intent logic A/B test with MRR and position-based metrics using order-based purchases

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
    e.item_id,
    e.source,
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

search_click_events AS (
    -- Get click events after search for MRR and CTR@k calculation
    SELECT 
        aa.session_id,
        aa.variant,
        e.query,
        e.position,
        e.time as event_time,
        e.item_id,
        ROW_NUMBER() OVER (
            PARTITION BY aa.session_id, aa.variant, e.query 
            ORDER BY e.time
        ) as click_rank_per_query
    FROM 
        ab_assign aa
    INNER JOIN 
        mp_events e 
        ON aa.session_id = e.session_id
    WHERE 
        e.type = 'click'
        AND e.source = 'search'
        AND e.query != ''
        AND e.query IS NOT NULL
        AND e.page_url LIKE 'https://eduki.com/de/suchergebnisse%'
        AND e.position IS NOT NULL
        AND e.position <= 36
),

purchase_map AS (
  -- Orders seen in any event of those sessions, within the window
  SELECT DISTINCT
    s.session_id,
    s.user_id,
    CAST(e.purchase_id AS STRING) AS order_number
  FROM `gtm-eduki-com.QE.events` e
  inner JOIN mp_sessions s USING (session_id, user_id)
  WHERE e.date >= '2025-09-01'
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
    aa.session_id,
    aa.user_id,
    aa.variant,
    COUNT(DISTINCT o.order_number) AS orders,
    SUM(o.gmv) AS gmv
  FROM ab_assign aa
  LEFT JOIN purchase_map pm USING (session_id, user_id)
  LEFT JOIN orders o
    ON o.order_number = pm.order_number
   AND o.user_id = pm.user_id
  GROUP BY aa.session_id, aa.user_id, aa.variant
),

clicks_with_purchases AS (
    -- Match clicks with subsequent purchases using order-based logic
    SELECT 
        sce.session_id,
        sce.variant,
        sce.query,
        sce.position,
        sce.event_time as click_time,
        sce.item_id,
        sce.click_rank_per_query,
        -- Check if this session had any purchases after this click
        CASE 
            WHEN sr.orders > 0 AND sr.session_id IS NOT NULL 
            THEN 1 
            ELSE 0 
        END as led_to_purchase
    FROM search_click_events sce
    LEFT JOIN session_revenue sr 
        ON sce.session_id = sr.session_id 
        AND sce.variant = sr.variant
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
    ) as ctr_pos_25_36_percentage

FROM 
    ab_assign aa
LEFT JOIN 
    session_mrr sm ON aa.session_id = sm.session_id AND aa.variant = sm.variant
LEFT JOIN 
    session_ctr_distribution scd ON aa.session_id = scd.session_id AND aa.variant = scd.variant
GROUP BY 
    aa.variant
ORDER BY 
    aa.variant;
