"""
Learning to Rank model training and evaluation for Eduki
Implements pointwise LTR using XGBoost with comprehensive evaluation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, ndcg_score
import xgboost as xgb
import joblib
import json
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime

from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EdukiLTRModel:
    """Learning to Rank model for Eduki teaching materials"""
    
    def __init__(self):
        self.model = None
        self.model_config = config.model
        self.feature_importance_ = None
        self.training_history = {}
        
    def prepare_data(self, features_df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare features and target for training"""
        logger.info("Preparing training data...")
        
        # Get feature columns (exclude ID and target columns)
        feature_cols = [col for col in features_df.columns 
                       if col not in ['relevance_score', 'user_id', 'material_id']]
        
        X = features_df[feature_cols].values
        y = features_df['relevance_score'].values
        
        logger.info(f"Prepared {X.shape[0]} samples with {X.shape[1]} features")
        
        return X, y, feature_cols
    
    def train_model(self, features_df: pd.DataFrame) -> Dict:
        """Train XGBoost model with comprehensive evaluation"""
        logger.info("Training LTR model...")
        
        X, y, feature_cols = self.prepare_data(features_df)
        
        # Split data into train, validation, and test sets
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=self.model_config.test_size, 
            random_state=self.model_config.random_state, stratify=None
        )
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=self.model_config.validation_size/(1-self.model_config.test_size),
            random_state=self.model_config.random_state
        )
        
        logger.info(f"Train: {X_train.shape[0]}, Val: {X_val.shape[0]}, Test: {X_test.shape[0]}")
        
        # Initialize XGBoost model
        self.model = xgb.XGBRegressor(
            n_estimators=self.model_config.n_estimators,
            max_depth=self.model_config.max_depth,
            learning_rate=self.model_config.learning_rate,
            random_state=self.model_config.random_state,
            objective=self.model_config.objective,
            eval_metric='rmse',
            early_stopping_rounds=20,
            verbose=False
        )
        
        # Train with validation set for early stopping
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_train, y_train), (X_val, y_val)],
            verbose=False
        )
        
        # Get training history
        self.training_history = {
            'train_rmse': self.model.evals_result()['validation_0']['rmse'],
            'val_rmse': self.model.evals_result()['validation_1']['rmse']
        }
        
        # Make predictions
        y_train_pred = self.model.predict(X_train)
        y_val_pred = self.model.predict(X_val)
        y_test_pred = self.model.predict(X_test)
        
        # Calculate metrics
        results = {
            'train_metrics': self._calculate_metrics(y_train, y_train_pred),
            'val_metrics': self._calculate_metrics(y_val, y_val_pred),
            'test_metrics': self._calculate_metrics(y_test, y_test_pred),
            'feature_importance': self._get_feature_importance(feature_cols),
            'X_test': X_test,
            'y_test': y_test,
            'y_test_pred': y_test_pred,
            'feature_names': feature_cols
        }
        
        # Log results
        logger.info(f"Training complete!")
        logger.info(f"Test RMSE: {results['test_metrics']['rmse']:.4f}")
        logger.info(f"Test R²: {results['test_metrics']['r2']:.4f}")
        
        return results
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Calculate regression and ranking metrics"""
        metrics = {
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred),
            'mse': mean_squared_error(y_true, y_pred)
        }
        
        return metrics
    
    def _get_feature_importance(self, feature_names: List[str]) -> pd.DataFrame:
        """Get feature importance from trained model"""
        if self.model is None:
            return pd.DataFrame()
        
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        self.feature_importance_ = importance_df
        return importance_df
    
    def calculate_ndcg(self, features_df: pd.DataFrame, k_values: Optional[List[int]] = None) -> Dict:
        """Calculate NDCG scores for ranking evaluation"""
        if self.model is None:
            logger.error("Model not trained yet")
            return {}
        
        if k_values is None:
            k_values = config.model.ndcg_k_values
        
        logger.info(f"Calculating NDCG@{k_values}...")
        
        # Get predictions for all interactions
        X, y_true, feature_cols = self.prepare_data(features_df)
        y_pred = self.model.predict(X)
        
        # Group by user to calculate NDCG per user
        user_ndcg_scores = {f'ndcg_{k}': [] for k in k_values}
        
        for user_id in features_df['user_id'].unique():
            user_mask = features_df['user_id'] == user_id
            user_true = y_true[user_mask]
            user_pred = y_pred[user_mask]
            
            if len(user_true) < 2:  # Need at least 2 items to rank
                continue
            
            # Calculate NDCG for each k
            for k in k_values:
                try:
                    ndcg_k = ndcg_score([user_true], [user_pred], k=k)
                    user_ndcg_scores[f'ndcg_{k}'].append(ndcg_k)
                except:
                    continue
        
        # Calculate average NDCG scores
        avg_ndcg = {}
        for k in k_values:
            scores = user_ndcg_scores[f'ndcg_{k}']
            if scores:
                avg_ndcg[f'ndcg_{k}'] = np.mean(scores)
                logger.info(f"Average NDCG@{k}: {avg_ndcg[f'ndcg_{k}']:.4f}")
            else:
                avg_ndcg[f'ndcg_{k}'] = 0.0
        
        return avg_ndcg
    
    def cross_validate(self, features_df: pd.DataFrame, cv_folds: int = 5) -> Dict:
        """Perform cross-validation"""
        logger.info(f"Performing {cv_folds}-fold cross-validation...")
        
        X, y, feature_cols = self.prepare_data(features_df)
        
        # Create model for CV
        cv_model = xgb.XGBRegressor(
            n_estimators=self.model_config.n_estimators,
            max_depth=self.model_config.max_depth,
            learning_rate=self.model_config.learning_rate,
            random_state=self.model_config.random_state,
            objective=self.model_config.objective
        )
        
        # Perform cross-validation
        cv_scores = cross_val_score(cv_model, X, y, cv=cv_folds, 
                                   scoring='neg_mean_squared_error')
        
        cv_results = {
            'cv_rmse_mean': np.sqrt(-cv_scores.mean()),
            'cv_rmse_std': np.sqrt(cv_scores.std()),
            'cv_scores': cv_scores
        }
        
        logger.info(f"CV RMSE: {cv_results['cv_rmse_mean']:.4f} ± {cv_results['cv_rmse_std']:.4f}")
        
        return cv_results
    
    def predict_relevance(self, features: np.ndarray) -> np.ndarray:
        """Predict relevance scores for new user-material pairs"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        return self.model.predict(features)
    
    def get_recommendations(self, user_id: str, candidate_materials: pd.DataFrame,
                           features_df: pd.DataFrame, top_k: int = 10) -> pd.DataFrame:
        """Get top-k recommendations for a user"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        logger.info(f"Generating top-{top_k} recommendations for user {user_id}")
        
        # Filter features for this user and candidate materials
        user_features = features_df[
            (features_df['user_id'] == user_id) & 
            (features_df['material_id'].isin(candidate_materials['material_id']))
        ]
        
        if len(user_features) == 0:
            logger.warning(f"No features found for user {user_id}")
            return pd.DataFrame()
        
        # Get feature matrix
        X, _, feature_cols = self.prepare_data(user_features)
        
        # Predict relevance scores
        relevance_scores = self.predict_relevance(X)
        
        # Create recommendations dataframe
        recommendations = user_features[['user_id', 'material_id']].copy()
        recommendations['predicted_relevance'] = relevance_scores
        
        # Merge with material information
        recommendations = recommendations.merge(
            candidate_materials[['material_id', 'title', 'subject', 'price', 'author_category']], 
            on='material_id', how='left'
        )
        
        # Sort by predicted relevance and return top-k
        recommendations = recommendations.sort_values('predicted_relevance', ascending=False).head(top_k)
        
        return recommendations
    
    def save_model(self, model_path: Optional[str] = None) -> None:
        """Save trained model"""
        if self.model is None:
            logger.error("No model to save")
            return
        
        if model_path is None:
            model_path = config.model_file
        
        joblib.dump(self.model, model_path)
        logger.info(f"Model saved to {model_path}")
    
    def load_model(self, model_path: Optional[str] = None) -> None:
        """Load trained model"""
        if model_path is None:
            model_path = config.model_file
        
        self.model = joblib.load(model_path)
        logger.info(f"Model loaded from {model_path}")
    
    def plot_training_history(self) -> None:
        """Plot training and validation loss"""
        if not self.training_history:
            logger.warning("No training history available")
            return
        
        plt.figure(figsize=(10, 6))
        
        epochs = range(1, len(self.training_history['train_rmse']) + 1)
        
        plt.plot(epochs, self.training_history['train_rmse'], 'b-', label='Training RMSE')
        plt.plot(epochs, self.training_history['val_rmse'], 'r-', label='Validation RMSE')
        
        plt.title('Model Training History')
        plt.xlabel('Epoch')
        plt.ylabel('RMSE')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def plot_feature_importance(self, top_n: int = 20) -> None:
        """Plot feature importance"""
        if self.feature_importance_ is None:
            logger.warning("No feature importance available")
            return
        
        plt.figure(figsize=(12, 8))
        
        top_features = self.feature_importance_.head(top_n)
        
        plt.barh(range(len(top_features)), top_features['importance'])
        plt.yticks(range(len(top_features)), top_features['feature'])
        plt.xlabel('Feature Importance')
        plt.title(f'Top {top_n} Feature Importance')
        plt.gca().invert_yaxis()
        
        plt.tight_layout()
        plt.show()
    
    def plot_predictions_vs_actual(self, y_true: np.ndarray, y_pred: np.ndarray) -> None:
        """Plot predictions vs actual values"""
        plt.figure(figsize=(10, 8))
        
        plt.scatter(y_true, y_pred, alpha=0.6, s=30)
        
        # Perfect prediction line
        min_val = min(y_true.min(), y_pred.min())
        max_val = max(y_true.max(), y_pred.max())
        plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')
        
        plt.xlabel('Actual Relevance Score')
        plt.ylabel('Predicted Relevance Score')
        plt.title('Predictions vs Actual Values')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Add R² score
        r2 = r2_score(y_true, y_pred)
        plt.text(0.05, 0.95, f'R² = {r2:.3f}', transform=plt.gca().transAxes, 
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.show()
    
    def plot_residuals(self, y_true: np.ndarray, y_pred: np.ndarray) -> None:
        """Plot residuals analysis"""
        residuals = y_true - y_pred
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Residuals vs Predictions
        axes[0].scatter(y_pred, residuals, alpha=0.6)
        axes[0].axhline(y=0, color='r', linestyle='--')
        axes[0].set_xlabel('Predicted Values')
        axes[0].set_ylabel('Residuals')
        axes[0].set_title('Residuals vs Predicted Values')
        axes[0].grid(True, alpha=0.3)
        
        # Residuals histogram
        axes[1].hist(residuals, bins=50, alpha=0.7, edgecolor='black')
        axes[1].set_xlabel('Residuals')
        axes[1].set_ylabel('Frequency')
        axes[1].set_title('Distribution of Residuals')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def generate_model_report(self, results: Dict, ndcg_results: Dict) -> Dict:
        """Generate comprehensive model evaluation report"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'model_config': {
                'n_estimators': self.model_config.n_estimators,
                'max_depth': self.model_config.max_depth,
                'learning_rate': self.model_config.learning_rate,
            },
            'performance_metrics': {
                'train': results['train_metrics'],
                'validation': results['val_metrics'],
                'test': results['test_metrics']
            },
            'ranking_metrics': ndcg_results,
            'feature_importance': results['feature_importance'].head(20).to_dict('records'),
            'model_summary': {
                'total_features': len(results['feature_names']),
                'best_iteration': getattr(self.model, 'best_iteration', None)
            }
        }
        
        return report
    
    def save_results(self, results: Dict, ndcg_results: Dict, 
                    file_path: Optional[str] = None) -> None:
        """Save experiment results to JSON"""
        if file_path is None:
            file_path = config.results_file
        
        report = self.generate_model_report(results, ndcg_results)
        
        with open(file_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Also save feature importance as CSV
        results['feature_importance'].to_csv(config.feature_importance_file, index=False)
        
        logger.info(f"Results saved to {file_path}")

if __name__ == "__main__":
    # Example usage
    from feature_engineering import EdukiFeatureEngineer
    
    # Load features
    logger.info("Loading features...")
    features_df = pd.read_csv(config.features_file)
    
    # Initialize and train model
    ltr_model = EdukiLTRModel()
    
    # Train model
    results = ltr_model.train_model(features_df)
    
    # Calculate NDCG
    ndcg_results = ltr_model.calculate_ndcg(features_df)
    
    # Cross-validation
    cv_results = ltr_model.cross_validate(features_df)
    
    # Save model and results
    ltr_model.save_model()
    ltr_model.save_results(results, ndcg_results)
    
    # Generate plots
    ltr_model.plot_training_history()
    ltr_model.plot_feature_importance()
    ltr_model.plot_predictions_vs_actual(results['y_test'], results['y_test_pred'])
    ltr_model.plot_residuals(results['y_test'], results['y_test_pred'])
    
    print("\n🎯 LTR Model Training Complete!")
    print(f"Test RMSE: {results['test_metrics']['rmse']:.4f}")
    print(f"Test R²: {results['test_metrics']['r2']:.4f}")
    print(f"NDCG@5: {ndcg_results.get('ndcg_5', 'N/A'):.4f}")
    print(f"NDCG@10: {ndcg_results.get('ndcg_10', 'N/A'):.4f}")