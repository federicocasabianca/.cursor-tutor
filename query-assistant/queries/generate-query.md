# Generate Query

## User Prompt
Obtain the folder usage as part of the wishlist.

## Expected Query Output
- Filter by world `world = 'de'` and `date >= CURRENT_DATE() - 3m`
- App orders `user_device NOT IN ('desktop', 'tablet', 'mobile') and AND os in ('android', 'ios')`  
- Add element to wishlist `type = 'addToFavorites'`
- Create a new folder `type = 'createFolder'`
- Update an existing folder `type = 'updateFolder'`
- Remove an existing folder `type = 'removeFolder'`
- Filter by `session_id is not null` and `user_id is not null`
- Return: total sessions, total add to wishlist, total create new folder, % of create folders on total add to wishlist, total update new folder, % of update folders on total add to wishlist, total remove new folder, % of remove folders on total add to wishlist.

## Environment
Target: BigQuery
Project: `gtm-eduki-com`
Dataset: `QE`

## Query
```sql
WITH filtered_events AS (
  SELECT
    session_id,
    user_id,
    type
  FROM `gtm-eduki-com.QE.events`
  WHERE world = 'de'
    AND DATE(event_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH)
    AND user_device NOT IN ('desktop', 'tablet', 'mobile')
    AND os IN ('android', 'ios')
    AND session_id IS NOT NULL
    AND user_id IS NOT NULL
),
session_totals AS (
  SELECT COUNT(DISTINCT session_id) AS total_sessions
  FROM filtered_events
),
event_totals AS (
  SELECT
    SUM(CASE WHEN type = 'addToFavorites' THEN 1 ELSE 0 END) AS total_add_to_wishlist,
    SUM(CASE WHEN type = 'createFolder' THEN 1 ELSE 0 END) AS total_create_folder,
    SUM(CASE WHEN type = 'updateFolder' THEN 1 ELSE 0 END) AS total_update_folder,
    SUM(CASE WHEN type = 'removeFolder' THEN 1 ELSE 0 END) AS total_remove_folder
  FROM filtered_events
)
SELECT
  st.total_sessions,
  et.total_add_to_wishlist,
  et.total_create_folder,
  SAFE_DIVIDE(et.total_create_folder, et.total_add_to_wishlist) AS pct_create_folder_of_adds,
  et.total_update_folder,
  SAFE_DIVIDE(et.total_update_folder, et.total_add_to_wishlist) AS pct_update_folder_of_adds,
  et.total_remove_folder,
  SAFE_DIVIDE(et.total_remove_folder, et.total_add_to_wishlist) AS pct_remove_folder_of_adds
FROM session_totals st
CROSS JOIN event_totals et;
```