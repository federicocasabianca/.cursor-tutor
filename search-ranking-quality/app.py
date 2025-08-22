from flask import Flask, render_template, jsonify, request
import json
import numpy as np
from datetime import datetime
import os

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

def load_materials_data():
    """Load materials data from JSON file"""
    try:
        with open('test-queries/combined/no-intent_category/mini-paket_herbst.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading mini-paket_herbst.json: {e}")
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

def calculate_metrics(materials, top_k=18, original_query=''):
    """Calculate ranking quality metrics for top-K results"""
    if not materials or len(materials) == 0:
        return {}
    
    # Take top-K results
    top_k_materials = materials[:top_k]
    
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
    match_summary = {'full_match': 0, 'partial_match': 0, 'no_match': 0}
    
    for material in top_k_materials:
        title = material.get('title', '')
        match_result = analyze_query_title_match(original_query, title)
        title_matches.append(match_result)
        match_summary[match_result['type']] += 1
    
    # Extract query information
    query_info = {
        'original_query': original_query or 'No query found',
        'world_info': world_info,
        'title_matches': title_matches,
        'match_summary': match_summary
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

def prepare_table_data(materials, top_k=18, original_query=''):
    """Prepare data for the results table"""
    if not materials:
        return []
    
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
        
        # Analyze title matching
        title = material.get('title', '')
        match_result = analyze_query_title_match(original_query, title)
        
        row = {
            'rank': i + 1,
            'id': material.get('id', ''),
            'title': title,
            'title_match': match_result,
            'material_categories': ', '.join(category_titles),
            'material_class_grades': ', '.join(grade_titles),
            'price': material.get('price', 0),
            'bestseller_rating': round(material.get('bestseller_rating', 0), 4),
            'engagement_score': f"{material.get('engagement_score', 0):.2e}",
            'is_bundle': 'Yes' if material.get('is_bundle', False) else 'No',
            'created_at': material.get('created_at', ''),
            'seller_segments': ', '.join(seller_segments) if seller_segments else 'None'
        }
        table_data.append(row)
    
    return table_data

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """API endpoint to get materials data and metrics"""
    data = load_materials_data()
    if not data:
        return jsonify({'error': 'Failed to load materials data'}), 500
    
    materials = data.get('items', {}).get('materials', [])
    
    # Extract query information
    auto_suggest = data.get('auto_suggest', {})
    original_query = auto_suggest.get('original_query', 'No query found')
    
    # Calculate metrics
    metrics = calculate_metrics(materials, top_k=18, original_query=original_query)
    
    # Prepare table data
    table_data = prepare_table_data(materials, top_k=18, original_query=original_query)
    
    return jsonify({
        'metrics': metrics,
        'table_data': table_data,
        'success': True
    })

@app.route('/api/reload')
def reload_data():
    """API endpoint to reload data"""
    data = load_materials_data()
    if not data:
        return jsonify({'error': 'Failed to reload materials data'}), 500
    
    materials = data.get('items', {}).get('materials', [])
    
    # Extract query information
    auto_suggest = data.get('auto_suggest', {})
    original_query = auto_suggest.get('original_query', 'No query found')
    
    # Calculate metrics
    metrics = calculate_metrics(materials, top_k=18, original_query=original_query)
    
    # Prepare table data
    table_data = prepare_table_data(materials, top_k=18, original_query=original_query)
    
    return jsonify({
        'metrics': metrics,
        'table_data': table_data,
        'success': True,
        'reloaded_at': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
