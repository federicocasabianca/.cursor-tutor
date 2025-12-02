import zipfile
import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

# Resolve project root as the directory above this script (../)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# ---------- CONFIG ----------
taxonomy_dir = PROJECT_ROOT / "data" / "taxonomy"
zip_files = list(taxonomy_dir.glob("*.zip"))  # All ZIP files
cat_path = taxonomy_dir / "taxonomy_categories.csv"
grade_path = taxonomy_dir / "taxonomy_grade_levels.csv"
material_path = taxonomy_dir / "taxonomy_material_type.csv"
freq_threshold = 100  # only include queries with frequency > X
top_n = 20  # Get top 20 queries per bucket
output_file = PROJECT_ROOT / "data" / "golden_queries.json"
# ----------------------------

def normalize(text):
    """Normalize text to lowercase and strip whitespace"""
    if pd.isna(text):
        return ""
    return str(text).lower().strip()

# Load taxonomy files
print("="*80)
print("LOADING TAXONOMY FILES")
print("="*80)

# Load categories
categories_df = pd.read_csv(cat_path)
category_tokens = set(categories_df['title'].map(normalize).dropna().tolist())
print(f"✓ Loaded {len(category_tokens)} category terms from taxonomy_categories.csv")

# Load grade levels
grade_levels_df = pd.read_csv(grade_path)
grade_level_tokens = set(grade_levels_df['title'].map(normalize).dropna().tolist())
# Also add common grade level patterns
grade_level_patterns = [
    # Single grades
    'klasse 1', 'klasse 2', 'klasse 3', 'klasse 4', 'klasse 5', 
    'klasse 6', 'klasse 7', 'klasse 8', 'klasse 9', 'klasse 10',
    'klasse 11', 'klasse 12',
    # Special levels
    'vorschule', 'kita',
    # Abbreviations with dot and space
    'kl. 1', 'kl. 2', 'kl. 3', 'kl. 4', 'kl. 5', 'kl. 6', 
    'kl. 7', 'kl. 8', 'kl. 9', 'kl. 10', 'kl. 11', 'kl. 12',
    # Abbreviations with space
    'kl 1', 'kl 2', 'kl 3', 'kl 4', 'kl 5', 'kl 6', 
    'kl 7', 'kl 8', 'kl 9', 'kl 10', 'kl 11', 'kl 12',
    # Abbreviations with dot no space
    'kl.1', 'kl.2', 'kl.3', 'kl.4', 'kl.5', 'kl.6', 
    'kl.7', 'kl.8', 'kl.9', 'kl.10', 'kl.11', 'kl.12',
    # No spaces
    'klasse1', 'klasse2', 'klasse3', 'klasse4', 'klasse5',
    'klasse6', 'klasse7', 'klasse8', 'klasse9',
    # Common ranges
    'klasse 1-2', 'klasse 1-3', 'klasse 1-4', 'klasse 1-6',
    'klasse 2-3', 'klasse 2-4', 'klasse 3-4', 'klasse 3-6',
    'klasse 4-5', 'klasse 5-6', 'klasse 5-7', 'klasse 7-10',
    'klasse 1 - 4',
    # Abbreviations no space
    'kl1', 'kl2', 'kl3', 'kl4', 'kl5', 'kl6', 'kl7', 'kl8', 'kl9'
]
grade_level_set = set(grade_level_patterns) | grade_level_tokens
print(f"✓ Loaded {len(grade_level_set)} grade level terms/patterns from taxonomy_grade_levels.csv")

# Load material types
material_types_df = pd.read_csv(material_path)
material_type_tokens = set(material_types_df['title'].map(normalize).dropna().tolist())
print(f"✓ Loaded {len(material_type_tokens)} material type terms from taxonomy_material_type.csv")

# Create a set of all taxonomy terms
all_taxonomy_terms = category_tokens | material_type_tokens
print(f"✓ Total unique taxonomy tokens: {len(all_taxonomy_terms)}")
print("="*80 + "\n")

# Initialize storage for queries
query_buckets = {
    "no-intent": defaultdict(int),
    "category": defaultdict(int),
    "grade_level": defaultdict(int),
    "material_type": defaultdict(int),
    "combination": defaultdict(int)
}

def has_category_intent(query_normalized, tokens):
    """Check if query has category intent"""
    return any(t in category_tokens for t in tokens)

