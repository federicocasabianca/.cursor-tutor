"""
Feature engineering module for Eduki LTR system
Creates comprehensive features for user-material interactions
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import logging
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib

from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EdukiFeatureEngineer:
    """Feature engineering for LTR model training"""
    
    def __init__(self):
        self.taxonomy = config.taxonomy
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        
    def create_features(self, users_df: pd.DataFrame, materials_df: pd.DataFrame, 
                       interactions_df: pd.DataFrame) -> pd.DataFrame:
        """Create comprehensive feature matrix for LTR training"""
        logger.info("Creating feature matrix...")
        
        features_list = []
        
        # Process interactions in batches for memory efficiency
        batch_size = 10000
        total_interactions = len(interactions_df)
        
        for i in range(0, total_interactions, batch_size):
            batch_end = min(i + batch_size, total_interactions)
            batch_interactions = interactions_df.iloc[i:batch_end]
            
            logger.info(f"Processing batch {i//batch_size + 1}/{(total_interactions-1)//batch_size + 1}")
            
            batch_features = self._process_interaction_batch(
                batch_interactions, users_df, materials_df
            )
            features_list.append(batch_features)
        
        # Combine all batches
        features_df = pd.concat(features_list, ignore_index=True)
        
        # Store feature column names
        self.feature_columns = [col for col in features_df.columns 
                               if col not in ['relevance_score', 'user_id', 'material_id']]
        
        logger.info(f"Created {len(features_df)} feature vectors with {len(self.feature_columns)} features")
        
        return features_df
    
    def _process_interaction_batch(self, interactions_batch: pd.DataFrame, 
                                  users_df: pd.DataFrame, materials_df: pd.DataFrame) -> pd.DataFrame:
        """Process a batch of interactions to create features"""
        
        # Merge with user and material data
        batch_with_users = interactions_batch.merge(users_df, on='user_id', how='left')
        batch_with_materials = batch_with_users.merge(materials_df, on='material_id', how='left')
        
        features_batch = []
        
        for _, row in batch_with_materials.iterrows():
            feature_vector = self._create_feature_vector(row)
            features_batch.append(feature_vector)
        
        return pd.DataFrame(features_batch)
    
    def _create_feature_vector(self, row: pd.Series) -> Dict:
        """Create feature vector for a single user-material interaction"""
        
        features = {
            'user_id': row['user_id'],
            'material_id': row['material_id'],
            'relevance_score': row['relevance_score']
        }
        
        # Material features
        features.update(self._create_material_features(row))
        
        # User features  
        features.update(self._create_user_features(row))
        
        # Interaction features
        features.update(self._create_interaction_features(row))
        
        # Temporal features
        features.update(self._create_temporal_features(row))
        
        # Context features
        features.update(self._create_context_features(row))
        
        return features
    
    def _create_material_features(self, row: pd.Series) -> Dict:
        """Create material-specific features"""
        features = {
            # Numerical material features
            'material_price': row['price'],
            'material_bestseller_rating': row['bestseller_rating'],
            'material_engagement_score': row['engagement_score'],
            'material_total_pages': row['total_pages'],
            'material_created_days_ago': row['created_days_ago'],
            'material_is_bundle': int(row['is_bundle']),
            
            # Derived material features
            'material_price_per_page': row['price'] / max(row['total_pages'], 1),
            'material_rating_score': np.log1p(row['bestseller_rating']),  # Log transform for better distribution
            'material_is_recent': int(row['created_days_ago'] <= 30),  # Recently created
            'material_is_premium': int(row['price'] > 15),  # Premium pricing
        }
        
        # One-hot encoded categorical features
        for subject in self.taxonomy.focus_subjects.keys():
            features[f'material_subject_{subject}'] = int(row['subject'] == subject)
        
        for material_type in self.taxonomy.material_types:
            clean_name = material_type.replace('/', '_').replace(' ', '_').replace('&', 'and')
            features[f'material_type_{clean_name}'] = int(row['material_type'] == material_type)
        
        for content_type in self.taxonomy.content_types:
            features[f'material_content_{content_type}'] = int(row['content_type'] == content_type)
        
        for author_cat in self.taxonomy.author_categories:
            features[f'material_author_{author_cat}'] = int(row['author_category'] == author_cat)
        
        return features
    
    def _create_user_features(self, row: pd.Series) -> Dict:
        """Create user-specific features"""
        features = {
            # Numerical user features
            'user_days_since_registration': row['days_since_registration'],
            'user_avg_monthly_purchases': row['avg_monthly_purchases'],
            
            # Derived user features
            'user_is_experienced': int(row['experience_level'] in ['experienced', 'expert']),
            'user_is_new': int(row['days_since_registration'] <= 60),
            'user_is_active': int(row['avg_monthly_purchases'] >= 3),
        }
        
        # One-hot encoded user features
        for sensitivity in ['low', 'medium', 'high']:
            features[f'user_price_sensitivity_{sensitivity}'] = int(row['price_sensitivity'] == sensitivity)
        
        for engagement in ['browser', 'focused', 'power_user']:
            features[f'user_engagement_{engagement}'] = int(row['engagement_style'] == engagement)
        
        for experience in ['novice', 'experienced', 'expert']:
            features[f'user_experience_{experience}'] = int(row['experience_level'] == experience)
        
        for subject in self.taxonomy.focus_subjects.keys():
            features[f'user_primary_subject_{subject}'] = int(row['primary_subject'] == subject)
        
        return features
    
    def _ensure_list(self, value):
        if isinstance(value, list):
            return value
        elif pd.isna(value) or value == '':
            return []
        else:
            return value.split(', ')
    
    def _create_interaction_features(self, row: pd.Series) -> Dict:
        """Create user-material interaction features"""
        
        # Parse grade levels and secondary subjects
        material_grades = set(self._ensure_list(row['grade_levels']))
        user_primary_grades = set(self._ensure_list(row['primary_grades']))
        user_secondary_subjects = self._ensure_list(row['secondary_subjects'])
        user_preferred_types = self._ensure_list(row['preferred_material_types'])
        
        features = {
            # Subject matching
            'subject_match_primary': int(row['subject'] == row['primary_subject']),
            'subject_match_secondary': int(row['subject'] in user_secondary_subjects),
            'subject_no_match': int(row['subject'] != row['primary_subject'] and row['subject'] not in user_secondary_subjects),
            
            # Grade level matching
            'grade_overlap_count': len(material_grades & user_primary_grades),
            'grade_perfect_match': int(material_grades == user_primary_grades),
            'grade_partial_match': int(len(material_grades & user_primary_grades) > 0),
            'grade_no_match': int(len(material_grades & user_primary_grades) == 0),
            
            # Material type preference
            'material_type_preferred': int(row['material_type'] in user_preferred_types),
            
            # Price-sensitivity matching
            'price_too_high_for_user': int(row['price_sensitivity'] == 'high' and row['price'] > 10),
            'price_affordable_for_user': int(row['price_sensitivity'] == 'high' and row['price'] <= 5),
            'price_premium_match': int(row['price_sensitivity'] == 'low' and row['price'] >= 15),
            
            # Content complexity matching
            'bundle_for_power_user': int(row['is_bundle'] and row['engagement_style'] == 'power_user'),
            'simple_for_novice': int(not row['is_bundle'] and row['experience_level'] == 'novice'),
            
            # Quality indicators
            'high_quality_match': int(row['author_category'] in ['Dragon', 'Innovators'] and row['engagement_style'] == 'power_user'),
            'beginner_friendly': int(row['author_category'] in ['Eggs', 'Cub'] and row['experience_level'] == 'novice'),
        }
        
        return features
    
    def _create_temporal_features(self, row: pd.Series) -> Dict:
        """Create time-based features"""
        
        # Parse timestamp if it's a string
        if isinstance(row['timestamp'], str):
            timestamp = pd.to_datetime(row['timestamp'])
        else:
            timestamp = row['timestamp']
        
        features = {
            # Time of interaction
            'interaction_hour': timestamp.hour,
            'interaction_day_of_week': timestamp.weekday(),
            'interaction_is_weekend': int(timestamp.weekday() >= 5),
            'interaction_is_evening': int(timestamp.hour >= 18),
            'interaction_is_school_hours': int(8 <= timestamp.hour <= 16),
            
            # Material age at interaction
            'material_age_at_interaction': row['created_days_ago'],
            'material_is_fresh': int(row['created_days_ago'] <= 7),
            'material_is_established': int(row['created_days_ago'] >= 365),
            
            # User tenure at interaction
            'user_tenure_months': row['days_since_registration'] / 30,
            'user_is_veteran': int(row['days_since_registration'] >= 365),
        }
        
        return features
    
    def _create_context_features(self, row: pd.Series) -> Dict:
        """Create contextual features"""
        features = {
            # Device context
            'device_desktop': int(row['device'] == 'desktop'),
            'device_mobile': int(row['device'] == 'mobile'),
            'device_tablet': int(row['device'] == 'tablet'),
            
            # Position in search results (if available)
            'position_in_results': row.get('position_in_results', 0) or 0,
            'position_top_3': int((row.get('position_in_results') or 0) <= 3),
            'position_first_page': int((row.get('position_in_results') or 0) <= 10),
            
            # Cross-feature interactions
            'mobile_and_bundle': int(row['device'] == 'mobile' and row['is_bundle']),
            'desktop_and_premium': int(row['device'] == 'desktop' and row['price'] > 15),
            'weekend_and_planning': int(row['timestamp'].weekday() >= 5 and row['material_type'] in ['Stundenentwürfe', 'Unterrichtsreihen']),
        }
        
        return features
    
    def scale_features(self, features_df: pd.DataFrame, fit_scaler: bool = True) -> pd.DataFrame:
        """Scale numerical features"""
        logger.info("Scaling numerical features...")
        
        # Identify numerical columns
        numerical_cols = [
            'material_price', 'material_bestseller_rating', 'material_engagement_score',
            'material_total_pages', 'material_created_days_ago', 'material_price_per_page',
            'material_rating_score', 'user_days_since_registration', 'user_avg_monthly_purchases',
            'grade_overlap_count', 'interaction_hour', 'interaction_day_of_week',
            'material_age_at_interaction', 'user_tenure_months', 'position_in_results'
        ]
        
        # Only scale columns that exist in the dataframe
        numerical_cols = [col for col in numerical_cols if col in features_df.columns]
        
        features_scaled = features_df.copy()
        
        if fit_scaler:
            # Fit and transform
            features_scaled[numerical_cols] = self.scaler.fit_transform(features_df[numerical_cols])
        else:
            # Only transform
            features_scaled[numerical_cols] = self.scaler.transform(features_df[numerical_cols])
        
        return features_scaled
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature column names"""
        return self.feature_columns
    
    def save_preprocessors(self) -> None:
        """Save scaler and encoders"""
        logger.info("Saving feature preprocessors...")
        joblib.dump(self.scaler, config.scaler_file)
        logger.info(f"Preprocessors saved to {config.models_dir}")
    
    def load_preprocessors(self) -> None:
        """Load scaler and encoders"""
        logger.info("Loading feature preprocessors...")
        self.scaler = joblib.load(config.scaler_file)
        logger.info("Preprocessors loaded successfully")
    
    def create_and_save_features(self, users_df: pd.DataFrame, materials_df: pd.DataFrame, 
                                interactions_df: pd.DataFrame) -> pd.DataFrame:
        """Create features and save to file"""
        features_df = self.create_features(users_df, materials_df, interactions_df)
        features_scaled = self.scale_features(features_df, fit_scaler=True)
        
        # Save features
        features_scaled.to_csv(config.features_file, index=False)
        logger.info(f"Features saved to {config.features_file}")
        
        # Save preprocessors
        self.save_preprocessors()
        
        return features_scaled
    
    def analyze_features(self, features_df: pd.DataFrame) -> Dict:
        """Analyze feature distributions and correlations"""
        logger.info("Analyzing feature characteristics...")
        
        feature_cols = self.get_feature_names()
        
        analysis = {
            'n_features': len(feature_cols),
            'n_samples': len(features_df),
            'feature_stats': features_df[feature_cols].describe(),
            'missing_values': features_df[feature_cols].isnull().sum(),
            'correlation_with_target': features_df[feature_cols + ['relevance_score']].corr()['relevance_score'].sort_values(ascending=False)
        }
        
        # Identify highly correlated features
        corr_matrix = features_df[feature_cols].corr()
        high_corr_pairs = []
        
        for i in range(len(feature_cols)):
            for j in range(i+1, len(feature_cols)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.8:
                    high_corr_pairs.append((feature_cols[i], feature_cols[j], corr_val))
        
        analysis['high_correlation_pairs'] = high_corr_pairs
        
        logger.info(f"Feature analysis complete: {analysis['n_features']} features, {analysis['n_samples']} samples")
        
        return analysis

if __name__ == "__main__":
    # Example usage
    from data_generator import EdukiDataGenerator
    
    # Generate or load data
    generator = EdukiDataGenerator()
    materials_df, users_df, interactions_df = generator.load_data()
    
    # Create features
    feature_engineer = EdukiFeatureEngineer()
    features_df = feature_engineer.create_and_save_features(users_df, materials_df, interactions_df)
    
    # Analyze features
    analysis = feature_engineer.analyze_features(features_df)
    
    print(f"\n📊 Feature Engineering Summary:")
    print(f"Total features: {analysis['n_features']}")
    print(f"Total samples: {analysis['n_samples']}")
    print(f"\nTop 10 features correlated with relevance:")
    print(analysis['correlation_with_target'].head(10))