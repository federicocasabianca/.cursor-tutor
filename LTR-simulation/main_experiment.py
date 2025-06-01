"""
Main experiment script for Eduki LTR system
Runs complete pipeline: data generation → feature engineering → model training → evaluation
"""

import os
import sys
import pandas as pd
import numpy as np
import argparse
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from data_generator import EdukiDataGenerator
from feature_engineering import EdukiFeatureEngineer
from ltr_model import EdukiLTRModel

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(config.results_dir, 'experiment.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EdukiLTRExperiment:
    """Complete LTR experiment pipeline"""
    
    def __init__(self, experiment_name: str = None):
        self.experiment_name = experiment_name or config.experiment.experiment_name
        self.start_time = datetime.now()
        
        logger.info(f"🚀 Starting LTR Experiment: {self.experiment_name}")
        logger.info(f"Configuration: {config.data_generation.n_materials} materials, "
                   f"{config.data_generation.n_users} users, "
                   f"{config.data_generation.n_interactions} interactions")
    
    def run_data_generation(self, force_regenerate: bool = False) -> tuple:
        """Generate or load synthetic data"""
        logger.info("📊 Step 1: Data Generation")
        
        generator = EdukiDataGenerator()
        
        # Check if data already exists
        if (not force_regenerate and 
            os.path.exists(config.raw_materials_file) and
            os.path.exists(config.raw_users_file) and 
            os.path.exists(config.raw_interactions_file)):
            
            logger.info("Loading existing data...")
            materials_df, users_df, interactions_df = generator.load_data()
        else:
            logger.info("Generating new synthetic data...")
            materials_df, users_df, interactions_df = generator.generate_and_save_all()
        
        # Log data statistics
        self._log_data_statistics(materials_df, users_df, interactions_df)
        
        return materials_df, users_df, interactions_df
    
    def run_feature_engineering(self, users_df: pd.DataFrame, materials_df: pd.DataFrame, 
                               interactions_df: pd.DataFrame, force_regenerate: bool = False) -> pd.DataFrame:
        """Create feature matrix for training"""
        logger.info("🔧 Step 2: Feature Engineering")
        
        feature_engineer = EdukiFeatureEngineer()
        
        # Check if features already exist
        if not force_regenerate and os.path.exists(config.features_file):
            logger.info("Loading existing features...")
            features_df = pd.read_csv(config.features_file)
            feature_engineer.load_preprocessors()
        else:
            logger.info("Creating new features...")
            features_df = feature_engineer.create_and_save_features(users_df, materials_df, interactions_df)
        
        # Analyze features
        analysis = feature_engineer.analyze_features(features_df)
        self._log_feature_analysis(analysis)
        
        return features_df
    
    def run_model_training(self, features_df: pd.DataFrame) -> tuple:
        """Train LTR model and evaluate performance"""
        logger.info("🤖 Step 3: Model Training & Evaluation")
        
        ltr_model = EdukiLTRModel()
        
        # Train model
        logger.info("Training XGBoost model...")
        results = ltr_model.train_model(features_df)
        
        # Calculate ranking metrics
        logger.info("Calculating NDCG scores...")
        ndcg_results = ltr_model.calculate_ndcg(features_df)
        
        # Cross-validation
        logger.info("Performing cross-validation...")
        cv_results = ltr_model.cross_validate(features_df)
        
        # Save model and results
        if config.experiment.save_model:
            ltr_model.save_model()
        
        if config.experiment.save_results:
            ltr_model.save_results(results, ndcg_results)
        
        # Generate visualizations
        if config.experiment.plot_results:
            self._generate_visualizations(ltr_model, results, ndcg_results)
        
        return ltr_model, results, ndcg_results, cv_results
    
    def run_recommendation_demo(self, ltr_model: EdukiLTRModel, materials_df: pd.DataFrame,
                               users_df: pd.DataFrame, features_df: pd.DataFrame) -> None:
        """Demonstrate recommendation generation"""
        logger.info("🎯 Step 4: Recommendation Demo")
        
        # Select a few random users for demo
        demo_users = users_df.sample(3)
        
        for _, user in demo_users.iterrows():
            logger.info(f"\n👩‍🏫 User: {user['user_id']}")
            logger.info(f"Primary Subject: {user['primary_subject']}")
            logger.info(f"Primary Grades: {user['primary_grades_str']}")
            logger.info(f"Engagement Style: {user['engagement_style']}")
            
            # Get candidate materials (all materials for demo)
            candidate_materials = materials_df.sample(min(100, len(materials_df)))
            
            try:
                recommendations = ltr_model.get_recommendations(
                    user['user_id'], candidate_materials, features_df, top_k=5
                )
                
                if len(recommendations) > 0:
                    logger.info("Top 5 Recommendations:")
                    for idx, rec in recommendations.iterrows():
                        logger.info(f"  {rec['material_id']}: {rec['title']} "
                                  f"(Score: {rec['predicted_relevance']:.3f}, "
                                  f"Price: €{rec['price']}, Subject: {rec['subject']})")
                else:
                    logger.info("No recommendations generated")
                    
            except Exception as e:
                logger.error(f"Error generating recommendations: {e}")
    
    def run_complete_experiment(self, force_regenerate_data: bool = False,
                               force_regenerate_features: bool = False) -> dict:
        """Run complete LTR experiment pipeline"""
        
        try:
            # Step 1: Data Generation
            materials_df, users_df, interactions_df = self.run_data_generation(force_regenerate_data)
            
            # Step 2: Feature Engineering
            features_df = self.run_feature_engineering(
                users_df, materials_df, interactions_df, force_regenerate_features
            )
            
            # Step 3: Model Training
            ltr_model, results, ndcg_results, cv_results = self.run_model_training(features_df)
            
            # Step 4: Recommendation Demo
            self.run_recommendation_demo(ltr_model, materials_df, users_df, features_df)
            
            # Set end time before generating the final report
            self.end_time = datetime.now()
            duration = self.end_time - self.start_time
            
            # Generate final report
            final_report = self._generate_final_report(results, ndcg_results, cv_results)
            
            logger.info(f"✅ Experiment completed successfully!")
            logger.info(f"Total duration: {duration}")
            logger.info(f"Results saved to: {config.results_dir}")
            
            return final_report
            
        except Exception as e:
            logger.error(f"❌ Experiment failed: {e}")
            raise
    
    def _log_data_statistics(self, materials_df: pd.DataFrame, users_df: pd.DataFrame, 
                           interactions_df: pd.DataFrame) -> None:
        """Log data generation statistics"""
        logger.info(f"📈 Data Statistics:")
        logger.info(f"  Materials: {len(materials_df):,}")
        logger.info(f"  Users: {len(users_df):,}")
        logger.info(f"  Interactions: {len(interactions_df):,}")
        
        logger.info(f"  Subject distribution: {materials_df['subject'].value_counts().to_dict()}")
        logger.info(f"  Event distribution: {interactions_df['event_type'].value_counts().to_dict()}")
        logger.info(f"  Price range: €{materials_df['price'].min():.2f} - €{materials_df['price'].max():.2f}")
    
    def _log_feature_analysis(self, analysis: dict) -> None:
        """Log feature engineering analysis"""
        logger.info(f"🔍 Feature Analysis:")
        logger.info(f"  Total features: {analysis['n_features']}")
        logger.info(f"  Total samples: {analysis['n_samples']}")
        logger.info(f"  Missing values: {analysis['missing_values'].sum()}")
        
        logger.info("  Top 5 features correlated with relevance:")
        top_corr = analysis['correlation_with_target'].head(5)
        for feature, corr in top_corr.items():
            logger.info(f"    {feature}: {corr:.3f}")
    
    def _generate_visualizations(self, ltr_model: EdukiLTRModel, results: dict, 
                               ndcg_results: dict) -> None:
        """Generate and save visualizations"""
        logger.info("📊 Generating visualizations...")
        
        try:
            # Training history
            ltr_model.plot_training_history()
            
            # Feature importance
            ltr_model.plot_feature_importance(top_n=20)
            
            # Predictions vs actual
            ltr_model.plot_predictions_vs_actual(results['y_test'], results['y_test_pred'])
            
            # Residuals analysis
            ltr_model.plot_residuals(results['y_test'], results['y_test_pred'])
            
        except Exception as e:
            logger.warning(f"Error generating visualizations: {e}")
    
    def _generate_final_report(self, results: dict, ndcg_results: dict, cv_results: dict) -> dict:
        """Generate final experiment report"""
        
        report = {
            'experiment_name': self.experiment_name,
            'timestamp': self.start_time.isoformat(),
            'duration_seconds': (self.end_time - self.start_time).total_seconds(),
            'config': {
                'n_materials': config.data_generation.n_materials,
                'n_users': config.data_generation.n_users,
                'n_interactions': config.data_generation.n_interactions,
                'model_params': {
                    'n_estimators': config.model.n_estimators,
                    'max_depth': config.model.max_depth,
                    'learning_rate': config.model.learning_rate
                }
            },
            'performance': {
                'test_rmse': results['test_metrics']['rmse'],
                'test_r2': results['test_metrics']['r2'],
                'test_mae': results['test_metrics']['mae'],
                'cv_rmse': cv_results['cv_rmse_mean'],
                'cv_rmse_std': cv_results['cv_rmse_std']
            },
            'ranking_performance': ndcg_results,
            'top_features': results['feature_importance'].head(10).to_dict('records')
        }
        
        logger.info("📋 Final Report:")
        logger.info(f"  Test RMSE: {report['performance']['test_rmse']:.4f}")
        logger.info(f"  Test R²: {report['performance']['test_r2']:.4f}")
        logger.info(f"  CV RMSE: {report['performance']['cv_rmse']:.4f} ± {report['performance']['cv_rmse_std']:.4f}")
        
        for k in [5, 10, 20]:
            ndcg_k = ndcg_results.get(f'ndcg_{k}', 0)
            if ndcg_k > 0:
                logger.info(f"  NDCG@{k}: {ndcg_k:.4f}")
        
        return report

def main():
    """Main experiment entry point"""
    parser = argparse.ArgumentParser(description='Run Eduki LTR Experiment')
    parser.add_argument('--name', type=str, default='baseline_ltr', 
                       help='Experiment name')
    parser.add_argument('--force-data', action='store_true',
                       help='Force regenerate data')
    parser.add_argument('--force-features', action='store_true',
                       help='Force regenerate features')
    parser.add_argument('--materials', type=int, default=5000,
                       help='Number of materials to generate')
    parser.add_argument('--users', type=int, default=1000,
                       help='Number of users to generate')
    parser.add_argument('--interactions', type=int, default=50000,
                       help='Number of interactions to generate')
    
    args = parser.parse_args()
    
    # Update config with command line arguments
    config.data_generation.n_materials = args.materials
    config.data_generation.n_users = args.users
    config.data_generation.n_interactions = args.interactions
    config.experiment.experiment_name = args.name
    
    # Run experiment
    experiment = EdukiLTRExperiment(args.name)
    final_report = experiment.run_complete_experiment(
        force_regenerate_data=args.force_data,
        force_regenerate_features=args.force_features
    )
    
    return final_report

if __name__ == "__main__":
    final_report = main()