# Golden Query Set

## Overview

This golden query set contains the top 20 most frequent real user queries from the taxonomy ZIP files, organized by intent type. This dataset can be used to assess the quality and performance of search/ranking algorithm changes.

## Generation Script

**Script**: `extract_golden_queries.py`

The script processes all ZIP files in the `taxonomy/` directory and classifies queries into 5 intent buckets based on the taxonomy files.

### How to Run

```bash
cd /Users/federico.casabianca/.cursor-tutor/material_type_dataset
source venv/bin/activate
python extract_golden_queries.py
```

## Intent Classification Logic

### 1. **No-Intent**
Queries that contain **no terms** from any taxonomy (categories, grade levels, or material types).

**Examples:**
- `kostenlos` (free)
- `adventskalender` (advent calendar)
- `märchen` (fairy tales)

### 2. **Category Intent**
Queries that contain **only category terms** (from `taxonomy_categories.csv`), with no grade level or material type terms.

**Examples:**
- `weihnachten` (Christmas)
- `kunst` (art)
- `halloween`

**Note:** Queries like `tragansparenz algebra` belong here because `algebra` is a category term, even though `tragansparenz` is not in the taxonomy.

### 3. **Grade Level Intent**
Queries that contain **only grade level terms** (from `taxonomy_grade_levels.csv` or common patterns like "klasse 1-4"), with no category or material type terms.

**Examples:**
- `vorschule` (preschool)
- `klasse 1` (class 1)
- `1. klasse`

**Note:** Queries like `wimpelkette klasse 7` belong here if `wimpelkette` is not in any taxonomy.

### 4. **Material Type Intent**
Queries that contain **only material type terms** (from `taxonomy_material_type.csv`), with no category or grade level terms.

**Examples:**
- `bildkarten` (flashcards)
- `spiele` (games)
- `poster`

### 5. **Combination**
Queries that have:
- Multiple taxonomy intents (e.g., category + grade level), OR
- At least one taxonomy intent + non-taxonomy terms

**Examples:**
- `kunst klasse 1` (art + class 1) - category + grade level
- `verliebte zahlen` (has category term + non-taxonomy word)
- `buchstabeneinführung kostenlos algebra klasse 8` - category + grade level + non-taxonomy words

## Output Files

### 1. `golden_queries.json`
JSON file with structured data for each intent bucket:
```json
{
  "no-intent": [
    {"query": "kostenlos", "frequency": 1308041},
    ...
  ],
  "category": [...],
  "grade_level": [...],
  "material_type": [...],
  "combination": [...]
}
```

### 2. `golden_queries.csv`
CSV file with columns: `bucket`, `query`, `frequency`

Easy to open in Excel/Google Sheets for analysis.

## Statistics (from last run)

| Intent Bucket    | Total Frequency | Unique Queries | Top Query                | Top Frequency |
|-----------------|-----------------|----------------|--------------------------|---------------|
| No-Intent       | 155,033,180     | 160,879        | kostenlos                | 1,308,041     |
| Category        | 30,002,158      | 5,551          | weihnachten              | 2,096,627     |
| Grade Level     | 453,105         | 59             | vorschule                | 225,599       |
| Material Type   | 180,766         | 102            | bildkarten               | 55,354        |
| Combination     | 72,826,814      | 97,732         | verliebte zahlen         | 401,008       |

**Total queries processed:** 330,413 (with frequency > 100)

## Usage for Testing

1. **Baseline Assessment**: Run your current search/ranking algorithm against these queries and record the results
2. **Change Testing**: After making algorithm changes, run the same queries again
3. **Compare Results**: Analyze differences in:
   - Result relevance
   - Result order
   - Result count
   - Performance metrics

## Configuration

The script has several configurable parameters at the top:

- `freq_threshold = 100`: Minimum query frequency to include (filters out rare queries)
- `top_n = 20`: Number of top queries to extract per bucket
- Taxonomy file paths
- Output file paths

## Taxonomy Sources

- **Categories**: `taxonomy/taxonomy_categories.csv` (1,344 terms)
- **Grade Levels**: `taxonomy/taxonomy_grade_levels.csv` (102 patterns including "klasse 1-12", "vorschule", "kita", etc.)
- **Material Types**: `taxonomy/taxonomy_material_type.csv` (26 terms)

## Notes

- The script uses both token-based and substring-based matching to handle various query formats
- Grade level patterns include abbreviations (kl., kl) and ranges (klasse 1-4)
- Queries are normalized to lowercase for consistent matching
- The frequency threshold ensures we focus on commonly-used queries that represent real user behavior

