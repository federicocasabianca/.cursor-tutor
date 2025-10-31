# Locker Dashboard Setup Guide: Search Quality Metrics

This guide explains how to create a Locker dashboard with your 4 BigQuery queries.

## Dashboard Structure

Create a dashboard with 4 visualizations:

1. **Overall Summary** (Card/Summary view)
2. **Daily Trend** (Time series/Line chart)
3. **Failure Reasons Breakdown** (Bar chart)
4. **Top 20 Problematic Queries** (Table)

## Step-by-Step Instructions

### 1. Create a New Dashboard in Locker

- In Locker, create a new dashboard called "Search Quality Metrics"
- Set the default time range to "Last 30 days"

### 2. Add Visualization 1: Overall Summary

**Title**: Search Quality Overview

**Visualization Type**: Summary Card or Table

**Query**: Use your main query from `generate-query.md` (lines 24-54)

**Expected Result**:
- Two rows showing GOOD_RESULTS and NOT_GOOD_RESULTS percentages
- Total queries count
- Unique sessions and users

**Configuration**:
- Display as: Summary cards or simple table
- Highlight percentage column

### 3. Add Visualization 2: Daily Trend

**Title**: Daily GOOD vs NOT_GOOD Breakdown

**Visualization Type**: Line Chart or Time Series

**Query**: Use "Day-by-day GOOD vs NO_GOOD breakdown" query (lines 157-207)

**Configuration**:
- X-axis: `date`
- Y-axis: `good_percentage` and `not_good_percentage`
- Chart type: Dual-axis line chart
- Show as: Two lines (good in green, not_good in red)

### 4. Add Visualization 3: Failure Reasons

**Title**: Reasons for NOT_GOOD_RESULTS

**Visualization Type**: Bar Chart or Pie Chart

**Query**: Use "Breakdown of reasons for NO_GOOD_RESULTS" query (lines 71-122)

**Configuration**:
- X-axis: `reason`
- Y-axis: `count` or `percentage`
- Sort by: Count descending
- Color-code by percentage

### 5. Add Visualization 4: Top Problem Queries

**Title**: Top 20 Most Frequent NOT_GOOD_RESULTS Queries

**Visualization Type**: Table

**Query**: Use "Top 20 most frequent NOT_GOOD_RESULTS queries" (lines 210-237)

**Configuration**:
- Columns: query, frequency, unique_sessions, unique_users, percentage
- Sort by: frequency descending
- Limit: 20 rows
- Make query column clickable (link back to search results if possible)

## Recommended Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│                   Search Quality Metrics                     │
├─────────────────────┬───────────────────────────────────────┤
│ Overall Summary     │  Daily Trend (Line Chart)             │
│ (Summary Cards)      │  GOOD vs NOT_GOOD over time          │
│ GOOD_RESULTS: X%    │                                       │
│ NOT_GOOD: Y%        │                                       │
│                     │                                       │
├─────────────────────┴───────────────────────────────────────┤
│  Failure Reasons Breakdown         │  Top 20 Problem Queries │
│  (Bar Chart showing reasons)        │  (Table sorted by freq) │
│  • margin < 0.35                   │  Query | Freq | %       │
│  • category_concentration < 0.6     │  ...                    │
│  • grade_coverage < 0.7             │                         │
│  etc.                               │                         │
└─────────────────────────────────────┴─────────────────────────┘
```

## Tips for Dashboard Creation

### 1. Refresh Settings
- Set data refresh to: Every hour (or as needed)
- Cache results for: 15-30 minutes

### 2. Filters (Optional)
Add dashboard-level filters for:
- **World**: Default to 'de', allow selection
- **Date range**: Default to last 30 days, allow custom range
- **Type**: Default to 'searchServeMetrics'

### 3. Interactive Elements
- Make the "Top 20" table rows clickable
- Add tooltips explaining each metric
- Add annotations for significant dates or events

### 4. Alerts (Optional)
Set up alerts when:
- NOT_GOOD_RESULTS percentage exceeds X% (e.g., 40%)
- A specific failure reason spikes significantly
- A query appears in top 20 frequently

## Alternative: Single Query Approach

If Locker supports subqueries or CTEs in a single visualization, you could create one master query, though this is usually less maintainable.

## Verification Checklist

Before publishing the dashboard, verify:
- ✅ All 4 queries execute successfully in BigQuery
- ✅ Data refresh works as expected
- ✅ Chart types are appropriate for each data set
- ✅ Filters work correctly across all visualizations
- ✅ Dashboard is responsive on mobile devices
- ✅ Permissions are set correctly for your team

## Expected Results

After setup, you should see:

1. **Overview**: Quick metric of search quality (e.g., 68% good, 32% not good)
2. **Trend**: Day-by-day improvement or degradation in search quality
3. **Reasons**: Which specific issues are most common (margin problems, coverage issues, etc.)
4. **Queries**: Which exact search queries are causing problems most frequently

This enables data-driven decisions on search improvements and sparse vector implementation prioritization.
