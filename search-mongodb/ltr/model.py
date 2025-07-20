import os
import joblib
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from sklearn.model_selection import train_test_split
from sklearn.metrics import ndcg_score, mean_squared_error
import xgboost as xgb
from feature_engineering import FeatureEngineer


class LTRModel:
    """Learning-to-Rank model using XGBoost"""
    
    def __init__(self, model_path: str = 'models/ltr_model.pkl'):
        self.model_path = model_path
        self.feature_engineer = FeatureEngineer()
        self.model = None
        self.feature_names = self.feature_engineer.feature_names
        
    def train(self, training_data: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
        """
        Train the LTR model
        
        Args:
            training_data: DataFrame with features and labels
            test_size: Fraction of data to use for testing
            random_state: Random seed for reproducibility
        """
        print("Training Learning-to-Rank model...")
        
        # Prepare features and labels
        X = self.feature_engineer.get_feature_matrix(training_data)
        y = self.feature_engineer.get_labels(training_data)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Create XGBoost model for ranking (pointwise approach)
        self.model = xgb.XGBRegressor(
            objective='reg:squarederror',
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=random_state,
            eval_metric='rmse'
        )
        
        # Train the model
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            early_stopping_rounds=10,
            verbose=True
        )
        
        # Evaluate the model
        self._evaluate_model(X_test, y_test, training_data)
        
        # Save the model
        self.save_model()
        
        print("Model training completed!")
    
    def _evaluate_model(self, X_test: np.ndarray, y_test: np.ndarray, training_data: pd.DataFrame):
        """Evaluate the trained model"""
        # Predictions
        y_pred = self.model.predict(X_test)
        
        # Calculate metrics
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        print(f"\nModel Evaluation:")
        print(f"MSE: {mse:.4f}")
        print(f"RMSE: {rmse:.4f}")
        
        # Feature importance
        feature_importance = self.model.feature_importances_
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': feature_importance
        }).sort_values('importance', ascending=False)
        
        print(f"\nFeature Importance:")
        for _, row in importance_df.iterrows():
            print(f"  {row['feature']}: {row['importance']:.4f}")
        
        # Save feature importance
        importance_df.to_csv('models/feature_importance.csv', index=False)
    
    def predict_scores(self, query: str, documents: List[Dict[str, Any]], mongodb_scores: List[float]) -> List[float]:
        """
        Predict relevance scores for documents given a query
        
        Args:
            query: Search query
            documents: List of documents from MongoDB
            mongodb_scores: List of original MongoDB scores
            
        Returns:
            List of predicted relevance scores
        """
        if not self.model:
            self.load_model()
        
        if not documents:
            return []
        
        # Extract features for all documents
        features_list = []
        for doc, mongo_score in zip(documents, mongodb_scores):
            features = self.feature_engineer.extract_features(query, doc, mongo_score)
            features_list.append([features[name] for name in self.feature_names])
        
        # Convert to numpy array
        X = np.array(features_list)
        
        # Predict scores
        scores = self.model.predict(X)
        
        return scores.tolist()
    
    def rank_documents(self, query: str, documents: List[Dict[str, Any]], mongodb_scores: List[float]) -> List[Tuple[int, float]]:
        """
        Rank documents by predicted relevance scores
        
        Args:
            query: Search query
            documents: List of documents from MongoDB
            mongodb_scores: List of original MongoDB scores
            
        Returns:
            List of (material_id, predicted_score) tuples, sorted by score descending
        """
        scores = self.predict_scores(query, documents, mongodb_scores)
        
        # Create (material_id, score) pairs
        ranked_pairs = []
        for doc, score in zip(documents, scores):
            material_id = doc.get('material_id')
            if material_id is not None:
                ranked_pairs.append((material_id, score))
        
        # Sort by score descending
        ranked_pairs.sort(key=lambda x: x[1], reverse=True)
        
        return ranked_pairs
    
    def save_model(self):
        """Save the trained model to disk"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """Load the trained model from disk"""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            print(f"Model loaded from {self.model_path}")
        else:
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
    
    def is_trained(self) -> bool:
        """Check if the model is trained and available"""
        return self.model is not None or os.path.exists(self.model_path) 