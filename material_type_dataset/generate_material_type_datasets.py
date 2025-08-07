"""
Generate training datasets for Material-Type intent
--------------------------------------------------
This script scans every seasonal ZIP archive and writes **five** CSV files:
  1. material_only.csv                  – queries w/ Material-Type only
  2. material_plus_category.csv          – Material-Type + Category (no Grade)
  3. material_plus_grade.csv             – Material-Type + Grade (no Category)
  4. material_plus_category_grade.csv    – Material-Type + Category + Grade
  5. material_other_combos.csv           – Material-Type plus any other mix
Each output row:  query,frequency,intents_json
Dependencies: pandas, zipfile, pathlib, regex (pip install regex)
Place script in /mnt/data and run:  python generate_material_type_datasets.py
"""
from pathlib import Path
import zipfile, json, csv
import regex as re
import pandas as pd

# --------------------------------- helper: load taxonomy tables
RESOURCE_DIR = Path('./taxonomy')
TAXO_FILES = {
    'category':  'taxonomy_categories.csv',
    'grade':     'taxonomy_grade_levels.csv',
    'material':  'taxonomy_material_type.csv',
    'schooltypes': 'taxonomy_school_types.csv'
}

def load_taxonomy(kind):
    df = pd.read_csv(RESOURCE_DIR / TAXO_FILES[kind])
    return {str(x).lower(): row['node_id'] for x, row in df.set_index('node_name').iterrows()}

category_lu  = load_taxonomy('category')
grade_lu     = load_taxonomy('grade')
material_lu  = load_taxonomy('material')

# quick tokeniser
TOK_RE = re.compile(r"[\p{L}\p{N}]+", re.UNICODE)

def tokens(text):
    return [t.lower() for t in TOK_RE.findall(text)]

# --------------------------------- gather queries
ZIP_FILES = sorted(RESOURCE_DIR.glob('*Query*.zip'))

def extract_queries():
    for zf in ZIP_FILES:
        with zipfile.ZipFile(zf) as z:
            for name in z.namelist():
                if name.endswith('.csv'):
                    df = pd.read_csv(z.open(name))
                    for _, row in df.iterrows():
                        yield row['query'], int(row.get('frequency', 1))

# --------------------------------- classify intents per query

def classify(q):
    tk = tokens(q)
    intents = set()
    # material
    if any(t in material_lu for t in tk):
        intents.add('material')
    # category (subject/season/language/skill/curriculum)
    if any(t in category_lu for t in tk):
        intents.add('category')
    # grade level (simple pattern 0-13 or Klasse/Kl.)
    for t in tk:
        if t in grade_lu or re.match(r'^[1-9][0-3]?\.?\s*(klasse|kl)$', t):
            intents.add('grade')
            break
    return intents

# --------------------------------- output csv writers
FILES = {
    'material_only':                   None,
    'material_plus_category':          None,
    'material_plus_grade':             None,
    'material_plus_category_grade':    None,
    'material_other_combos':           None,
}

writers = {}
for tag in FILES:
    fh = open(RESOURCE_DIR / f'{tag}.csv', 'w', newline='', encoding='utf-8')
    writers[tag] = csv.writer(fh)
    writers[tag].writerow(['query', 'frequency', 'intents'])
    FILES[tag] = fh

# --------------------------------- main loop
for q, freq in extract_queries():
    intents = classify(q)
    if 'material' not in intents:
        continue  # skip – no material-type token
    intents_json = json.dumps(sorted(intents))
    key = None
    if intents == {'material'}:
        key = 'material_only'
    elif intents == {'material', 'category'}:
        key = 'material_plus_category'
    elif intents == {'material', 'grade'}:
        key = 'material_plus_grade'
    elif intents == {'material', 'category', 'grade'}:
        key = 'material_plus_category_grade'
    else:
        key = 'material_other_combos'
    writers[key].writerow([q, freq, intents_json])

# close files
for fh in FILES.values():
    fh.close()

print("Done – files written to /mnt/data")