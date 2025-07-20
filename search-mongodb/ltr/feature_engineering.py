import os
import json
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from db import get_mongodb_connection
from query_tracking.service import load_previous_searches_mongodb


class FeatureEngineer:
    """Feature engineering for Learning-to-Rank model"""
    
    def __init__(self):
        self.feature_names = [
            'mongodb_score',
            'title_match',  # 2=full match, 1=partial, 0=none
            'log_price',
            'recency_days',
            'bestseller_rating',
            'is_free',
            'is_bundle',
            'user_cat_pref',
            'user_grade_pref'
        ]
    
    def extract_features(self, raw_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract features for a query-document-user triple
        Args:
            raw_data: Dict with keys: query, document, mongodb_score, user_cat_pref, user_grade_pref
        Returns:
            Dictionary of feature values
        """
        query = raw_data.get('query', '').strip().lower()
        document = raw_data.get('document', {})
        mongodb_score = raw_data.get('mongodb_score', 0.0)
        user_cat_pref = raw_data.get('user_cat_pref', 0)
        user_grade_pref = raw_data.get('user_grade_pref', 0)

        features = {}
        # MongoDB score
        features['mongodb_score'] = float(mongodb_score) if mongodb_score else 0.0
        # Title match: 2=full, 1=partial, 0=none
        title = document.get('title', '').strip().lower()
        if query == title:
            features['title_match'] = 2
        elif query in title or title in query or any(qw in title for qw in query.split()):
            features['title_match'] = 1
        else:
            features['title_match'] = 0
        # Log price
        price = document.get('price', 0.0)
        features['log_price'] = math.log(1 + price) if price > 0 else 0.0
        # Recency in days
        created_at = document.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except Exception:
                    created_at = None
            elif not isinstance(created_at, datetime):
                created_at = None
            if created_at:
                now = datetime.utcnow()
                recency_days = (now - created_at).days
                features['recency_days'] = max(0, recency_days)
            else:
                features['recency_days'] = 365
        else:
            features['recency_days'] = 365
        # Bestseller rating
        features['bestseller_rating'] = float(document.get('bestseller_rating', 0.0))
        # Boolean features
        features['is_free'] = 1.0 if document.get('is_free', False) else 0.0
        features['is_bundle'] = 1.0 if document.get('is_bundle', False) else 0.0
        # User preference features
        features['user_cat_pref'] = float(user_cat_pref)
        features['user_grade_pref'] = float(user_grade_pref)
        return features

    def create_training_data(self, query_document_pairs: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Create training dataset from list of raw data dicts (with label)
        Args:
            query_document_pairs: List of dicts with keys: query, document, mongodb_score, label, user_cat_pref, user_grade_pref
        Returns:
            DataFrame with features and labels
        """
        data = []
        for raw_data in query_document_pairs:
            features = self.extract_features(raw_data)
            features['query'] = raw_data.get('query', '')
            features['user_id'] = raw_data.get('user_id', '')
            features['material_id'] = raw_data.get('document', {}).get('material_id')
            features['label'] = raw_data.get('label', 0)
            data.append(features)
        df = pd.DataFrame(data)
        return df
    
    def get_feature_matrix(self, df: pd.DataFrame) -> np.ndarray:
        """Extract feature matrix for training"""
        return df[self.feature_names].values
    
    def get_labels(self, df: pd.DataFrame) -> np.ndarray:
        """Extract labels for training"""
        return df['label'].values


def generate_synthetic_labels(raw_data: Dict[str, Any]) -> int:
    """
    Generate synthetic label for a training example based on the attached example.
    Args:
        raw_data: Dict with keys: query, user_id, document, etc.
    Returns:
        Label (int)
    """
    return raw_data.get('label', 1)  # Use the provided label in the synthetic example 