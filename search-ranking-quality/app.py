from flask import Flask, render_template, jsonify, request
import json
import numpy as np
from datetime import datetime
import os
import glob
import csv

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
    """Analyze how well the query matches the material title"""
    if not query or not title or query == 'No query found':
        return {'type': 'no_match', 'score': 0, 'matched_tokens': []}
    
    # Clean and tokenize query and title
    import re
    query_clean = re.sub(r'[^\w\s]', ' ', query.lower()).strip()
    title_clean = re.sub(r'[^\w\s]', ' ', title.lower()).strip()
    
    if not query_clean or not title_clean:
        return {'type': 'no_match', 'score': 0, 'matched_tokens': []}
    
    query_tokens = [token for token in query_clean.split() if len(token) > 2]  # Ignore short words
    
    if not query_tokens:
        return {'type': 'no_match', 'score': 0, 'matched_tokens': []}
    
    # Check for full match (entire query appears in title)
    if query_clean in title_clean:
        return {'type': 'full_match', 'score': 100, 'matched_tokens': query_tokens}
    
    # Check for partial match (any tokens appear in title)
    matched_tokens = []
    for token in query_tokens:
        if token in title_clean:
            matched_tokens.append(token)
    
    if matched_tokens:
        match_percentage = (len(matched_tokens) / len(query_tokens)) * 100
        return {'type': 'partial_match', 'score': match_percentage, 'matched_tokens': matched_tokens}
    
    return {'type': 'no_match', 'score': 0, 'matched_tokens': []}

def analyze_query_category_match(query, material_categories, taxonomy):
    """Analyze how well the query matches the material categories based on taxonomy"""
    if not query or not material_categories or not taxonomy or query == 'No query found':
        return {'type': 'no_match', 'score': 0, 'matched_categories': [], 'query_category': None}
    
    # Clean and tokenize query
    import re
    query_clean = re.sub(r'[^\w\s]', ' ', query.lower()).strip()
    query_tokens = [token for token in query_clean.split() if len(token) > 2]
    
    if not query_tokens:
        return {'type': 'no_match', 'score': 0, 'matched_categories': [], 'query_category': None}
    
    # Find which taxonomy category the query might be referring to
    query_category = None
    query_category_info = None
    best_match_score = 0
    
    for cat_id, cat_data in taxonomy.items():
        match_score = 0
        
        for token in query_tokens:
            # Exact title match gets highest priority
            if cat_data['title'] == token:
                match_score += 100
            # Token is the entire title (reverse check)
            elif token == cat_data['title']:
                match_score += 100
            # Token appears at the beginning of title
            elif cat_data['title'].startswith(token):
                match_score += 80
            # Title appears at the beginning of token (for compound words)
            elif token.startswith(cat_data['title']) and len(cat_data['title']) > 3:
                match_score += 70
            # Token appears in title (but not at start)
            elif token in cat_data['title'] and len(token) > 3:
                match_score += 50
            # Token appears in path
            elif cat_data['path'] and token in cat_data['path'] and len(token) > 3:
                match_score += 30
        
        # Update best match if this one is better
        if match_score > best_match_score:
            best_match_score = match_score
            query_category = cat_id
            query_category_info = cat_data
    
    # If no category found in taxonomy for the query, it's not a category query
    if not query_category:
        return {'type': 'no_match', 'score': 0, 'matched_categories': [], 'query_category': None}
    
    # Extract material category titles and check against the query category
    material_category_titles = []
    matched_categories = []
    
    for cat in material_categories:
        cat_title = cat.get('full_title', '').lower()
        if cat_title and cat_title != 'meta':
            material_category_titles.append(cat_title)
            
            # Check if this material category matches the query category
            query_title = query_category_info['title']
            query_path = query_category_info['path']
            query_full_title = query_category_info['full_title']
            
            # More flexible matching - check for root words and similar terms
            def get_root_word(word):
                # Simple stemming for German words
                word = word.lower()
                if word.endswith('en'):
                    return word[:-2]  # religionen -> religion
                elif word.endswith('e'):
                    return word[:-1]  # schule -> schul
                return word
            
            query_root = get_root_word(query_title)
            cat_root = get_root_word(cat_title)
            
            # Extract the last part of the category path (the actual category title)
            cat_parts = cat_title.split(' → ')
            cat_actual_title = cat_parts[-1] if cat_parts else cat_title
            
            # Check if the query category title matches the actual category title
            # This prevents matching "Herbst" with "Sommer" just because they share the same path
            title_matches = (
                query_title == cat_actual_title or
                query_root == get_root_word(cat_actual_title) or
                query_full_title.lower() == cat_actual_title or
                (len(query_title) > 3 and query_title in cat_actual_title) or
                (len(cat_actual_title) > 3 and cat_actual_title in query_title)
            )
            
            # Also check for broader category matches (like "Religion" matching full hierarchy)
            broader_matches = (
                query_title in cat_title or 
                cat_title in query_title or
                query_full_title.lower() in cat_title or
                cat_title in query_full_title.lower()
            )
            
            if title_matches or broader_matches:
                matched_categories.append(cat_title)
    
    # Determine match type
    if not matched_categories:
        return {
            'type': 'no_match', 
            'score': 0, 
            'matched_categories': [], 
            'query_category': query_category_info['full_title'],
            'material_categories': material_category_titles
        }
    
    # Check if the query category is the ONLY category present (Full Match)
    if len(material_category_titles) == len(matched_categories):
        return {
            'type': 'full_match', 
            'score': 100, 
            'matched_categories': matched_categories,
            'query_category': query_category_info['full_title'],
            'material_categories': material_category_titles
        }
    
    # Partial match - query category present but with other categories
    match_percentage = (len(matched_categories) / len(material_category_titles)) * 100 if material_category_titles else 0
    return {
        'type': 'partial_match', 
        'score': match_percentage,
        'matched_categories': matched_categories,
        'query_category': query_category_info['full_title'],
        'material_categories': material_category_titles
    }

