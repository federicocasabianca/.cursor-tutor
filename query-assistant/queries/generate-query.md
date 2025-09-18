# Generate Query

## User Prompt
I want to know the performance (CTR general, CTR@K, CR/saerch, GMV/session) of the sessions where ONLY search suggestion was used 

## Expected Query Output
- Filter by world `world = 'de'` and `date >= '2025-04-01'` (date has a DATE format, doesn't require any transformation).
- Use the `session_id` column to know the unique sessions. 
- Filter only by the sessions where a `type = 'appearedInSearch'` and `type = 'selectedSearchSuggestion'` happened.
- Calutate the overall CTR: `type = 'click'` and `page_url like 'https://eduki.com/de/suchergebnisse?query=%'` and `internal_path = 'sp'` and `source = 'search'`.
- Calutate the CTR@k: use the overall CTR but using `position` to know the @k that has been clicked.
- Calutate the CR/search: sessions where `type = 'purchase'` ocurred / total suggestion search sessions.
- Use the following code:
### BigQuery Example
```sql
purchase_map AS (
  -- Pedidos vistos en cualquier evento de esas sesiones, dentro de la ventana
  SELECT DISTINCT
    s.session_id,
    s.user_id,
    CAST(e.purchase_id AS STRING) AS order_number
  FROM `QE.events` e
  inner JOIN mp_sessions s USING (session_id, user_id)
  WHERE e.date >= '2025-04-01'
    AND e.purchase_id IS NOT NULL
),
orders AS (
  SELECT
    CAST(o.number AS STRING) AS order_number,
    o.user_id,
    SUM(it.final_price) AS gmv
  FROM `gtm-eduki-com.lmp.orders` o
  LEFT JOIN `gtm-eduki-com.lmp.order_items` it
    ON o.id = it.order_id
  WHERE o.status NOT IN ('new','pending','cancelled')
  GROUP BY order_number, o.user_id
),
session_revenue AS (
  SELECT
    sf.session_id,
    sf.user_id,
    COUNT(DISTINCT o.order_number) AS orders,
    SUM(o.gmv) AS gmv
  FROM session_features sf
  LEFT JOIN purchase_map pm USING (session_id, user_id)
  LEFT JOIN orders o
    ON o.order_number = pm.order_number
   AND o.user_id     = pm.user_id
  GROUP BY sf.session_id, sf.user_id
)
```
to calculate the GMV/session and CR/search.
- Group the % by month
- Return: month, total suggestion search session, CTR ovearll, CTR@1, CTR@2, CTR@3, CTR@4, CTR@5, CTR@6-12, CR/search, GMV/session.  

## Environment
Target: BigQuery
Project: `gtm-eduki-com`
Dataset: `QE`