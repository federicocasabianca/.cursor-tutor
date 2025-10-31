# Generate Query

## User Prompt
We need to calculate type of material (Standalone, hybrid, interactive) for our current bestsellers.

## Expected Query Output
- Filter by world `world = 'de'`
- Table we need to look at `gtm-eduki-com.lmp.material_categories` and pull the unique best_material_id
- We need to join the previous best_material_id with the `gtm-eduki-com.lmp.materials` id column
- Interactive id is identified in the `gtm-eduki-com.lmp.materials` interactive_id
- Bundle is identified in the `gtm-eduki-com.lmp.materials` is_bundle = 1
- Return: The count of bestseller materials that are interactive and bundle

## Environment
Target: BigQuery
Project: `gtm-eduki-com`
Dataset: `QE`

## Generated Query

```sql
SELECT COUNT(DISTINCT mc.best_material_id) AS count_interactive_bundle_bestsellers
FROM `gtm-eduki-com.lmp.material_categories` mc
INNER JOIN `gtm-eduki-com.lmp.materials` m
  ON mc.best_material_id = m.id
WHERE mc.world = 'de'
  AND m.interactive_id IS NOT NULL
  AND m.is_bundle = 1;
```

## Query Explanation

This query:
1. Selects distinct `best_material_id` from `material_categories` filtered by `world = 'de'`
2. Joins with `materials` table matching `best_material_id` to `materials.id`
3. Filters for materials that are both interactive (`interactive_id IS NOT NULL`) and bundle (`is_bundle = 1`)
4. Returns the count of unique bestseller materials meeting these criteria