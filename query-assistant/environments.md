# Query Assistant - Environments & Examples

This document is the **single source of truth** for all supported environments, syntax conventions, and examples.

## Supported Environments

### BigQuery

**Target**: BigQuery  
**Project**: `gtm-eduki-com` (or your project name)  
**Dataset**: `QE` (or your dataset name)

#### Syntax Conventions
- **Table names**: Use backticks for fully qualified names: `project.dataset.table`
- **Date functions**: `DATE_SUB(CURRENT_DATE(), INTERVAL X DAY)`
- **Array handling**: Use `UNNEST()` for array operations
- **String functions**: Standard SQL functions like `LOWER()`, `LIKE`
- **Multi-schema**: Use `project.schema.table` format

#### Example Queries

**Basic Search Frequency Query**:
```sql
SELECT
  query,
  COUNT(*) as frequency
FROM
  `gtm-eduki-com.QE.events`
WHERE
  type = 'appearedInSearch'
  AND DATE(date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 180 DAY)
  AND world = 'es'
  AND (
    LOWER(query) LIKE '%verano%'
    OR LOWER(query) LIKE '%invierno%'
    OR LOWER(query) LIKE '%primavera%'
    OR LOWER(query) LIKE '%otoño%'
  )
GROUP BY
  query
ORDER BY
  frequency DESC
```

**A/B Test Filtering**:
```sql
SELECT
  session_id,
  query,
  COUNT(*) as frequency
FROM
  `gtm-eduki-com.QE.events`
WHERE
  type = 'appearedInSearch'
  AND DATE(date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
  AND EXISTS (
    SELECT 1 FROM UNNEST(ab_tests.key) AS k WITH OFFSET i
    JOIN UNNEST(ab_tests.value) AS v WITH OFFSET j
    ON i = j
    WHERE k = 'DES' AND v IN ('A', 'B')
  )
GROUP BY
  session_id, query
ORDER BY
  frequency DESC
```

**Multi-Schema Join Example**:
```sql
SELECT 
    e.session_id,
    u.user_id,
    up.segment_name,
    c.campaign_name,
    COUNT(*) as event_count
FROM 
    `gtm-eduki-com.QE.events` e
    JOIN `gtm-eduki-com.QE.users` u ON e.user_id = u.id
    JOIN `gtm-eduki-com.analytics.user_profiles` up ON u.id = up.user_id
    JOIN `gtm-eduki-com.marketing.campaigns` c ON e.campaign_id = c.id
WHERE 
    e.world = 'de'
    AND e.date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY 
    e.session_id, u.user_id, up.segment_name, c.campaign_name
```

### Clickhouse with Metabase

**Target**: Clickhouse with Metabase  
**Project**: not applicable  
**Dataset**: not applicable

#### Syntax Conventions
- **Table names**: Use standard table names without backticks: `table_name`
- **Date functions**: `today() - INTERVAL X DAY`
- **Array handling**: Use `indexOf()` and `arrayElement()` for array operations
- **String functions**: Clickhouse-specific functions like `lower()`, `like`
- **Multi-schema**: Use `schema.table` format

#### Example Queries

**Basic Search Frequency Query**:
```sql
SELECT
  query,
  COUNT(*) as frequency
FROM
  QE.events
WHERE
  type = 'appearedInSearch'
  AND date >= today() - INTERVAL 180 DAY
  AND world = 'es'
  AND (
    lower(query) LIKE '%verano%'
    OR lower(query) LIKE '%invierno%'
    OR lower(query) LIKE '%primavera%'
    OR lower(query) LIKE '%otoño%'
  )
GROUP BY
  query
ORDER BY
  frequency DESC
```

**A/B Test Filtering with Array Operations**:
```sql
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
```

**Multi-Schema Join Example**:
```sql
SELECT 
    e.session_id,
    u.user_id,
    up.segment_name,
    c.campaign_name,
    COUNT(*) as event_count
FROM 
    QE.events e
    JOIN QE.users u ON e.user_id = u.id
    JOIN analytics.user_profiles up ON u.id = up.user_id
    JOIN marketing.campaigns c ON e.campaign_id = c.id
WHERE 
    e.world = 'de'
    AND e.date >= today() - INTERVAL 30 DAY
GROUP BY 
    e.session_id, u.user_id, up.segment_name, c.campaign_name
```

## Multi-Schema Join Templates

### Enhanced Query Template for Multi-Schema Joins

When creating queries that join tables from different schemas, use this enhanced template:

```markdown
# Generate Query

## User Prompt
[Your specific query description here]

## Expected Query Output
[Your specific requirements and filters]

## Environment
Target: [BigQuery or Clickhouse with Metabase]
Project: [your project name or not applicable]
Dataset: [your dataset name or not applicable]

## Schema Configuration
### Primary Schema
- **Schema Name**: `QE`
- **Tables**: `events`, `users`, `sessions`

### Secondary Schemas (if needed)
- **Schema Name**: `analytics`
- **Tables**: `user_profiles`, `user_behavior`
- **Schema Name**: `marketing`
- **Tables**: `campaigns`, `banner_configs`

### Join Relationships
- `QE.events.session_id` → `QE.sessions.id`
- `QE.events.user_id` → `analytics.user_profiles.user_id`
- `QE.events.campaign_id` → `marketing.campaigns.id`
```

