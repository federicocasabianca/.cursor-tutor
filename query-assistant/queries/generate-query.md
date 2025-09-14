# Generate Query

## User Prompt
I want to know the total number of materials that meet a specific criteria.

## Expected Query Output
- Use `author_profiles` and `materials`
- Filter by world `world = 'de'`
- Select the `user_id` from the `author_profiles` where segment in (`'dragon','bear','cub'`) 
- Join the previous data with the `materials` table by `author_id`
- Filter the elements by `materials` where `is_bundle = 0 AND interactive_id IS NULL AND (is_standalone_interactive = 0 OR is_standalone_interactive IS NULL) AND deleted_at IS NULL AND status NOT IN ('deleted', 'inactive')`
- Use `custom_pages_total`, if available, otherwise `total_pages`
- Filter the top 20 materials for each user_id ordered desc by bestseller_rating
- Return: segment, total number of materials 

## Environment
Target: Clickhouse with Metabase
Project: not applicable
Dataset: not applicable