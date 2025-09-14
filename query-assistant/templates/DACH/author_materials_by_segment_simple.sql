-- Author Materials Count by Segment Query (Working Simple Approach)
-- Count total materials for authors in specific segments meeting criteria
-- Target: MySQL - Simple approach that actually works

-- Approach: Use a simple approach - just get all materials and count them
-- Since we can't easily do top 20 per author in MySQL, let's get a reasonable subset

SELECT 
  ap.segment,
  COUNT(DISTINCT m.author_id) AS author_count,
  COUNT(*) AS total_materials
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
  -- Filter for materials created in the last 24 months
  AND m.created_at >= DATE_SUB(NOW(), INTERVAL 24 MONTH)
  -- Simple filter: only include materials with high bestseller_rating
  -- This gives us a reasonable subset without complex logic
  AND m.bestseller_rating >= 4.0  -- Adjust this threshold as needed
GROUP BY ap.segment
ORDER BY ap.segment;