### Multi-Schema Join Examples

#### Example 1: Simple Multi-Schema Join
```markdown
## Schema Configuration
### Primary Schema
- **Schema Name**: `QE`
- **Tables**: `events`

### Secondary Schemas (if needed)
- **Schema Name**: `lmp`
- **Tables**: `materials`, `orders`, `order_items`, `material_categories`, `material_class_grade`, `material_type`, `materials_categories`   

### Join Relationships
- `QE.events.item_id` → `lmp.materials.id`
- `QE.events.user_id` → `lmp.users.id`
- `QE.events.purchase_id` → `lmp.orders.number`
- `lmp.orders.id` → `lmp.order_items.order_id`
- `lmp.materials.id` → `lmp.material_categories.material_id`
- `lmp.material_categories.id` → `lmp.material_categories.material_category_id`
- `lmp.materials.id` → `lmp.order_items.order_id`
```

## Key Differences Between Environments

1. **Table names**: BigQuery uses backticks (`project.dataset.table`), Clickhouse uses standard names (`table_name`)
2. **Date functions**: BigQuery uses `DATE_SUB(CURRENT_DATE(), INTERVAL X DAY)`, Clickhouse uses `today() - INTERVAL X DAY`
3. **String functions**: BigQuery uses `LOWER()`, Clickhouse uses `lower()`
4. **Array handling**: 
   - BigQuery: `UNNEST()` with JOIN
   - Clickhouse: `indexOf()` and `arrayElement()`
5. **Multi-schema syntax**:
   - BigQuery: `project.schema.table`
   - Clickhouse: `schema.table`

## Common Patterns

### A/B Test Filtering
- **BigQuery**: `EXISTS(SELECT 1 FROM UNNEST(ab_tests.key) AS k WITH OFFSET i JOIN UNNEST(ab_tests.value) AS v WITH OFFSET j ON i = j WHERE k = 'DES' AND v IN ('A','B'))`
- **Clickhouse**: `indexOf(ab_tests.key, 'DES') > 0 AND arrayElement(ab_tests.value, indexOf(ab_tests.key, 'DES')) IN ('A', 'B')`

### Date Filtering
- **BigQuery**: `DATE(date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 180 DAY)`
- **Clickhouse**: `date >= today() - INTERVAL 180 DAY`

### String Pattern Matching
- **BigQuery**: `LOWER(query) LIKE '%pattern%'`
- **Clickhouse**: `lower(query) LIKE '%pattern%'`

### Multi-Schema Joins
- **BigQuery**: `project.schema.table` format with backticks
- **Clickhouse**: `schema.table` format without backticks

### Additional tables (User Segments, Personalisations, Free downloads)
- **User Segments** (current and history): `Segments.lcs_history` — BigQuery: `` `gtm-eduki-com.Segments.lcs_history` ``; Clickhouse: `Segments.lcs_history`. Joins on `user_id` to `QE.events.user_id` and `lmp.users.id`.
- **Personalisations** (category/grade preferences): `lmp.personalisations` — BigQuery: `` `gtm-eduki-com.lmp.personalisations` ``; Clickhouse: `lmp.personalisations`. Joins on `user_id` to `QE.events.user_id`, `lmp.users.id`, and `Segments.lcs_history.user_id`.
- **Free downloads** (acl_free): `lmp.acl_free` — BigQuery: `` `gtm-eduki-com.lmp.acl_free` ``; Clickhouse: `lmp.acl_free`. Contains free material downloads. Joins: `material_id` → `lmp.materials.id`; `user_id` → `lmp.users.id`, `QE.events.user_id`. See [joins.md](joins.md) for the full join map.

## Usage Instructions

When generating queries, the agent should:

1. **Check the `Environment` section** in the query specification
2. **Use the appropriate syntax** for the specified environment
3. **Apply environment-specific rules** and conventions
4. **Generate queries** that are compatible with the target system
5. **For multi-schema joins**: Use the enhanced template with schema configuration

## Environment Selection Examples

### BigQuery Specification
```markdown
## Environment
Target: BigQuery
Project: `gtm-eduki-com`
Dataset: `QE`
```

### Clickhouse Specification
```markdown
## Environment
Target: Clickhouse with Metabase
Project: not applicable
Dataset: not applicable
```

## Troubleshooting

### Common Issues
1. **Wrong table naming**: Ensure backticks for BigQuery, standard names for Clickhouse
2. **Date function errors**: Use environment-specific date functions
3. **Array operation failures**: Use correct array syntax for each environment
4. **String function errors**: Use environment-specific string functions
5. **Multi-schema join errors**: Use correct schema.table format for each environment

### Validation Checklist
- [ ] Table names follow environment conventions
- [ ] Date functions use correct syntax
- [ ] Array operations use environment-specific methods
- [ ] String functions use correct casing
- [ ] Multi-schema joins use correct format
- [ ] Query syntax is compatible with target environment