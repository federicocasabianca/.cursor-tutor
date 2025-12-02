import zipfile
import json
import pandas as pd
import re
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

# Resolve project root as the directory above this script (../)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# ---------- CONFIG ----------
taxonomy_dir = PROJECT_ROOT / "data" / "taxonomy"
zip_files = list(taxonomy_dir.glob("*.zip"))
cat_path = taxonomy_dir / "taxonomy_categories.csv"
grade_path = taxonomy_dir / "taxonomy_grade_levels.csv"
material_path = taxonomy_dir / "taxonomy_material_type.csv"
freq_threshold = 100  # Only analyze queries with frequency > X
output_file = PROJECT_ROOT / "data" / "linguistic_analysis.json"
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

categories_df = pd.read_csv(cat_path)
category_tokens = set(categories_df['title'].map(normalize).dropna().tolist())
print(f"✓ Loaded {len(category_tokens)} category terms")

grade_levels_df = pd.read_csv(grade_path)
grade_level_tokens = set(grade_levels_df['title'].map(normalize).dropna().tolist())
print(f"✓ Loaded {len(grade_level_tokens)} grade level terms")

material_types_df = pd.read_csv(material_path)
material_type_tokens = set(material_types_df['title'].map(normalize).dropna().tolist())
print(f"✓ Loaded {len(material_type_tokens)} material type terms")

# Comprehensive grade level patterns
grade_level_patterns = [
    'klasse 1', 'klasse 2', 'klasse 3', 'klasse 4', 'klasse 5', 
    'klasse 6', 'klasse 7', 'klasse 8', 'klasse 9', 'klasse 10',
    'klasse 11', 'klasse 12', 'vorschule', 'kita',
    'kl. 1', 'kl. 2', 'kl. 3', 'kl. 4', 'kl. 5', 'kl. 6', 
    'kl. 7', 'kl. 8', 'kl. 9', 'kl. 10', 'kl. 11', 'kl. 12',
    'kl 1', 'kl 2', 'kl 3', 'kl 4', 'kl 5', 'kl 6', 
    'kl 7', 'kl 8', 'kl 9', 'kl 10', 'kl 11', 'kl 12',
    'kl.1', 'kl.2', 'kl.3', 'kl.4', 'kl.5', 'kl.6', 
    'kl.7', 'kl.8', 'kl.9', 'kl.10', 'kl.11', 'kl.12',
    'klasse1', 'klasse2', 'klasse3', 'klasse4', 'klasse5',
    'klasse6', 'klasse7', 'klasse8', 'klasse9',
    'klasse 1-2', 'klasse 1-3', 'klasse 1-4', 'klasse 1-6',
    'klasse 2-3', 'klasse 2-4', 'klasse 3-4', 'klasse 3-6',
    'klasse 4-5', 'klasse 5-6', 'klasse 5-7', 'klasse 7-10',
    'klasse 1 - 4', 'kl1', 'kl2', 'kl3', 'kl4', 'kl5', 'kl6', 'kl7', 'kl8', 'kl9'
]
grade_level_set = set(grade_level_patterns) | grade_level_tokens

all_taxonomy_terms = category_tokens | material_type_tokens
print(f"✓ Total unique taxonomy tokens: {len(all_taxonomy_terms)}")
print("="*80 + "\n")

