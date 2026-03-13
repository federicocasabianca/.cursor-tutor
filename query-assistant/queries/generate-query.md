# Generate Query

## How to use this file

1. Fill the **Current request** section below (Instruction, Expected output, Source(s), Environment, Output path).
2. Ask the AI to generate the query. It will: resolve Source(s) from [sources.md](../sources.md), load the listed schema files, use [environments.md](../environments.md) for syntax and [joins.md](../joins.md) for table joins, then write the SQL to the path you set.
3. For **A/B test** requests, the AI will also use [rules/ab-test.mdc](../rules/ab-test.mdc) and [rules/ab-test-columns.md](../rules/ab-test-columns.md).
4. Replace the "Current request" and "Generated SQL" blocks when you start a new query.

---

## Current request

**Instruction**  
I want to pull the most frequent search queries during a period of time.

**Expected output**
- Common filters: world = 'de' AND session_id IS NOT NULL AND user_id IS NOT NULL
- Date range: date between '2026-02-22' and '2026-02-23' 
- Purchased Material: type = 'pageView' and page_url LIKE 'https://eduki.com/de/suchergebnisse?query=%' AND query != ''
- Please don't consider the case sensitive cases. For instance 'Herbst' should be counted as 'herbst'.
- Return: a list of the most frequent queries with the query (lowercase) and frequency.

**Source(s)**  
QE

**Environment**  
BigQuery 

**Output path**  
`query-assistant/output/frequent_searches.sql`