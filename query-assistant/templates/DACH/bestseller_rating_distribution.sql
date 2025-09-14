-- Bestseller Rating Distribution Query
-- Show distribution of materials across bestseller_rating ranges
-- Target: MySQL - Simple approach to analyze rating distribution
-- Note: bestseller_rating scale goes up to ~24,000

SELECT 
  ap.segment,
  CASE 
    WHEN m.bestseller_rating >= 20000 THEN '20,000+ (Top Tier)'
    WHEN m.bestseller_rating >= 15000 THEN '15,000-19,999 (Excellent)'
    WHEN m.bestseller_rating >= 10000 THEN '10,000-14,999 (Very Good)'
    WHEN m.bestseller_rating >= 5000 THEN '5,000-9,999 (Good)'
    WHEN m.bestseller_rating >= 1000 THEN '1,000-4,999 (Average)'
    WHEN m.bestseller_rating >= 500 THEN '500-999 (Below Average)'
    WHEN m.bestseller_rating >= 100 THEN '100-499 (Low)'
    ELSE 'Below 100 (Very Low)'
  END AS rating_range,
  COUNT(*) AS material_count,
  COUNT(DISTINCT m.author_id) AS author_count,
  ROUND(AVG(m.bestseller_rating), 0) AS avg_rating,
  ROUND(MIN(m.bestseller_rating), 0) AS min_rating,
  ROUND(MAX(m.bestseller_rating), 0) AS max_rating
FROM materials m
INNER JOIN author_profiles ap ON m.author_id = ap.user_id
WHERE ap.segment IN ('dragon', 'bear', 'cub')
  AND m.world = 'de'
  AND m.is_bundle = 0 
  AND m.interactive_id IS NULL 
  AND (m.is_standalone_interactive = 0 OR m.is_standalone_interactive IS NULL)
  AND m.deleted_at IS NULL 
  AND m.status NOT IN ('deleted', 'inactive')
  AND COALESCE(m.custom_pages_total, m.total_pages) IS NOT NULL
  AND COALESCE(m.custom_pages_total, m.total_pages) <= 100
GROUP BY 
  ap.segment,
  CASE 
    WHEN m.bestseller_rating >= 20000 THEN '20,000+ (Top Tier)'
    WHEN m.bestseller_rating >= 15000 THEN '15,000-19,999 (Excellent)'
    WHEN m.bestseller_rating >= 10000 THEN '10,000-14,999 (Very Good)'
    WHEN m.bestseller_rating >= 5000 THEN '5,000-9,999 (Good)'
    WHEN m.bestseller_rating >= 1000 THEN '1,000-4,999 (Average)'
    WHEN m.bestseller_rating >= 500 THEN '500-999 (Below Average)'
    WHEN m.bestseller_rating >= 100 THEN '100-499 (Low)'
    ELSE 'Below 100 (Very Low)'
  END
ORDER BY 
  ap.segment,
  CASE 
    WHEN m.bestseller_rating >= 20000 THEN 1
    WHEN m.bestseller_rating >= 15000 THEN 2
    WHEN m.bestseller_rating >= 10000 THEN 3
    WHEN m.bestseller_rating >= 5000 THEN 4
    WHEN m.bestseller_rating >= 1000 THEN 5
    WHEN m.bestseller_rating >= 500 THEN 6
    WHEN m.bestseller_rating >= 100 THEN 7
    ELSE 8
  END;
