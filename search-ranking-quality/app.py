from flask import Flask, render_template, jsonify, request
import json
import numpy as np
from datetime import datetime
import os

app = Flask(__name__)

def load_materials_data():
    """Load materials data from JSON file"""
    try:
        with open('materials.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading materials.json: {e}")
        return None

def calculate_metrics(materials, top_k=18):
    """Calculate ranking quality metrics for top-K results"""
    if not materials or len(materials) == 0:
        return {}
    
    # Take top-K results
    top_k_materials = materials[:top_k]
    
    # Extract query information
    query_info = {
        'original_query': 'No query found',
        'modified_query': 'No query found'
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

def prepare_table_data(materials, top_k=18):
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
        
        row = {
            'rank': i + 1,
            'world': material.get('world', ''),
            'id': material.get('id', ''),
            'title': material.get('title', ''),
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
    query_info = {
        'original_query': auto_suggest.get('original_query', 'No query found'),
        'modified_query': auto_suggest.get('modified_query', 'No query found')
    }
    
    # Calculate metrics
    metrics = calculate_metrics(materials)
    metrics['query_info'] = query_info
    
    # Prepare table data
    table_data = prepare_table_data(materials)
    
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
    query_info = {
        'original_query': auto_suggest.get('original_query', 'No query found'),
        'modified_query': auto_suggest.get('modified_query', 'No query found')
    }
    
    # Calculate metrics
    metrics = calculate_metrics(materials)
    metrics['query_info'] = query_info
    
    # Prepare table data
    table_data = prepare_table_data(materials)
    
    return jsonify({
        'metrics': metrics,
        'table_data': table_data,
        'success': True,
        'reloaded_at': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
