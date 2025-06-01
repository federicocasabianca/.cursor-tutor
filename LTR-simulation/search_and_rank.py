import argparse
import pandas as pd
import numpy as np
import sys
import os

from config import config
from ltr_model import EdukiLTRModel
from feature_engineering import EdukiFeatureEngineer


def load_user(users_df, user_id):
    user_row = users_df[users_df['user_id'] == user_id]
    if user_row.empty:
        raise ValueError(f"User ID {user_id} not found.")
    return user_row.iloc[0]

def search_materials(materials_df, keyword):
    keyword = keyword.lower()
    mask = (
        materials_df['title'].str.lower().str.contains(keyword) |
        materials_df['subject'].str.lower().str.contains(keyword) |
        materials_df['subcategory'].str.lower().str.contains(keyword)
    )
    return materials_df[mask]

def main():
    parser = argparse.ArgumentParser(description="Search and rank Eduki materials for a user using LTR model.")
    parser.add_argument('--user', type=str, required=True, help='User ID')
    parser.add_argument('--keyword', type=str, required=True, help='Search keyword')
    parser.add_argument('--topk', type=int, default=10, help='Number of top results to show')
    args = parser.parse_args()

    # Load data
    users_df = pd.read_csv(config.raw_users_file)
    materials_df = pd.read_csv(config.raw_materials_file)

    # Find user
    try:
        user = load_user(users_df, args.user)
    except ValueError as e:
        print(e)
        sys.exit(1)

    # Search materials
    candidates = search_materials(materials_df, args.keyword)
    if candidates.empty:
        print(f"No materials found for keyword '{args.keyword}'.")
        sys.exit(0)

    # Simulate interactions for feature engineering
    interactions = []
    for _, mat in candidates.iterrows():
        interactions.append({
            'user_id': user['user_id'],
            'material_id': mat['material_id'],
            'event_type': 'viewMaterial',  # Simulate a view event
            'relevance_score': 0,  # Placeholder, not used for prediction
            'timestamp': pd.Timestamp.now(),
            'date': pd.Timestamp.now().date(),
            'device': 'desktop',
            'session_id': 'search_session',
            'position_in_results': 1
        })
    interactions_df = pd.DataFrame(interactions)

    # Feature engineering
    feature_engineer = EdukiFeatureEngineer()
    feature_engineer.load_preprocessors()
    features_df = feature_engineer.create_features(users_df, materials_df, interactions_df)
    features_df = feature_engineer.scale_features(features_df, fit_scaler=False)

    # Load LTR model
    ltr_model = EdukiLTRModel()
    ltr_model.load_model()

    # Predict relevance
    X, _, _ = ltr_model.prepare_data(features_df)
    preds = ltr_model.predict_relevance(X)
    candidates = candidates.copy()
    candidates['predicted_relevance'] = preds
    candidates = candidates.sort_values('predicted_relevance', ascending=False).head(args.topk)

    # Print results
    print(f"Top {args.topk} results for user {user['user_id']} and keyword '{args.keyword}':\n")
    for idx, row in candidates.iterrows():
        print(f"{row['material_id']}: {row['title']} (Subject: {row['subject']}, Score: {row['predicted_relevance']:.3f})")

if __name__ == "__main__":
    main() 