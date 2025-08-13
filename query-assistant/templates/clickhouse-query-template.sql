-- Query Name: {{query_name}}
-- Generated: {{date}}
-- Environment: Clickhouse with Metabase

SELECT 
    session_id,
    indexOf(ab_tests.key, 'RANK2') AS rank2_index,
    CASE 
        WHEN arrayElement(ab_tests.value, indexOf(ab_tests.key, 'RANK2')) = 'A' THEN 'Elastic'
        WHEN arrayElement(ab_tests.value, indexOf(ab_tests.key, 'RANK2')) = 'B' THEN 'Detectum'
        ELSE arrayElement(ab_tests.value, indexOf(ab_tests.key, 'RANK2'))
    END AS rank2_value,
    position,
    type,
    item_price
FROM events
WHERE 
    world = 'de'
    AND date >= '2024-12-17'
    AND indexOf(ab_tests.key, 'RANK2') > 0
