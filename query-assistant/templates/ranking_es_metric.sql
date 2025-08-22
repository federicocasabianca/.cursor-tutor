WITH search_results AS (
  SELECT 
    -- Generate unique identifier for each search execution
    CONCAT(query, '-', CAST(time AS STRING)) as search_execution_id,
    query,
    -- Remove leading/trailing quotes and parse JSON array
    JSON_EXTRACT_ARRAY(REGEXP_REPLACE(extra, r'^"|"$', '')) as results_array
  FROM `gtm-eduki-com.QE.events`
  WHERE world = 'es' 
    AND type = 'appearedInSearch' 
    AND date >= '2025-08-12' 
    AND query != '' 
    AND page_url LIKE 'https://eduki.com/es/resultados-busqueda?query=%' 
    AND extra != ''
),

flattened_results AS (
  SELECT 
    search_execution_id,
    query,
    -- Extract index (position within array, starting from 0) and price from each result
    CAST(JSON_EXTRACT_SCALAR(result, '$.index') AS INT64) as index,
    CAST(JSON_EXTRACT_SCALAR(result, '$.price') AS FLOAT64) as price
  FROM search_results
  CROSS JOIN UNNEST(results_array) as result
  WHERE JSON_EXTRACT_SCALAR(result, '$.price') IS NOT NULL
    AND JSON_EXTRACT_SCALAR(result, '$.index') IS NOT NULL
    -- Accept all results (index 0-35, but we might have fewer than 36)
    AND CAST(JSON_EXTRACT_SCALAR(result, '$.index') AS INT64) < 36
),

price_metrics AS (
  SELECT 
    search_execution_id,
    query,
    -- Basic statistics
    AVG(price) as avg_price,
    STDDEV(price) as std_dev_price,
    COUNT(*) as total_results,
    
    -- Price threshold counts
    SUM(CASE WHEN price > 0 THEN 1 ELSE 0 END) as above_0,
    SUM(CASE WHEN price > 2 THEN 1 ELSE 0 END) as above_2,
    SUM(CASE WHEN price > 5 THEN 1 ELSE 0 END) as above_5,
    SUM(CASE WHEN price > 10 THEN 1 ELSE 0 END) as above_10,
    
    -- Top 12 and top 36 sums for share calculation (adjusting for 0-based indexing)
    SUM(CASE WHEN index < 12 THEN price ELSE 0 END) as top_12_sum,
    SUM(price) as top_36_sum,
    
    -- Collect all prices for percentile calculations
    ARRAY_AGG(price ORDER BY price) as price_array
  FROM flattened_results
  GROUP BY search_execution_id, query
),

percentile_calculations AS (
  SELECT 
    search_execution_id,
    query,
    avg_price,
    std_dev_price,
    total_results,
    above_0,
    above_2,
    above_5,
    above_10,
    top_12_sum,
    top_36_sum,
    -- Calculate percentiles from the sorted array with proper bounds checking
    CASE 
      WHEN total_results > 0 THEN 
        price_array[OFFSET(GREATEST(0, LEAST(CAST(total_results * 0.25 AS INT64), total_results - 1)))]
      ELSE NULL 
    END as q1,
    CASE 
      WHEN total_results > 0 THEN 
        price_array[OFFSET(GREATEST(0, LEAST(CAST(total_results * 0.75 AS INT64), total_results - 1)))]
      ELSE NULL 
    END as q3
  FROM price_metrics
),

gini_calculation AS (
  SELECT 
    fr.search_execution_id,
    fr.query,
    pc.avg_price,
    pc.std_dev_price,
    pc.total_results,
    pc.above_0,
    pc.above_2,
    pc.above_5,
    pc.above_10,
    pc.top_12_sum,
    pc.top_36_sum,
    pc.q1,
    pc.q3,
    -- Calculate Gini coefficient components
    SUM(ABS(fr.price - pc.avg_price)) as sum_abs_diff
  FROM flattened_results fr
  JOIN percentile_calculations pc ON fr.search_execution_id = pc.search_execution_id
  GROUP BY 
    fr.search_execution_id, fr.query, pc.avg_price, pc.std_dev_price, pc.total_results,
    pc.above_0, pc.above_2, pc.above_5, pc.above_10,
    pc.top_12_sum, pc.top_36_sum, pc.q1, pc.q3
),

final_metrics AS (
  SELECT 
    search_execution_id,
    query,
    total_results,
    avg_price,
    std_dev_price,
    -- Calculate IQR (handle NULL cases)
    CASE 
      WHEN q1 IS NOT NULL AND q3 IS NOT NULL THEN (q3 - q1)
      ELSE NULL 
    END as iqr,
    
    -- Calculate Gini Coefficient using pre-calculated components (handle edge cases)
    CASE 
      WHEN total_results > 0 AND avg_price > 0 THEN (1.0 - (sum_abs_diff / (2 * total_results * avg_price)))
      ELSE NULL 
    END as gini_coefficient,
    
    -- Calculate percentages above thresholds
    ROUND((above_0 / total_results) * 100, 2) as pct_above_0,
    ROUND((above_2 / total_results) * 100, 2) as pct_above_2,
    ROUND((above_5 / total_results) * 100, 2) as pct_above_5,
    ROUND((above_10 / total_results) * 100, 2) as pct_above_10,
    
    -- Calculate share of total price in top-12 vs top-36 (handle division by zero)
    CASE 
      WHEN top_36_sum > 0 THEN ROUND((top_12_sum / top_36_sum) * 100, 2)
      ELSE NULL 
    END as share_top_12_vs_36
  FROM gini_calculation
)

SELECT 
  search_execution_id,
  query,
  total_results,
  ROUND(avg_price, 2) as average_price,
  ROUND(std_dev_price, 2) as standard_deviation,
  ROUND(iqr, 2) as interquartile_range,
  ROUND(gini_coefficient, 4) as gini_coefficient,
  pct_above_0 as pct_above_0_euro,
  pct_above_2 as pct_above_2_euro,
  pct_above_5 as pct_above_5_euro,
  pct_above_10 as pct_above_10_euro,
  share_top_12_vs_36 as share_top_12_vs_top_36,
  -- Add execution timestamp for reference
  CURRENT_DATETIME() as execution_timestamp
FROM final_metrics
ORDER BY query, search_execution_id