# Query Assistant

Generate SQL for BigQuery or Clickhouse (Metabase) from a short request: you choose **Source(s)** and **Environment**; the AI loads the right schemas and syntax and writes the query to an **output folder**.

## Quick start (3 steps)

1. **Choose Source(s)** from [sources.md](sources.md) (e.g. QE, LMP, or QE+LMP).
2. **Fill the request** in [queries/generate-query.md](queries/generate-query.md): Instruction, Expected output, Source(s), Environment, and **Output path** (e.g. `query-assistant/output/my-query.sql`).
3. **Ask the AI** to generate the query. It will load the schemas for your source(s), apply [environments.md](environments.md) for syntax and [joins.md](joins.md) for joins, then write the SQL to the path you set.

Generated queries are written to **`query-assistant/output/`** (or the path you specify in the request).

## How the AI generates a query

1. Read **Source(s)** from the request and resolve them in [sources.md](sources.md).
2. **Load** the schema file(s) listed for that source (from `schema/*.json`).
3. For multi-table queries, use **only** the relationships in [joins.md](joins.md).
4. Read [environments.md](environments.md) for the target environment (BigQuery vs Clickhouse) and apply the correct syntax.
5. For **A/B test** requests, also use [rules/ab-test.mdc](rules/ab-test.mdc) and [rules/ab-test-columns.md](rules/ab-test-columns.md).
6. **Write** the generated SQL to the path given in the request (default: under `query-assistant/output/`).

## Project structure

```
query-assistant/
├── README.md                 # This file + quick start
├── sources.md                # Source definitions and schema file list
├── joins.md                  # Table join map (single source of truth)
├── environments.md           # Environment syntax (BigQuery vs Clickhouse)
├── queries/
│   └── generate-query.md     # Request form + generated SQL
├── output/                   # Generated queries (or path you set per request)
├── schema/                   # Per-table schema JSON (qe_events, lmp_*, …)
├── rules/
│   ├── filters.mdc          # Time/search/table rules
│   ├── ab-test.mdc          # A/B test syntax by environment
│   ├── ab-test-columns.md    # Columns to pull for A/B test analysis
│   ├── order-data.mdc       # Order/purchase joins
│   └── ...
└── templates/                # Example SQL by domain (reference)
```

## Supported environments

- **BigQuery**: backticks for tables, `DATE_SUB(CURRENT_DATE(), INTERVAL X DAY)`, `UNNEST()` for arrays. Project/dataset from [sources.md](sources.md).
- **Clickhouse with Metabase**: `QE.events`-style names, `today() - INTERVAL X DAY`, `indexOf` / `arrayElement` for arrays. See [environments.md](environments.md) for full conventions.

## Adding a source or join

- **New source**: Add a row in [sources.md](sources.md) (name, environment, project/schema, list of `schema/*.json` files). If it joins to others, add rows in [joins.md](joins.md).
- **New join**: Add one row in [joins.md](joins.md): left table.column → right table.column.

## Contributing

1. Keep schema files and join map up to date when tables change.
2. Add or adjust rules in `rules/` when you introduce new patterns (e.g. a new analysis type).
3. Test generated queries in the target environment before committing.