# Linguistic analysis functions
def analyze_query_linguistics(query: str):
    """Analyze linguistic characteristics of a query"""
    q = normalize(query)
    tokens = q.split()
    
    analysis = {
        'query': query,
        'normalized': q,
        'word_count': len(tokens),
        'char_count': len(q),
        'char_count_no_spaces': len(q.replace(' ', '')),
        'avg_word_length': np.mean([len(t) for t in tokens]) if tokens else 0,
        
        # Syntactic complexity indicators
        'has_conjunctions': any(word in q for word in ['und', 'oder', 'aber', 'sondern', 'und', 'oder']),
        'has_prepositions': any(word in q for word in ['für', 'mit', 'von', 'zu', 'in', 'auf', 'bei', 'nach', 'über', 'unter']),
        'has_articles': any(word in q for word in ['der', 'die', 'das', 'den', 'dem', 'des', 'ein', 'eine', 'einen', 'einem', 'eines']),
        'has_adjectives': any(word in q for word in ['gut', 'schlecht', 'neu', 'alt', 'groß', 'klein', 'wichtig', 'interessant', 'schön', 'einfach', 'schwer']),
        
        # Semantic richness indicators
        'has_descriptive_words': any(word in q for word in ['bunt', 'farbig', 'interaktiv', 'spielerisch', 'kreativ', 'praktisch', 'nützlich', 'hilfreich']),
        'has_educational_terms': any(word in q for word in ['lernen', 'lehren', 'unterrichten', 'üben', 'trainieren', 'verstehen', 'erklären']),
        'has_qualifiers': any(word in q for word in ['kostenlos', 'gratis', 'free', 'einfach', 'schwer', 'leicht', 'kompliziert', 'praktisch']),
        
        # Intent classification
        'has_category_intent': any(t in category_tokens for t in tokens),
        'has_grade_intent': any(pattern in q for pattern in grade_level_set),
        'has_material_intent': any(t in material_type_tokens for t in tokens),
        'has_taxonomy_terms': any(t in all_taxonomy_terms for t in tokens),
        
        # Natural language indicators
        'is_single_word': len(tokens) == 1,
        'is_two_words': len(tokens) == 2,
        'is_phrase': len(tokens) >= 3,
        'has_spaces': ' ' in q,
        'has_hyphens': '-' in q,
        'has_numbers': bool(re.search(r'\d', q)),
        'has_special_chars': bool(re.search(r'[^\w\s\-]', q)),
        
        # Complexity scoring
        'linguistic_complexity_score': 0,
        'natural_language_score': 0
    }
    
    # Calculate linguistic complexity score (0-10)
    complexity_score = 0
    if analysis['word_count'] > 1: complexity_score += 1
    if analysis['word_count'] > 2: complexity_score += 1
    if analysis['word_count'] > 4: complexity_score += 1
    if analysis['has_conjunctions']: complexity_score += 1
    if analysis['has_prepositions']: complexity_score += 1
    if analysis['has_articles']: complexity_score += 1
    if analysis['has_adjectives']: complexity_score += 1
    if analysis['has_descriptive_words']: complexity_score += 1
    if analysis['has_educational_terms']: complexity_score += 1
    if analysis['has_qualifiers']: complexity_score += 1
    
    analysis['linguistic_complexity_score'] = min(complexity_score, 10)
    
    # Calculate natural language score (0-10)
    natural_score = 0
    if analysis['word_count'] >= 3: natural_score += 2
    if analysis['has_conjunctions']: natural_score += 2
    if analysis['has_prepositions']: natural_score += 1
    if analysis['has_articles']: natural_score += 1
    if analysis['has_adjectives']: natural_score += 1
    if analysis['has_descriptive_words']: natural_score += 1
    if analysis['has_educational_terms']: natural_score += 1
    if analysis['has_qualifiers']: natural_score += 1
    
    analysis['natural_language_score'] = min(natural_score, 10)
    
    return analysis

def classify_query_intent(query: str):
    """Classify query into intent buckets"""
    q = normalize(query)
    tokens = [t for t in q.split() if len(t) > 0]
    
    has_cat = any(t in category_tokens for t in tokens)
    has_grade = any(pattern in q for pattern in grade_level_set)
    has_material = any(t in material_type_tokens for t in tokens)
    has_non_taxonomy = any(t not in all_taxonomy_terms for t in tokens if len(t) > 2)
    
    intent_count = sum([has_cat, has_grade, has_material])
    
    if intent_count == 0:
        return "no-intent"
    elif intent_count == 1 and not has_non_taxonomy:
        if has_cat:
            return "category"
        elif has_grade:
            return "grade_level"
        else:
            return "material_type"
    else:
        return "combination"

# Initialize storage
linguistic_data = []
query_stats = defaultdict(int)
intent_stats = defaultdict(int)
complexity_distribution = defaultdict(int)
natural_language_distribution = defaultdict(int)

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
                            # Analyze linguistic patterns
                            analysis = analyze_query_linguistics(query)
                            intent = classify_query_intent(query)
                            
                            # Store analysis with frequency weighting
                            analysis['frequency'] = freq
                            analysis['intent'] = intent
                            linguistic_data.append(analysis)
                            
                            # Update statistics
                            query_stats[query] += freq
                            intent_stats[intent] += freq
                            complexity_distribution[analysis['linguistic_complexity_score']] += freq
                            natural_language_distribution[analysis['natural_language_score']] += freq
                            
                            total_queries_processed += 1
                    except:
                        continue

print(f"\n✓ Total queries processed: {total_queries_processed:,}")
print("="*80 + "\n")

