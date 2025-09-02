from flask import Flask, render_template, jsonify, request
import json
import numpy as np
from datetime import datetime
import os
import glob
import csv
from api_client import EdukiSearchAPI

app = Flask(__name__)

def get_world_flag(world):
    """Get flag emoji for world/country code"""
    flag_mapping = {
        'us': '🇺🇸',
        'uk': '🇬🇧',
        'ca': '🇨🇦',
        'au': '🇦🇺',
        'de': '🇩🇪',
        'fr': '🇫🇷',
        'es': '🇪🇸',
        'it': '🇮🇹',
        'br': '🇧🇷',
        'mx': '🇲🇽',
        'in': '🇮🇳',
        'jp': '🇯🇵',
        'kr': '🇰🇷',
        'cn': '🇨🇳',
        'nl': '🇳🇱',
        'se': '🇸🇪',
        'no': '🇳🇴',
        'dk': '🇩🇰',
        'fi': '🇫🇮',
        'pt': '🇵🇹',
        'pl': '🇵🇱',
        'ru': '🇷🇺',
        'tr': '🇹🇷',
        'za': '🇿🇦',
        'ar': '🇦🇷',
        'cl': '🇨🇱',
        'co': '🇨🇴',
        'pe': '🇵🇪',
        'nz': '🇳🇿'
    }
    return flag_mapping.get(world.lower(), '🌍')

def detect_query_intent_type(query_path):
    """Detect the intent type from the query path"""
    if not query_path:
        return {'type': 'unknown', 'has_category': False, 'has_grade': False}
    
    # Normalize path
    path_lower = query_path.lower()
    
    # Determine intent type based on folder structure
    if 'no-intent' in path_lower and 'category' in path_lower and 'grade-level' in path_lower:
        return {'type': 'no-intent_category_grade-level', 'has_category': True, 'has_grade': True}
    elif 'category' in path_lower and 'grade-level' in path_lower:
        return {'type': 'category_grade-level', 'has_category': True, 'has_grade': True}
    elif 'no-intent' in path_lower and 'category' in path_lower:
        return {'type': 'no-intent_category', 'has_category': True, 'has_grade': False}
    elif 'no-intent' in path_lower and 'grade-level' in path_lower:
        return {'type': 'no-intent_grade-level', 'has_category': False, 'has_grade': True}
    elif 'category' in path_lower:
        return {'type': 'category', 'has_category': True, 'has_grade': False}
    elif 'grade-level' in path_lower:
        return {'type': 'grade-level', 'has_category': False, 'has_grade': True}
    elif 'no-intent' in path_lower:
        return {'type': 'no-intent', 'has_category': False, 'has_grade': False}
    else:
        return {'type': 'unknown', 'has_category': False, 'has_grade': False}

