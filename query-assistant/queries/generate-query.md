# Generate Query

## User Prompt
I want a query that summarizes the overall performance of an A/B Test.

## Expected Query Output
- Use `events` table
- Use `session_id` as unique session identifier.
- Use the starting period `date >= '2025-08-06'` 
- The A/B test keyword is `CVC` and the values are `'A: Original', 'B: Cart group', 'C: Cart on Preview'`
- Here is the list of events depending on the action:
* search: `type = 'appearedInSearch'` and `page_url like 'https://eduki.com/de/suchergebnisse%'`
* click to mp: `type = 'click'` AND `page_url LIKE 'https://eduki.com/de/suchergebnisse%'` AND `source = 'search'` AND `internal_path = 'sp'` AND e.`item_id IS NOT NULL` AND `position IS NOT NULL`
* A2F: `type = 'addToFavorites'`
* A2C:  `type = 'addToCart'`
* Conversion: `type = 'purchase'`  
- include order data to calculate GMV/session and join it with the converstion
- The rate fields should be used as denominator the total number of sessions for the variant.
- Return: a/b test variant, total_sessions, percentage_of_sessions, number of searches, CTR_to_MP, A2F_rate, A2C_rate, Converstion Rate, GMV/session.

## Environment
Target: BigQuery
Project: `gtm-eduki-com`
Dataset: `QE`