# Calculate aggregate statistics
print("LINGUISTIC ANALYSIS RESULTS")
print("="*80)

# Overall statistics
total_frequency = sum(query_stats.values())
avg_word_count = np.mean([d['word_count'] for d in linguistic_data])
avg_char_count = np.mean([d['char_count'] for d in linguistic_data])
avg_complexity = np.mean([d['linguistic_complexity_score'] for d in linguistic_data])
avg_natural_language = np.mean([d['natural_language_score'] for d in linguistic_data])

print(f"Total unique queries analyzed: {len(linguistic_data):,}")
print(f"Total frequency: {total_frequency:,}")
print(f"Average word count: {avg_word_count:.2f}")
print(f"Average character count: {avg_char_count:.2f}")
print(f"Average linguistic complexity: {avg_complexity:.2f}/10")
print(f"Average natural language score: {avg_natural_language:.2f}/10")

# Intent distribution
print(f"\nINTENT DISTRIBUTION:")
for intent, freq in sorted(intent_stats.items(), key=lambda x: x[1], reverse=True):
    percentage = (freq / total_frequency) * 100
    print(f"  {intent}: {freq:,} ({percentage:.1f}%)")

# Complexity distribution
print(f"\nLINGUISTIC COMPLEXITY DISTRIBUTION:")
for score in sorted(complexity_distribution.keys()):
    freq = complexity_distribution[score]
    percentage = (freq / total_frequency) * 100
    print(f"  Score {score}: {freq:,} queries ({percentage:.1f}%)")

# Natural language distribution
print(f"\nNATURAL LANGUAGE SCORE DISTRIBUTION:")
for score in sorted(natural_language_distribution.keys()):
    freq = natural_language_distribution[score]
    percentage = (freq / total_frequency) * 100
    print(f"  Score {score}: {freq:,} queries ({percentage:.1f}%)")

# Word count distribution
word_count_dist = defaultdict(int)
for d in linguistic_data:
    word_count_dist[d['word_count']] += d['frequency']

print(f"\nWORD COUNT DISTRIBUTION:")
for count in sorted(word_count_dist.keys()):
    freq = word_count_dist[count]
    percentage = (freq / total_frequency) * 100
    print(f"  {count} words: {freq:,} queries ({percentage:.1f}%)")

# Top examples by complexity
print(f"\nTOP 10 MOST COMPLEX QUERIES:")
complex_queries = sorted(linguistic_data, key=lambda x: x['linguistic_complexity_score'], reverse=True)[:10]
for i, q in enumerate(complex_queries, 1):
    print(f"  {i:2d}. {q['query']:50s} (complexity: {q['linguistic_complexity_score']}, freq: {q['frequency']:,})")

# Top examples by natural language score
print(f"\nTOP 10 MOST NATURAL LANGUAGE QUERIES:")
natural_queries = sorted(linguistic_data, key=lambda x: x['natural_language_score'], reverse=True)[:10]
for i, q in enumerate(natural_queries, 1):
    print(f"  {i:2d}. {q['query']:50s} (natural: {q['natural_language_score']}, freq: {q['frequency']:,})")

# Single word queries (likely exact terms)
single_word_queries = [d for d in linguistic_data if d['is_single_word']]
single_word_freq = sum(d['frequency'] for d in single_word_queries)
single_word_percentage = (single_word_freq / total_frequency) * 100

print(f"\nSINGLE WORD QUERIES:")
print(f"  Count: {len(single_word_queries):,}")
print(f"  Frequency: {single_word_freq:,} ({single_word_percentage:.1f}%)")
print(f"  Top 10 single word queries:")
for i, q in enumerate(sorted(single_word_queries, key=lambda x: x['frequency'], reverse=True)[:10], 1):
    print(f"    {i:2d}. {q['query']:30s} (freq: {q['frequency']:,})")

# Multi-word queries (more natural language)
multi_word_queries = [d for d in linguistic_data if not d['is_single_word']]
multi_word_freq = sum(d['frequency'] for d in multi_word_queries)
multi_word_percentage = (multi_word_freq / total_frequency) * 100

print(f"\nMULTI-WORD QUERIES:")
print(f"  Count: {len(multi_word_queries):,}")
print(f"  Frequency: {multi_word_freq:,} ({multi_word_percentage:.1f}%)")

# Save detailed results
results = {
    'top_complex_queries': complex_queries[:20]
}

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n" + "="*80)
print(f"✓ Detailed linguistic analysis saved to: {output_file}")
print("="*80)
