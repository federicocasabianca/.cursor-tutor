# Generate Query

## User Prompt
I want to summarize the performance for an A/B for different visualizations listView and gridView.

## Expected Query Output
- Use `events` table
- Use the starting period `date >= '2025-08-06'`
- Filter by world `world = 'de'`
- This is an A/B test with the ab_test_key `CVC` and variants are `B: Cart group or C: Cart on Preview`
- The field to identify the visualization_type are `extra in ('listView','gridView')`.
- Calculate the total number of sessions
- Calculate the total number of each visualizationType
- Calculate the % for each visualization_type out of total number of sessions
- Calculate the addToFavorites from search page.
* `type = 'addToFavorites' and page_url like 'https://eduki.com/de/suchergebnisse%'`
- Calculate the removeToFavorite from search page.
* `type = 'removeFromFavorites' and page_url like 'https://eduki.com/de/suchergebnisse%'`
- Calculate the addToCart from search page.
* `type = 'addToCart' and page_url like 'https://eduki.com/de/suchergebnisse%'`
- Calculate the time in minutes to conversion after adding to favorites.
* The conversion event is `type = 'purchase'` and `time` of purchase should be higher than `type = 'addToFavorites'`
- Calculate the time in minutes to conversion after adding to cart.
* The conversion event is `type = 'purchase'` and `time` of purchase should be higher than `type = 'addToCart'`
- Group by variant, visualization_type
- Return: visualization_type, total_sessions, total_number_visualization_type, %_of_sessions, add2Favorites, removeFromFavorites, add2Cart, conversion_after_favorites, conversion_after_cart

## Environment
Target: BigQuery
Project: `gtm-eduki-com`
Dataset: `QE`