def has_grade_level_intent(query_normalized):
    """Check if query has grade level intent (substring-based)"""
    return any(pattern in query_normalized for pattern in grade_level_set)

def has_material_type_intent(query_normalized, tokens):
    """Check if query has material type intent"""
    return any(t in material_type_tokens for t in tokens)

def has_non_taxonomy_terms(tokens, query_normalized):
    """Check if query has terms not in taxonomy"""
    # Check token-based
    has_non_taxonomy_token = any(t not in all_taxonomy_terms for t in tokens if len(t) > 2)
    # Also check if it doesn't fully match grade level patterns
    has_non_grade_pattern = not any(query_normalized == pattern for pattern in grade_level_set)
    return has_non_taxonomy_token and has_non_grade_pattern

def classify_query(query: str, freq: int):
    """Classify query into one of the 5 buckets"""
    q = normalize(query)
    tokens = [t for t in q.split() if len(t) > 0]
    
    # Check for each type of intent
    has_cat = has_category_intent(q, tokens)
    has_grade = has_grade_level_intent(q)
    has_material = has_material_type_intent(q, tokens)
    has_non_taxonomy = has_non_taxonomy_terms(tokens, q)
    
    # Count how many taxonomy intents
    intent_count = sum([has_cat, has_grade, has_material])
    
    # Classification logic
    if intent_count == 0:
        # No taxonomy terms at all
        bucket = "no-intent"
    elif intent_count == 1 and not has_non_taxonomy:
        # Only one type of intent and no other terms
        if has_cat:
            bucket = "category"
        elif has_grade:
            bucket = "grade_level"
        else:
            bucket = "material_type"
    else:
        # Multiple taxonomy types OR has taxonomy + non-taxonomy terms
        bucket = "combination"
    
    query_buckets[bucket][query] += freq

# Process all ZIP files
print(f"PROCESSING {len(zip_files)} ZIP FILES")
print("="*80)
total_queries_processed = 0

for zip_path in zip_files:
    print(f"  - {zip_path.name}...")
    with zipfile.ZipFile(zip_path, 'r') as z:
        for file in z.namelist():
            if not file.endswith(".json"):
                continue
            with z.open(file) as f:
                for line in f:
                    try:
                        line = line.decode("utf-8", errors='ignore').strip().rstrip(",")
                    except:
                        continue
                    if not line or not line.startswith("{"):
                        continue
                    try:
                        obj = json.loads(line)
                        query = obj.get("query", "")
                        freq = int(obj.get("frequency", 0))
                        if freq > freq_threshold:
                            classify_query(query, freq)
                            total_queries_processed += 1
                    except:
                        continue

print(f"\n✓ Total queries processed: {total_queries_processed:,}")
print("="*80 + "\n")

# Get top N queries for each bucket
golden_queries = {}
print(f"EXTRACTING TOP {top_n} QUERIES PER BUCKET")
print("="*80)

for bucket_name, queries_dict in query_buckets.items():
    # Sort by frequency and get top N
    sorted_queries = sorted(queries_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    # Store as list of dicts with query and frequency
    golden_queries[bucket_name] = [
        {"query": q, "frequency": f} 
        for q, f in sorted_queries
    ]
    
    total_freq = sum(queries_dict.values())
    unique_queries = len(queries_dict)
    
    print(f"\n{bucket_name.upper()}:")
    print(f"  Total frequency: {total_freq:,}")
    print(f"  Unique queries: {unique_queries:,}")
    print(f"  Top {min(top_n, len(sorted_queries))} queries:")
    for i, (query, freq) in enumerate(sorted_queries[:10], 1):  # Show top 10 in console
        print(f"    {i:2d}. {query:50s} (freq: {freq:,})")
    if len(sorted_queries) > 10:
        print(f"    ... and {len(sorted_queries) - 10} more")

# Save to JSON file
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(golden_queries, f, ensure_ascii=False, indent=2)

print("\n" + "="*80)
print(f"✓ Golden queries saved to: {output_file}")
print("="*80)

# Also create a CSV version for easier viewing
csv_rows = []
for bucket_name, queries in golden_queries.items():
    for item in queries:
        csv_rows.append({
            "bucket": bucket_name,
            "query": item["query"],
            "frequency": item["frequency"]
        })

csv_df = pd.DataFrame(csv_rows)
csv_path = output_file.with_suffix('.csv')
csv_df.to_csv(csv_path, index=False, encoding='utf-8')
print(f"✓ Golden queries also saved to: {csv_path}")

