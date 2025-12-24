# Generate Query

## User Prompt
Count the total free materials in DACH, the total free materials downloads in 2025, the % of materials (1%, 10%, 20%, and +25%) that represents the % of free downloads.

## Expected Query Output
- Filter by `date between '2025-01-01' AND CURRENT_DATE() AND world = 'de' AND session_id is not null and user_id is not null`
- Filter by search sessions `'type ='freeDownload'` and `item_id`and the material id.
- In order to know the distinct materials we need to join the `QE.events.item_id` table with `lmp.materials.id`
- Return: Year, Total Free Downloads, Total unique.

## Environment
Target: BigQuery
Project: `gtm-eduki-com`
Dataset: `QE`