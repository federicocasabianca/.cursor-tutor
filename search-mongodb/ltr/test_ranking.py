#!/usr/bin/env python3
"""
Test script for the Learning-to-Rank system
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .ranking_service import get_ranking_service
from search.service import search_materials


def test_ranking_service():
    """Test the ranking service with a sample query"""
    print("Testing Learning-to-Rank system...")
    
    # Test query
    test_query = "mathematik klasse 3"
    
    print(f"Search query: '{test_query}'")
    
    # Get search results from MongoDB
    print("\n1. Getting MongoDB search results...")
    search_results = search_materials(test_query, page=1, limit=10)
    
    if not search_results.get('results'):
        print("No search results found!")
        return
    
    print(f"Found {len(search_results['results'])} results")
    
    # Show original ranking
    print("\n2. Original MongoDB ranking:")
    for i, doc in enumerate(search_results['results'][:5]):
        print(f"  {i+1}. {doc.get('title', 'No title')} (Score: {doc.get('score', 0)})")
    
    # Check if LTR model is available
    ranking_service = get_ranking_service()
    ranking_info = ranking_service.get_ranking_info()
    
    print(f"\n3. LTR Model Status:")
    print(f"  Model loaded: {ranking_info['model_loaded']}")
    print(f"  Model path: {ranking_info['model_path']}")
    print(f"  Features: {ranking_info['features']}")
    
    if ranking_info['model_loaded']:
        print("\n4. Re-ranked results:")
        # The re-ranking is already applied in search_materials
        # Just show the final results
        for i, doc in enumerate(search_results['results'][:5]):
            original_score = doc.get('mongodb_score', doc.get('score', 0))
            new_score = doc.get('score', 0)
            print(f"  {i+1}. {doc.get('title', 'No title')}")
            print(f"      MongoDB Score: {original_score:.2f} -> LTR Score: {new_score:.2f}")
    else:
        print("\n4. No LTR model available - using MongoDB scores only")
    
    # Show ranking info if available
    if 'ranking_info' in search_results:
        print(f"\n5. Ranking Information:")
        for key, value in search_results['ranking_info'].items():
            print(f"  {key}: {value}")


def test_feature_extraction():
    """Test feature extraction with sample data"""
    print("\n" + "="*50)
    print("Testing Feature Extraction")
    print("="*50)
    
    from ltr.feature_engineering import FeatureEngineer
    
    feature_engineer = FeatureEngineer()
    
    # Sample document
    sample_doc = {
        'material_id': 12345,
        'title': 'Mathematik Arbeitsblätter Klasse 3',
        'price': 5.99,
        'created_at': '2024-01-15T10:30:00Z',
        'bestseller_rating': 4.5,
        'is_free': False,
        'is_bundle': True
    }
    
    # Extract features
    features = feature_engineer.extract_features("mathematik klasse 3", sample_doc, 8.5)
    
    print("Sample document features:")
    for feature_name, value in features.items():
        print(f"  {feature_name}: {value}")


def main():
    """Main test function"""
    print("="*60)
    print("LEARNING-TO-RANK SYSTEM TEST")
    print("="*60)
    
    try:
        # Test feature extraction
        test_feature_extraction()
        
        # Test ranking service
        test_ranking_service()
        
        print("\n" + "="*60)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("="*60)
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 