def load_taxonomy_data():
    """Load taxonomy data from CSV file"""
    taxonomy = {}
    try:
        with open('taxonomy/categories.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                category_id = row['id']
                title = row['title'].lower() if row['title'] else ''
                path = row['path'].lower() if row['path'] else ''
                
                taxonomy[category_id] = {
                    'title': title,
                    'path': path,
                    'full_title': row['title'],
                    'full_path': row['path']
                }
        return taxonomy
    except Exception as e:
        print(f"Error loading taxonomy data: {e}")
        return {}

def load_grade_taxonomy_data():
    """Load grade level taxonomy data from CSV file"""
    grade_taxonomy = {}
    try:
        with open('taxonomy/grade_levels.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                grade_id = row['id']
                title = row['title'].lower() if row['title'] else ''
                short_title = row['short_title'].lower() if row['short_title'] else ''
                
                grade_taxonomy[grade_id] = {
                    'title': title,
                    'short_title': short_title,
                    'full_title': row['title'],
                    'full_short_title': row['short_title'],
                    'position': int(row['position']) if row['position'] else 0
                }
        return grade_taxonomy
    except Exception as e:
        print(f"Error loading grade taxonomy data: {e}")
        return {}

def scan_query_structure():
    """Scan the test-queries folder structure and return available queries"""
    base_path = 'test-queries'
    structure = {}
    
    if not os.path.exists(base_path):
        return structure
    
    # Define the expected folder structure
    folders = [
        'no-intent',
        'category', 
        'grade-level',
        'combined/no-intent_category',
        'combined/no-intent_grade-level',
        'combined/category_grade-level',
        'combined/no-intent_category_grade-level'
    ]
    
    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        if os.path.exists(folder_path):
            # Find all JSON files in this folder
            json_files = glob.glob(os.path.join(folder_path, '*.json'))
            queries = []
            
            for json_file in json_files:
                filename = os.path.basename(json_file)
                query_name = filename.replace('.json', '')
                queries.append({
                    'name': query_name,
                    'path': json_file,
                    'filename': filename
                })
            
            # Clean folder name for display
            display_name = folder.replace('combined/', '').replace('_', ' + ').title()
            if folder.startswith('combined/'):
                display_name = f"Combined: {display_name}"
            
            structure[folder] = {
                'display_name': display_name,
                'path': folder_path,
                'queries': queries,
                'enabled': len(queries) > 0
            }
    
    return structure

def load_materials_data(query_path=None):
    """Load materials data from JSON file"""
    if query_path is None:
        return None  # No default file, require explicit selection
    
    try:
        with open(query_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading {query_path}: {e}")
        return None

def analyze_query_title_match(query, title):
    """Analyze how well the query matches the material title based on token presence (order independent)"""
    if not query or not title or query == 'No query found':
        return {'type': 'no_match', 'score': 0, 'matched_tokens': []}
    
    # Clean and tokenize query and title
    import re
    query_clean = re.sub(r'[^\w\s]', ' ', query.lower()).strip()
    title_clean = re.sub(r'[^\w\s]', ' ', title.lower()).strip()
    
    if not query_clean or not title_clean:
        return {'type': 'no_match', 'score': 0, 'matched_tokens': []}
    
    # Tokenize query - keep ALL tokens (including short ones like "4")
    query_tokens = [token for token in query_clean.split() if len(token) > 0]
    title_tokens = [token for token in title_clean.split() if len(token) > 0]
    
    if not query_tokens:
        return {'type': 'no_match', 'score': 0, 'matched_tokens': []}
    
    # Check which query tokens are present in the title (order independent)
    matched_tokens = []
    for query_token in query_tokens:
        token_found = False
        for title_token in title_tokens:
            # Direct match or flexible matching (e.g., "4" in "4.", "klasse" in "klasse")
            if query_token == title_token or query_token in title_token or title_token in query_token:
                token_found = True
                break
            # Handle synonyms: Klasse <-> Schulstufe
            elif (query_token == 'klasse' and 'schulstufe' in title_token) or \
                 (query_token == 'schulstufe' and 'klasse' in title_token):
                token_found = True
                break
        
        if token_found:
            matched_tokens.append(query_token)
    
    # Calculate match percentage
    if not matched_tokens:
        return {'type': 'no_match', 'score': 0, 'matched_tokens': []}
    
    match_percentage = (len(matched_tokens) / len(query_tokens)) * 100
    
    # Determine match type based on percentage
    if match_percentage == 100:
        return {'type': 'full_match', 'score': match_percentage, 'matched_tokens': matched_tokens}
    else:
        return {'type': 'partial_match', 'score': match_percentage, 'matched_tokens': matched_tokens}

def analyze_query_grade_match(query, material_grades, grade_taxonomy):
    """Analyze how well the query matches the material grades based on grade taxonomy"""
    if not query or not material_grades or not grade_taxonomy or query == 'No query found':
        return {'type': 'no_match', 'score': 0, 'matched_grades': [], 'query_grade': None}
    
    # Clean and tokenize query
    import re
    query_clean = re.sub(r'[^\w\s]', ' ', query.lower()).strip()
    query_tokens = [token for token in query_clean.split() if len(token) > 0]
    
    if not query_tokens:
        return {'type': 'no_match', 'score': 0, 'matched_grades': [], 'query_grade': None}
    
    # Find which grade levels the query might be referring to
    query_grades = []
    best_matches = []
    
    # Extract numeric patterns and grade patterns from query
    grade_patterns = []
    
    # Pattern matching for various grade formats
    for token in query_tokens:
        # Direct number matches (1, 2, 3, etc.)
        if re.match(r'^\d+$', token):
            grade_patterns.append(token)
        
        # Klasse patterns (klasse, kl, etc.)
        if 'klasse' in token or token.startswith('kl'):
            # Extract numbers from patterns like "kl8", "klasse8", etc.
            numbers = re.findall(r'\d+', token)
            grade_patterns.extend(numbers)
    
    # Handle space-separated patterns like "kl 8", "klasse 5" 
    for i, token in enumerate(query_tokens):
        if token in ['kl', 'klasse'] and i + 1 < len(query_tokens):
            next_token = query_tokens[i + 1]
            # Check if next token is a number or contains numbers
            numbers = re.findall(r'\d+', next_token)
            grade_patterns.extend(numbers)
    
    # Look for grade ranges (e.g., "6-8", "6,7,8")
    query_text = ' '.join(query_tokens)
    range_patterns = re.findall(r'(\d+)[-,\s]*(?:und\s*)?(\d+)', query_text)
    for start, end in range_patterns:
        start_num, end_num = int(start), int(end)
        for i in range(start_num, end_num + 1):
            grade_patterns.append(str(i))
    
    # Look for multiple grades listed (e.g., "6, 7, 8")
    multi_patterns = re.findall(r'\d+', query_text)
    grade_patterns.extend(multi_patterns)
    
    # Remove duplicates
    grade_patterns = list(set(grade_patterns))
    
    # Find matching grades in taxonomy
    for grade_id, grade_data in grade_taxonomy.items():
        match_score = 0
        
        # Check if any of the extracted patterns match this grade
        grade_title = grade_data['title']
        grade_short = grade_data['short_title']
        
        for pattern in grade_patterns:
            # Direct match with short title (e.g., "8" matches "8")
            if pattern == grade_short:
                match_score += 100
            # Match within title (e.g., "8" matches "8. Klasse")
            elif pattern in grade_title:
                match_score += 90
            # Match for compound titles
            elif grade_short in pattern:
                match_score += 80
        
        # Also check for direct word matches in query
        for token in query_tokens:
            # Exact title match
            if grade_title == token:
                match_score += 100
            # Token appears in grade title
            elif token in grade_title and len(token) > 2:
                match_score += 70
            # Special patterns for German school system
            elif 'ef' in token and 'ef' in grade_title:
                match_score += 95
            elif 'q1' in token and 'q1' in grade_title:
                match_score += 95
            elif 'q2' in token and 'q2' in grade_title:
                match_score += 95
            elif 'vorschule' in token and 'vorschule' in grade_title:
                match_score += 95
            elif 'erwachsenen' in token and 'erwachsenen' in grade_title:
                match_score += 90
            elif 'lehrer' in token and 'lehrer' in grade_title:
                match_score += 90
        
        # If we found a good match, add it to query grades
        if match_score > 0:
            best_matches.append({
                'grade_id': grade_id,
                'grade_data': grade_data,
                'score': match_score
            })
    
    # Sort by score and take the best matches
    best_matches.sort(key=lambda x: x['score'], reverse=True)
    
    # If no grades found in taxonomy for the query, it's not a grade query
    if not best_matches:
        return {'type': 'no_match', 'score': 0, 'matched_grades': [], 'query_grade': None}
    
    # Take the highest scoring grades as the query grades
    # Only take grades with the highest score to avoid false positives
    if best_matches:
        max_score = best_matches[0]['score']
        # Only take grades with the maximum score (or within 10 points of it)
        query_grades = [match['grade_data'] for match in best_matches if match['score'] >= max(70, max_score - 10)]
    else:
        query_grades = []
    
    if not query_grades:
        return {'type': 'no_match', 'score': 0, 'matched_grades': [], 'query_grade': None}
    
    # Extract material grade titles and check against the query grades
    material_grade_titles = []
    matched_grades = []
    
    for grade in material_grades:
        grade_title = grade.get('title', '').lower()
        if grade_title:
            material_grade_titles.append(grade_title)
            
            # Check if this material grade matches any of the query grades
            for query_grade in query_grades:
                query_grade_title = query_grade['title']
                query_grade_short = query_grade['short_title']
                query_grade_full = query_grade['full_title']
                
                # More flexible matching for grades
                grade_matches = (
                    query_grade_title == grade_title or
                    query_grade_short == grade_title or
                    query_grade_full.lower() == grade_title or
                    (len(query_grade_short) > 0 and query_grade_short in grade_title) or
                    (len(grade_title) > 2 and grade_title in query_grade_title)
                )
                
                if grade_matches:
                    matched_grades.append(grade_title)
                    break
    
    # Determine match type
    if not matched_grades:
        return {
            'type': 'no_match', 
            'score': 0, 
            'matched_grades': [], 
            'query_grade': ', '.join([g['full_title'] for g in query_grades]),
            'material_grades': material_grade_titles
        }
    
    # Check if ALL material grades match the query grades (Full Match)
    # This means every material grade matches at least one query grade
    all_material_grades_match = len(matched_grades) == len(material_grade_titles)
    
    if all_material_grades_match:
        return {
            'type': 'full_match', 
            'score': 100, 
            'matched_grades': matched_grades,
            'query_grade': ', '.join([g['full_title'] for g in query_grades]),
            'material_grades': material_grade_titles
        }
    
    # Partial match - query grades present but with other grades
    match_percentage = (len(matched_grades) / len(material_grade_titles)) * 100 if material_grade_titles else 0
    return {
        'type': 'partial_match', 
        'score': match_percentage,
        'matched_grades': matched_grades,
        'query_grade': ', '.join([g['full_title'] for g in query_grades]),
        'material_grades': material_grade_titles
    }

def analyze_query_category_match(query, material_categories, taxonomy):
    """Analyze how well the query matches the material categories based on token presence (order independent)"""
    if not query or not material_categories or not taxonomy or query == 'No query found':
        return {'type': 'no_match', 'score': 0, 'matched_categories': [], 'query_category': None}
    
    # Clean and tokenize query
    import re
    query_clean = re.sub(r'[^\w\s]', ' ', query.lower()).strip()
    query_tokens = [token for token in query_clean.split() if len(token) > 2]  # Filter short words for categories
    
    if not query_tokens:
        return {'type': 'no_match', 'score': 0, 'matched_categories': [], 'query_category': None}
    
    # Find ALL potential category tokens in the query by checking each token against taxonomy
    category_tokens_found = []
    
    for token in query_tokens:
        for cat_id, cat_data in taxonomy.items():
            # Check if this token matches any part of the taxonomy
            if (cat_data['title'] == token or 
                token in cat_data['title'] or 
                (cat_data['path'] and token in cat_data['path'].lower())):
                category_tokens_found.append({
                    'token': token,
                    'category_data': cat_data
                })
                break  # Found a match for this token, move to next token
    
    # If no category tokens found in query, it's not a category query
    if not category_tokens_found:
        return {'type': 'no_match', 'score': 0, 'matched_categories': [], 'query_category': None}
    
    # Extract material category titles and check which ones contain our category tokens
    material_category_titles = []
    matched_categories = []
    
    for cat in material_categories:
        cat_title = cat.get('full_title', '').lower()
        if cat_title and cat_title != 'meta':
            material_category_titles.append(cat_title)
            
            # Check if this material category contains any of our query category tokens
            category_matched = False
            
            for category_token_info in category_tokens_found:
                token = category_token_info['token']
                cat_data = category_token_info['category_data']
                
                # Check multiple matching strategies
                token_matches = (
                    # Direct token match in category title
                    token in cat_title or
                    # Token matches category hierarchy parts
                    any(token in part.strip().lower() for part in cat_title.split(' → ')) or
                    # Fuzzy matching for German words
                    any(token.startswith(part.strip().lower()[:4]) and len(part.strip()) > 3 
                        for part in cat_title.split(' → ')) or
                    any(part.strip().lower().startswith(token[:4]) and len(token) > 3 
                        for part in cat_title.split(' → '))
                )
                
                if token_matches:
                    category_matched = True
                    break
            
            if category_matched:
                matched_categories.append(cat_title)
    
    # Determine match type
    if not matched_categories:
        # Create a summary of found category tokens for reporting
        found_tokens = [info['token'] for info in category_tokens_found]
        return {
            'type': 'no_match', 
            'score': 0, 
            'matched_categories': [], 
            'query_category': ', '.join(found_tokens),
            'material_categories': material_category_titles
        }
    
    # Calculate match percentage based on how many material categories matched
    match_percentage = (len(matched_categories) / len(material_category_titles)) * 100 if material_category_titles else 0
    
    # Determine match type based on percentage
    if match_percentage == 100:
        match_type = 'full_match'
    else:
        match_type = 'partial_match'
    
    # Create summary of found category tokens for reporting
    found_tokens = [info['token'] for info in category_tokens_found]
    
    return {
        'type': match_type, 
        'score': match_percentage,
        'matched_categories': matched_categories,
        'query_category': ', '.join(found_tokens),
        'material_categories': material_category_titles
    }

def calculate_metrics(materials, top_k=18, original_query='', intent_type=None):
    """Calculate ranking quality metrics for top-K results"""
    if not materials or len(materials) == 0:
        return {}
    
    # Take top-K results
    top_k_materials = materials[:top_k]
    
    # Load taxonomy data for category and grade matching
    taxonomy = load_taxonomy_data()
    grade_taxonomy = load_grade_taxonomy_data()
    
    # Default intent type if not provided
    if intent_type is None:
        intent_type = {'type': 'unknown', 'has_category': False, 'has_grade': False}
    
    # Extract world information for flag
    world_info = {}
    if top_k_materials:
        first_material_world = top_k_materials[0].get('world', '')
        world_info = {
            'world': first_material_world,
            'flag': get_world_flag(first_material_world)
        }
    
    # Analyze query-title matching
    title_matches = []
    title_match_summary = {'full_match': 0, 'partial_match': 0, 'no_match': 0}
    
    for material in top_k_materials:
        title = material.get('title', '')
        match_result = analyze_query_title_match(original_query, title)
        title_matches.append(match_result)
        title_match_summary[match_result['type']] += 1
    
    # Analyze query-category matching (only if intent has category)
    category_matches = []
    category_match_summary = {'full_match': 0, 'partial_match': 0, 'no_match': 0}
    
    if intent_type.get('has_category', False):
        for material in top_k_materials:
            categories = material.get('material_categories', [])
            match_result = analyze_query_category_match(original_query, categories, taxonomy)
            category_matches.append(match_result)
            category_match_summary[match_result['type']] += 1
    
    # Analyze query-grade matching (only if intent has grade)
    grade_matches = []
    grade_match_summary = {'full_match': 0, 'partial_match': 0, 'no_match': 0}
    
    if intent_type.get('has_grade', False):
        for material in top_k_materials:
            grades = material.get('material_class_grades', [])
            match_result = analyze_query_grade_match(original_query, grades, grade_taxonomy)
            grade_matches.append(match_result)
            grade_match_summary[match_result['type']] += 1
    
    # Extract query information
    query_info = {
        'original_query': original_query or 'No query found',
        'world_info': world_info,
        'title_matches': title_matches,
        'title_match_summary': title_match_summary,
        'category_matches': category_matches,
        'category_match_summary': category_match_summary,
        'grade_matches': grade_matches,
        'grade_match_summary': grade_match_summary
    }
    
    # Price mix metrics
    prices = [m.get('price', 0) for m in top_k_materials]
    avg_price = np.mean(prices) if prices else 0
    median_price = np.median(prices) if prices else 0
    free_count = sum(1 for p in prices if p == 0)
    free_share = free_count / top_k if top_k > 0 else 0
    
    # Performance proxy mix
    bestseller_ratings = [m.get('bestseller_rating', 0) for m in top_k_materials]
    bestseller_ratings_log = [np.log(r + 1) if r > 0 else 0 for r in bestseller_ratings]
    mean_bestseller_log = np.mean(bestseller_ratings_log) if bestseller_ratings_log else 0
    
    # Calculate Gini coefficient for bestseller ratings
    def gini_coefficient(values):
        if not values or len(values) == 1:
            return 0
        sorted_values = np.sort(values)
        n = len(values)
        cumsum = np.cumsum(sorted_values)
        return (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n if cumsum[-1] != 0 else 0
    
    # Calculate HHI (Herfindahl-Hirschman Index)
    def hhi(values):
        if not values:
            return 0
        total = sum(values)
        if total == 0:
            return 0
        return sum((v / total) ** 2 for v in values)
    
    gini_bestseller = gini_coefficient(bestseller_ratings)
    hhi_bestseller = hhi(bestseller_ratings)
    
    # Content & diversity hygiene
    bundles_count = sum(1 for m in top_k_materials if m.get('is_bundle', False))
    bundles_share = bundles_count / top_k if top_k > 0 else 0
    
    # Seller segments diversity
    seller_segments = []
    for m in top_k_materials:
        segments = m.get('seller_segments', [])
        if segments:
            seller_segments.extend(segments)
    
    unique_seller_segments = len(set(seller_segments)) if seller_segments else 0
    hhi_seller_segments = hhi([seller_segments.count(s) for s in set(seller_segments)]) if seller_segments else 0
    
    # Category and grade breadth
    top_categories = set()
    grade_titles = set()
    
    for m in top_k_materials:
        # Extract top categories
        categories = m.get('material_categories', [])
        for cat in categories:
            top_cat_title = cat.get('top_category_title')
            if top_cat_title and top_cat_title != 'Meta':
                top_categories.add(top_cat_title)
        
        # Extract grade titles
        grades = m.get('material_class_grades', [])
        for grade in grades:
            grade_title = grade.get('title')
            if grade_title:
                grade_titles.add(grade_title)
    
    category_breadth = len(top_categories)
    grade_breadth = len(grade_titles)
    
    return {
        'query_info': query_info,
        'price_mix': {
            'average_price': round(avg_price, 2),
            'median_price': round(median_price, 2),
            'free_share': round(free_share * 100, 1),
            'free_count': free_count
        },
        'performance_proxy': {
            'mean_bestseller_log': round(mean_bestseller_log, 4),
            'gini_bestseller': round(gini_bestseller, 4),
            'hhi_bestseller': round(hhi_bestseller, 4)
        },
        'content_diversity': {
            'bundles_share': round(bundles_share * 100, 1),
            'bundles_count': bundles_count,
            'seller_segments_diversity': unique_seller_segments,
            'seller_segments_hhi': round(hhi_seller_segments, 4),
            'category_breadth': category_breadth,
            'grade_breadth': grade_breadth
        },
        'top_k': top_k,
        'total_results': len(materials)
    }

def prepare_table_data(materials, top_k=18, original_query='', intent_type=None):
    """Prepare data for the results table with intent-aware matching"""
    if not materials:
        return []
    
    # Default intent type if not provided
    if intent_type is None:
        intent_type = {'type': 'unknown', 'has_category': False, 'has_grade': False}
    
    # Load taxonomy data for category matching (only if needed)
    taxonomy = load_taxonomy_data() if intent_type.get('has_category', False) else {}
    
    table_data = []
    for i, material in enumerate(materials[:top_k]):
        # Extract material categories (with defensive coding)
        categories = material.get('material_categories', [])
        category_titles = []
        if categories and isinstance(categories, list):
            for cat in categories:
                if isinstance(cat, dict) and cat.get('full_title') and cat.get('full_title') != 'Meta':
                    category_titles.append(cat.get('full_title', ''))
        
        # Extract grade titles (with defensive coding)
        grades = material.get('material_class_grades', [])
        grade_titles = []
        if grades and isinstance(grades, list):
            for grade in grades:
                if isinstance(grade, dict) and grade.get('title'):
                    grade_titles.append(grade.get('title', ''))
        
        # Extract seller segments (with defensive coding)
        seller_segments = material.get('seller_segments', [])
        if not isinstance(seller_segments, list):
            seller_segments = []
        
        # Always analyze title matching
        title = material.get('title', '')
        title_match_result = analyze_query_title_match(original_query, title)
        
        # Analyze category matching only if the intent type has category
        category_match_result = None
        if intent_type.get('has_category', False):
            category_match_result = analyze_query_category_match(original_query, categories, taxonomy)
        
        # Analyze grade matching only if the intent type has grade
        grade_match_result = None
        if intent_type.get('has_grade', False):
            grades = material.get('material_class_grades', [])
            grade_taxonomy = load_grade_taxonomy_data()
            grade_match_result = analyze_query_grade_match(original_query, grades, grade_taxonomy)
        
        # Safe handling of fields that might be missing or in unexpected format
        try:
            price = float(material.get('price', 0)) if material.get('price') is not None else 0
        except (ValueError, TypeError):
            price = 0
            
        try:
            bestseller_rating = round(float(material.get('bestseller_rating', 0)), 4) if material.get('bestseller_rating') is not None else 0
        except (ValueError, TypeError):
            bestseller_rating = 0
            
        try:
            engagement_score = float(material.get('engagement_score', 0)) if material.get('engagement_score') is not None else 0
            engagement_score_str = f"{engagement_score:.2e}"
        except (ValueError, TypeError):
            engagement_score_str = "0.00e+00"

        row = {
            'rank': i + 1,
            'id': str(material.get('id', '')),
            'title': str(title),
            'title_match': title_match_result,
            'category_match': category_match_result,
            'grade_match': grade_match_result,
            'material_categories': ', '.join(category_titles),
            'material_class_grades': ', '.join(grade_titles),
            'price': price,
            'bestseller_rating': bestseller_rating,
            'engagement_score': engagement_score_str,
            'is_bundle': 'Yes' if material.get('is_bundle', False) else 'No',
            'created_at': str(material.get('created_at', '')),
            'seller_segments': ', '.join(seller_segments) if seller_segments else 'None',
            'intent_type': intent_type
        }
        table_data.append(row)
    
    return table_data

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/query-structure')
def get_query_structure():
    """API endpoint to get the query folder structure"""
    try:
        structure = scan_query_structure()
        return jsonify({
            'structure': structure,
            'success': True
        })
    except Exception as e:
        return jsonify({'error': f'Failed to scan query structure: {e}'}), 500

@app.route('/api/data')
def get_data():
    """API endpoint to get materials data and metrics"""
    query_path = request.args.get('query_path')
    
    if not query_path:
        return jsonify({'error': 'No query selected'}), 400
    
    data = load_materials_data(query_path)
    if not data:
        return jsonify({'error': 'Failed to load query data'}), 500
    
    materials = data.get('items', {}).get('materials', [])
    
    # Extract query information
    auto_suggest = data.get('auto_suggest', {})
    original_query = auto_suggest.get('original_query', 'No query found')
    
    # Detect intent type from query path
    intent_type = detect_query_intent_type(query_path)
    
    # Calculate metrics
    metrics = calculate_metrics(materials, top_k=18, original_query=original_query, intent_type=intent_type)
    
    # Prepare table data with intent-aware matching
    table_data = prepare_table_data(materials, top_k=18, original_query=original_query, intent_type=intent_type)
    
    return jsonify({
        'metrics': metrics,
        'table_data': table_data,
        'query_path': query_path,
        'intent_type': intent_type,
        'success': True
    })

@app.route('/api/reload')
def reload_data():
    """API endpoint to reload data"""
    query_path = request.args.get('query_path')
    
    if not query_path:
        return jsonify({'error': 'No query selected'}), 400
    
    data = load_materials_data(query_path)
    if not data:
        return jsonify({'error': 'Failed to reload query data'}), 500
    
    materials = data.get('items', {}).get('materials', [])
    
    # Extract query information
    auto_suggest = data.get('auto_suggest', {})
    original_query = auto_suggest.get('original_query', 'No query found')
    
    # Detect intent type from query path
    intent_type = detect_query_intent_type(query_path)
    
    # Calculate metrics
    metrics = calculate_metrics(materials, top_k=18, original_query=original_query, intent_type=intent_type)
    
    # Prepare table data with intent-aware matching
    table_data = prepare_table_data(materials, top_k=18, original_query=original_query, intent_type=intent_type)
    
    return jsonify({
        'metrics': metrics,
        'table_data': table_data,
        'query_path': query_path,
        'intent_type': intent_type,
        'success': True,
        'reloaded_at': datetime.now().isoformat()
    })

@app.route('/api/search', methods=['POST'])
def live_search():
    """API endpoint for live search using the Eduki API"""
    try:
        # Get the search query from request
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Initialize API client
        try:
            api_client = EdukiSearchAPI()
        except FileNotFoundError as e:
            return jsonify({
                'error': 'API configuration error',
                'details': 'Bearer token file not found. Please ensure bearer_token.txt exists.',
                'technical_error': str(e)
            }), 500
        except Exception as e:
            return jsonify({
                'error': 'API initialization failed',
                'details': 'Failed to initialize API client.',
                'technical_error': str(e)
            }), 500
        
        # Make the search request
        try:
            search_results = api_client.search_materials(query, limit=12)
        except Exception as e:
            return jsonify({
                'error': 'Search request failed',
                'details': 'Unable to fetch search results from the API.',
                'technical_error': str(e)
            }), 500
        
        # Extract materials and original query
        materials = search_results.get('items', {}).get('materials', [])
        auto_suggest = search_results.get('auto_suggest', {})
        
        # Use the query parameter directly since auto_suggest might be empty with test_segment=30 and intent=1
        original_query = query
        if auto_suggest and isinstance(auto_suggest, dict) and auto_suggest.get('original_query'):
            original_query = auto_suggest.get('original_query')
        
        # For live search, we assume no specific intent type (just basic query analysis)
        intent_type = {'type': 'live_search', 'has_category': False, 'has_grade': False}
        
        # Prepare table data (top 12 for compare)
        table_data = prepare_table_data(materials, top_k=12, original_query=original_query, intent_type=intent_type)
        
        return jsonify({
            'success': True,
            'query': original_query,
            'total_results': len(materials),
            'table_data': table_data,
            'searched_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        # Catch any unexpected errors
        return jsonify({
            'error': 'Unexpected error occurred',
            'details': 'An unexpected error occurred while processing your search.',
            'technical_error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