def calculate_metrics(materials, top_k=18, original_query=''):
    """Calculate ranking quality metrics for top-K results"""
    if not materials or len(materials) == 0:
        return {}
    
    # Take top-K results
    top_k_materials = materials[:top_k]
    
    # Load taxonomy data for category matching
    taxonomy = load_taxonomy_data()
    
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
    
    # Analyze query-category matching
    category_matches = []
    category_match_summary = {'full_match': 0, 'partial_match': 0, 'no_match': 0}
    
    for material in top_k_materials:
        categories = material.get('material_categories', [])
        match_result = analyze_query_category_match(original_query, categories, taxonomy)
        category_matches.append(match_result)
        category_match_summary[match_result['type']] += 1
    
    # Extract query information
    query_info = {
        'original_query': original_query or 'No query found',
        'world_info': world_info,
        'title_matches': title_matches,
        'title_match_summary': title_match_summary,
        'category_matches': category_matches,
        'category_match_summary': category_match_summary
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
        # Extract material categories
        categories = material.get('material_categories', [])
        category_titles = [cat.get('full_title', '') for cat in categories if cat.get('full_title') != 'Meta']
        
        # Extract grade titles
        grades = material.get('material_class_grades', [])
        grade_titles = [grade.get('title', '') for grade in grades]
        
        # Extract seller segments
        seller_segments = material.get('seller_segments', [])
        
        # Always analyze title matching
        title = material.get('title', '')
        title_match_result = analyze_query_title_match(original_query, title)
        
        # Analyze category matching only if the intent type has category
        category_match_result = None
        if intent_type.get('has_category', False):
            category_match_result = analyze_query_category_match(original_query, categories, taxonomy)
        
        # TODO: Add grade-level matching for grade-level intent types
        grade_match_result = None
        if intent_type.get('has_grade', False):
            # Placeholder for future grade-level matching implementation
            grade_match_result = {'type': 'no_match', 'score': 0, 'matched_grades': []}
        
        row = {
            'rank': i + 1,
            'id': material.get('id', ''),
            'title': title,
            'title_match': title_match_result,
            'category_match': category_match_result,
            'grade_match': grade_match_result,
            'material_categories': ', '.join(category_titles),
            'material_class_grades': ', '.join(grade_titles),
            'price': material.get('price', 0),
            'bestseller_rating': round(material.get('bestseller_rating', 0), 4),
            'engagement_score': f"{material.get('engagement_score', 0):.2e}",
            'is_bundle': 'Yes' if material.get('is_bundle', False) else 'No',
            'created_at': material.get('created_at', ''),
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
    metrics = calculate_metrics(materials, top_k=18, original_query=original_query)
    
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
    metrics = calculate_metrics(materials, top_k=18, original_query=original_query)
    
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
