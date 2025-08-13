# Query Assistant

A comprehensive query generation system that supports multiple database environments including BigQuery and Clickhouse with Metabase.

## Overview

The Query Assistant helps generate SQL queries for different database environments with environment-specific syntax and conventions. It provides templates, rules, and examples to ensure consistent and correct query generation.

## Supported Environments

### BigQuery
- **Target**: BigQuery
- **Project**: `gtm-eduki-com` (or your project name)
- **Dataset**: `QE` (or your dataset name)
- **Syntax**: Uses BigQuery SQL syntax with backticks for table names

### Clickhouse with Metabase
- **Target**: Clickhouse with Metabase
- **Project**: not applicable
- **Dataset**: not applicable
- **Syntax**: Uses Clickhouse SQL syntax with standard table names

## Project Structure

```
query-assistant/
├── README.md                 # This file
├── environments.md           # Environment documentation
├── queries/
│   └── generate-query.md     # Query generation template
├── templates/
│   ├── bq-query-template.sql        # BigQuery template
│   ├── clickhouse-query-template.sql # Clickhouse template
│   └── ...                          # Other templates
├── rules/
│   ├── filters.mdc           # Filter rules for all environments
│   └── ab-test.mdc           # A/B test rules for all environments
├── examples/
│   ├── search-frequency-query.md    # Basic example
│   └── multi-environment-example.md # Multi-environment example
└── schema/
    └── qe_events.schema.json # Schema definitions
```

## Usage

### 1. Define Your Query

Create a query specification in the `queries/` directory or use the existing `generate-query.md` template:

```markdown
# Generate Query

## User Prompt
Your query description here

## Expected Query Output
Expected output description

## Environment
Target: BigQuery  # or "Clickhouse with Metabase"
Project: `your-project`
Dataset: `your-dataset`
```

### 2. Environment-Specific Rules

The system automatically applies environment-specific rules:

- **Date functions**: BigQuery uses `DATE_SUB(CURRENT_DATE(), INTERVAL X DAY)`, Clickhouse uses `today() - INTERVAL X DAY`
- **Table names**: BigQuery uses backticks (`project.dataset.table`), Clickhouse uses standard names (`table_name`)
- **Array handling**: BigQuery uses `UNNEST()`, Clickhouse uses `hasAny()`
- **String functions**: BigQuery uses `LOWER()`, Clickhouse uses `lower()`

### 3. Query Generation

The agent will:
1. Read the environment specification
2. Apply environment-specific rules and syntax
3. Generate a query compatible with the target system
4. Use appropriate templates and conventions

## Examples

### BigQuery Example
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
GROUP BY
  query
ORDER BY
  frequency DESC
```

### Clickhouse Example
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
GROUP BY
  query
ORDER BY
  frequency DESC
```

## Rules and Conventions

### Filters (`rules/filters.mdc`)
- Time filter syntax for different environments
- Search query handling
- Table naming conventions

### A/B Testing (`rules/ab-test.mdc`)
- Array handling for different environments
- Segment filtering syntax
- Environment-specific array operations

## Adding New Environments

To add a new environment:

1. **Update `environments.md`** with the new environment's syntax and conventions
2. **Create a template** in `templates/` directory
3. **Update rules** in `rules/` directory to handle the new environment
4. **Add examples** in `examples/` directory
5. **Update `generate-query.md`** to include the new environment option

## Contributing

When contributing to this project:

1. Follow the existing structure and conventions
2. Update documentation for any new features
3. Add examples for new functionality
4. Test queries in the target environment before committing
