# Generate Query

## User Prompt
Pull the total unique number of sessions where the marketing banner has been printed and the % of sessions where the banner has been clicked for DE world from the '2025-08-06'

## Expected Query Output
- Use `events` table  
- Filter for printed marketing banner: `world = 'de'` and `type = 'marketingBarEvent'` and `date >= '2025-08-06'` and `page_url='https://eduki.com/de'` and `user_device in ('desktop', 'mobile', 'tablet')`
- Filter for banner clicks: `world = 'de'` and `type = 'back-to-school-2025-page-view'` and `date >= '2025-08-06'` and `page_url='https://eduki.com/de/gewinnspiel'` and `user_device in ('desktop', 'mobile', 'tablet')` and `referrer = 'https://eduki.com/de'`
- Calculate CTR (Click-Through-Rate) as a percentage
- Return: sessions_banner_impressions, sessions_banner_clicks, ctr_banner

## Environment
Target: Clickhouse with Metabase
Project: not applicable
Dataset: not applicable