import zipfile
import json
import pandas as pd
import re
from pathlib import Path

# Resolve project root as the directory above this script (../)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# ---------- CONFIG ----------
taxonomy_dir = PROJECT_ROOT / "data" / "taxonomy"
zip_files = list(taxonomy_dir.glob("*.zip"))  # All ZIP files
cat_path = taxonomy_dir / "taxonomy_categories.csv"
freq_threshold = 100  # only include queries with frequency > X
# ----------------------------

# Load taxonomy
categories = pd.read_csv(cat_path)

def normalize(text):
    if pd.isna(text):
        return ""
    return str(text).lower().strip()

category_tokens = set(categories['title'].map(normalize).dropna().tolist())

# Comprehensive Grade Level Patterns (High + Medium Priority)
# Based on analysis of all ZIP files with frequency > 1,000
grade_level_patterns = [
    # High Priority - Single grades (klasse 1-12)
    'klasse 1', 'klasse 2', 'klasse 3', 'klasse 4', 'klasse 5', 
    'klasse 6', 'klasse 7', 'klasse 8', 'klasse 9', 'klasse 10',
    'klasse 11', 'klasse 12',
    
    # High Priority - Special levels
    'vorschule', 'kita',
    
    # Medium Priority - Abbreviations with dot and space (kl. X)
    'kl. 1', 'kl. 2', 'kl. 3', 'kl. 4', 'kl. 5', 'kl. 6', 
    'kl. 7', 'kl. 8', 'kl. 9', 'kl. 10', 'kl. 11', 'kl. 12',
    
    # Medium Priority - Abbreviations with space (kl X)
    'kl 1', 'kl 2', 'kl 3', 'kl 4', 'kl 5', 'kl 6', 
    'kl 7', 'kl 8', 'kl 9', 'kl 10', 'kl 11', 'kl 12',
    
    # Medium Priority - Abbreviations with dot no space (kl.X)
    'kl.1', 'kl.2', 'kl.3', 'kl.4', 'kl.5', 'kl.6', 
    'kl.7', 'kl.8', 'kl.9', 'kl.10', 'kl.11', 'kl.12',
    
    # Medium Priority - No spaces (klasseX)
    'klasse1', 'klasse2', 'klasse3', 'klasse4', 'klasse5',
    'klasse6', 'klasse7', 'klasse8', 'klasse9',
    
    # Medium Priority - Common ranges
    'klasse 1-2', 'klasse 1-3', 'klasse 1-4', 'klasse 1-6',
    'klasse 2-3', 'klasse 2-4', 'klasse 3-4', 'klasse 3-6',
    'klasse 4-5', 'klasse 5-6', 'klasse 5-7', 'klasse 7-10',
    'klasse 1 - 4',  # with spaces around dash
    
    # Medium Priority - Extra spaces
    'klasse  1', 'klasse  2', 'klasse  4',
    
    # Medium Priority - Abbreviations no space (klX)
    'kl1', 'kl2', 'kl3', 'kl4', 'kl5', 'kl6', 'kl7', 'kl8', 'kl9'
]

# Convert to set for faster lookup
grade_level_set = set(grade_level_patterns)

print("="*80)
print("CONFIGURATION")
print("="*80)
print(f"Grade level patterns loaded: {len(grade_level_set)}")
print(f"Category tokens loaded: {len(category_tokens)}")
print(f"Frequency threshold: {freq_threshold}")
print("="*80 + "\n")

# Initialize counters
query_counts = {"No-intent": 0, "Category intent": 0, "Grade level intent": 0, "Combination": 0}
query_examples = {"No-intent": {}, "Category intent": {}, "Grade level intent": {}, "Combination": {}}
total = 0

# Function to classify
def classify_query(query: str, freq: int):
    global total
    q = normalize(query)
    tokens = set(q.split())
    
    # Check for category intent (token-based)
    has_cat = any(t in category_tokens for t in tokens)
    
    # Check for grade level intent (substring-based for better pattern matching)
    # This catches patterns like "klasse 1-2" that don't work with token matching
    has_grade = any(pattern in q for pattern in grade_level_set)

    category = None
    if not has_cat and not has_grade:
        category = "No-intent"
    elif has_cat and not has_grade:
        category = "Category intent"
    elif has_grade and not has_cat:
        category = "Grade level intent"
    elif has_cat and has_grade:
        category = "Combination"
    
    if category:
        query_counts[category] += freq
        query_examples[category][query] = query_examples[category].get(query, 0) + freq
    total += freq

# Stream parse JSON inside all ZIP files
print(f"Processing {len(zip_files)} ZIP files...")
for zip_path in zip_files:
    print(f"  - {zip_path.name}")
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
                    except:
                        continue

print(f"\nTotal queries analyzed: {total:,}\n")

# Compute percentages
percentages = {k: round(v / total * 100, 2) for k, v in query_counts.items() if total > 0}

# Get top 10 queries for each category
def get_top_queries(category: str, n: int = 10):
    queries = query_examples[category]
    sorted_queries = sorted(queries.items(), key=lambda x: x[1], reverse=True)[:n]
    return [q[0] for q in sorted_queries]

# Convert to DataFrame for nicer output
results = pd.DataFrame([
    {
        "Query Type": k, 
        "Percentage": percentages.get(k, 0), 
        "Total Frequency": query_counts[k],
        "Examples": get_top_queries(k)
    }
    for k in query_counts
])

# Display settings for better output
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', None)

print(results)
print("\n" + "="*80 + "\n")
print("TOP 10 QUERIES BY TYPE:")
print("="*80 + "\n")

for _, row in results.iterrows():
    print(f"{row['Query Type']}:")
    print(f"  Percentage: {row['Percentage']}%")
    print(f"  Total Frequency: {row['Total Frequency']:,}")
    print(f"  Examples:")
    for i, query in enumerate(row['Examples'], 1):
        print(f"    {i}. {query}")
    print()