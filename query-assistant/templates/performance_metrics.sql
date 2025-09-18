-- =========================
-- PARÁMETROS
-- =========================
DECLARE tz STRING DEFAULT 'Europe/Madrid';
DECLARE TEST_KEY STRING DEFAULT 'RANK6';               -- <-- cámbialo: 'MPL' | 'MPRD' | 'ab_app_material_ci' | otro
DECLARE START_DATE DATE DEFAULT '2025-09-01';        -- <-- ajusta ventana (p.ej. T1/T2)
DECLARE END_DATE   DATE DEFAULT CURRENT_DATE(tz);

DECLARE EVT_PAGEVIEW         STRING DEFAULT 'pageView';
DECLARE EVT_VIEW_MATERIAL    STRING DEFAULT 'viewMaterial';
DECLARE EVT_PREVIEW_MATERIAL STRING DEFAULT 'showMaterialPreview';
DECLARE EVT_ADD_TO_CART      STRING DEFAULT 'addToCart';
DECLARE EVT_ADD_TO_FAV       STRING DEFAULT 'addToFavorites';

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
    e.query
  FROM `QE.events` e
  WHERE e.date BETWEEN START_DATE AND END_DATE

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
  -- Busca la variante del TEST_KEY en cualquier evento de la sesión (no solo MP)
  SELECT
    s.session_id,
    s.user_id,
    ANY_VALUE(ab_value) AS variant
  FROM `QE.events` e
  INNER JOIN mp_sessions s USING (session_id, user_id)
  CROSS JOIN UNNEST(e.ab_tests_key)  AS ab_key WITH OFFSET key_offset
  CROSS JOIN UNNEST(e.ab_tests_value) AS ab_value WITH OFFSET value_offset
  WHERE e.date BETWEEN START_DATE AND END_DATE
    AND key_offset = value_offset
    AND ab_key = TEST_KEY
    AND world = 'de'
  GROUP BY s.session_id, s.user_id
),
session_features AS (
  SELECT
    m.session_id,
    m.user_id,
    MIN(m.d_local) AS session_date,  
    ANY_VALUE(m.world) AS world,
    os as platform,
    COUNTIF(m.type = EVT_PAGEVIEW)         AS pageviews,
    COUNTIF(m.type = EVT_VIEW_MATERIAL)    AS view_material,
    COUNTIF(m.type = EVT_PREVIEW_MATERIAL) AS preview_clicks,
    COUNTIF(m.type = EVT_ADD_TO_CART)      AS add_to_cart,
    COUNTIF(m.type = EVT_ADD_TO_FAV)       AS add_to_fav
  FROM mp_events m
    inner join mp_sessions s USING (session_id, user_id)
  GROUP BY m.session_id, m.user_id, os
),
purchase_map AS (
  -- Pedidos vistos en cualquier evento de esas sesiones, dentro de la ventana
  SELECT DISTINCT
    s.session_id,
    s.user_id,
    CAST(e.purchase_id AS STRING) AS order_number
  FROM `QE.events` e
  inner JOIN mp_sessions s USING (session_id, user_id)
  WHERE e.date BETWEEN START_DATE AND END_DATE
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
    sf.session_id,
    sf.user_id,
    COUNT(DISTINCT o.order_number) AS orders,
    SUM(o.gmv) AS gmv
  FROM session_features sf
  LEFT JOIN purchase_map pm USING (session_id, user_id)
  LEFT JOIN orders o
    ON o.order_number = pm.order_number
   AND o.user_id     = pm.user_id
  GROUP BY sf.session_id, sf.user_id
),
sessions AS (
  SELECT
    sf.session_id, sf.user_id, sf.session_date, sf.platform, sf.world,
    sf.pageviews, sf.view_material, sf.preview_clicks, sf.add_to_cart, sf.add_to_fav,
    COALESCE(sa.variant, 'unknown') AS variant,
    COALESCE(sr.orders, 0) AS orders,
    COALESCE(sr.gmv,    0) AS gmv
  FROM session_features sf
  LEFT JOIN ab_assign sa USING (session_id, user_id)
  LEFT JOIN session_revenue sr USING (session_id, user_id)
)
SELECT
  --session_date AS date,
  --platform,
  --world,
  variant,
  COUNT(DISTINCT session_id) AS sessions,
  SUM(pageviews) AS pageviews,
  SUM(view_material) AS view_material,
  SUM(preview_clicks) AS previews,
  SUM(add_to_cart) AS add_to_cart,
  SUM(add_to_fav) AS add_to_fav,
  SUM(orders) AS orders,
  SUM(gmv) AS gmv,
  SAFE_DIVIDE(SUM(orders), COUNT(DISTINCT session_id)) AS cvr,
  SAFE_DIVIDE(SUM(gmv), NULLIF(SUM(orders),0))        AS aov,
  SAFE_DIVIDE(SUM(gmv), COUNT(DISTINCT session_id))   AS gmv_per_session
FROM sessions
WHERE variant IS NOT NULL AND variant != 'unknown'
AND world = 'de'
GROUP BY 1--,2,3,4
ORDER BY 1--,2,3,4