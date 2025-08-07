#!/usr/bin/env python3
"""
Example usage of the Learning-to-Rank system
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .ranking_service import get_ranking_service
from .model import LTRModel
from .feature_engineering import FeatureEngineer


def example_feature_extraction():
    """Example of feature extraction"""
    print("=== Feature Extraction Example ===")
    
    feature_engineer = FeatureEngineer()
    
    # Sample query and document
    query = "mathematik klasse 3"
    document = {
        'material_id': 12345,
        'title': 'Mathematik Arbeitsblätter Klasse 3 - Addition und Subtraktion',
        'price': 7.99,
        'created_at': '2024-01-15T10:30:00Z',
        'bestseller_rating': 4.7,
        'is_free': False,
        'is_bundle': True
    }
    mongodb_score = 8.5
    
    # Extract features
    features = feature_engineer.extract_features(query, document, mongodb_score)
    
    print(f"Query: '{query}'")
    print(f"Document: {document['title']}")
    print("\nExtracted features:")
    for feature_name, value in features.items():
        print(f"  {feature_name}: {value}")
    
    return features


def example_model_prediction():
    """Example of model prediction"""
    print("\n=== Model Prediction Example ===")
    
    # Check if model exists
    model = LTRModel()
    if not model.is_trained():
        print("No trained model found. Please run the training pipeline first.")
        return
    
    # Sample documents
    documents = [
        {
            'material_id': 1,
            'title': 'Mathematik Klasse 3 Arbeitsblätter',
            'price': 5.99,
            'created_at': '2024-01-15T10:30:00Z',
            'bestseller_rating': 4.5,
            'is_free': False,
            'is_bundle': False
        },
        {
            'material_id': 2,
            'title': 'Kostenlose Mathematik Übungen',
            'price': 0.0,
            'created_at': '2024-03-20T14:15:00Z',
            'bestseller_rating': 4.8,
            'is_free': True,
            'is_bundle': False
        },
        {
            'material_id': 3,
            'title': 'Alte Mathematik Materialien',
            'price': 3.99,
            'created_at': '2020-05-10T09:00:00Z',
            'bestseller_rating': 3.2,
            'is_free': False,
            'is_bundle': False
        }
    ]
    
    mongodb_scores = [7.2, 6.8, 5.5]
    query = "mathematik klasse 3"
    
    # Get predictions
    ltr_scores = model.predict_scores(query, documents, mongodb_scores)
    
    print(f"Query: '{query}'")
    print("\nDocument rankings:")
    for i, (doc, mongo_score, ltr_score) in enumerate(zip(documents, mongodb_scores, ltr_scores)):
        print(f"  {i+1}. {doc['title']}")
        print(f"      MongoDB Score: {mongo_score:.2f}")
        print(f"      LTR Score: {ltr_score:.2f}")
        print(f"      Price: ${doc['price']:.2f}")
        print(f"      Rating: {doc['bestseller_rating']}")
        print(f"      Free: {doc['is_free']}")
        print()


def example_ranking_service():
    """Example of using the ranking service"""
    print("=== Ranking Service Example ===")
    
    ranking_service = get_ranking_service()
    ranking_info = ranking_service.get_ranking_info()
    
    print("Ranking Service Status:")
    print(f"  Model loaded: {ranking_info['model_loaded']}")
    print(f"  Model path: {ranking_info['model_path']}")
    print(f"  Features: {ranking_info['features']}")
    
    if not ranking_info['model_loaded']:
        print("\nNo trained model available. Please run the training pipeline first.")
        return
    
    # Sample search results
    search_results = {
        'results': [
            {
                'material_id': 1,
                'title': 'Mathematik Klasse 3 Arbeitsblätter',
                'score': 7.2,
                'price': 5.99,
                'bestseller_rating': 4.5,
                'is_free': False
            },
            {
                'material_id': 2,
                'title': 'Kostenlose Mathematik Übungen',
                'score': 6.8,
                'price': 0.0,
                'bestseller_rating': 4.8,
                'is_free': True
            },
            {
                'material_id': 3,
                'title': 'Alte Mathematik Materialien',
                'score': 5.5,
                'price': 3.99,
                'bestseller_rating': 3.2,
                'is_free': False
            }
        ],
        'total': 3
    }
    
    query = "mathematik klasse 3"
    
    print(f"\nOriginal search results for '{query}':")
    for i, doc in enumerate(search_results['results']):
        print(f"  {i+1}. {doc['title']} (Score: {doc['score']:.2f})")
    
    # Re-rank results
    re_ranked_results = ranking_service.re_rank_results(
        query, 
        search_results['results'], 
        [doc['score'] for doc in search_results['results']]
    )
    
    print(f"\nRe-ranked results:")
    for i, doc in enumerate(re_ranked_results):
        original_score = doc.get('mongodb_score', doc.get('score', 0))
        new_score = doc.get('score', 0)
        print(f"  {i+1}. {doc['title']}")
        print(f"      Original: {original_score:.2f} -> LTR: {new_score:.2f}")


def main():
    """Run all examples"""
    print("LEARNING-TO-RANK SYSTEM EXAMPLES")
    print("=" * 50)
    
    try:
        # Example 1: Feature extraction
        example_feature_extraction()
        
        # Example 2: Model prediction
        example_model_prediction()
        
        # Example 3: Ranking service
        example_ranking_service()
        
        print("\n" + "=" * 50)
        print("EXAMPLES COMPLETED!")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 