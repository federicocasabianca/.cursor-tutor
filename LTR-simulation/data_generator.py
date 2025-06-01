"""
Data generation module for Eduki LTR simulation
Generates realistic materials, users, and interactions based on actual taxonomy
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple
import logging

from config import config, INTERACTION_PATTERNS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EdukiDataGenerator:
    """Generates synthetic but realistic data for Eduki marketplace"""
    
    def __init__(self):
        self.taxonomy = config.taxonomy
        self.relevance_config = config.relevance
        self.data_config = config.data_generation
        
        # Set random seeds for reproducibility
        np.random.seed(config.experiment.numpy_seed)
        random.seed(config.experiment.random_seed)
    
    def generate_materials(self) -> pd.DataFrame:
        """Generate realistic material dataset"""
        logger.info(f"Generating {self.data_config.n_materials} materials...")
        
        materials = []
        
        for i in range(self.data_config.n_materials):
            # Select random subject and subcategory
            subject = np.random.choice(list(self.taxonomy.focus_subjects.keys()))
            subcategory = np.random.choice(self.taxonomy.focus_subjects[subject])
            
            # Generate material features
            material = {
                'material_id': f"mat_{i+1:06d}",
                'subject': subject,
                'subcategory': subcategory,
                'grade_levels': self._select_grade_levels(),
                'material_type': np.random.choice(self.taxonomy.material_types),
                'school_type': np.random.choice(self.taxonomy.school_types),
                'content_type': np.random.choice(self.taxonomy.content_types),
                'is_bundle': np.random.choice([0, 1], p=[1-self.data_config.bundle_probability, 
                                                       self.data_config.bundle_probability]),
                'price': self._generate_price(),
                'author_category': np.random.choice(self.taxonomy.author_categories, 
                                                  p=self.data_config.author_distribution),
                'bestseller_rating': np.random.exponential(50),
                'total_pages': np.random.poisson(8) + 1,
                'engagement_score': np.random.gamma(2, 2),
                'created_days_ago': np.random.randint(1, 365*3),
                'author_id': f"author_{np.random.randint(1, 1000):04d}",
            }
            
            # Adjust features based on bundle status
            if material['is_bundle']:
                material['price'] *= np.random.uniform(2, 5)
                material['total_pages'] *= np.random.randint(3, 8)
                material['title'] = f"{subcategory} - Sparpaket"
            else:
                material['title'] = f"{subcategory} - {material['material_type']}"
            
            # Add grade levels as string for easier processing
            material['grade_levels_str'] = ', '.join(material['grade_levels'])
            
            materials.append(material)
        
        df = pd.DataFrame(materials)
        logger.info(f"Generated materials with subjects: {df['subject'].value_counts().to_dict()}")
        
        return df
    
    def generate_users(self) -> pd.DataFrame:
        """Generate realistic user profiles"""
        logger.info(f"Generating {self.data_config.n_users} users...")
        
        users = []
        
        for i in range(self.data_config.n_users):
            # Select user's primary teaching focus
            primary_subject = np.random.choice(list(self.taxonomy.focus_subjects.keys()))
            primary_grades = self._select_primary_grades()
            
            # Select secondary subjects (0-2 additional subjects)
            available_subjects = [s for s in self.taxonomy.focus_subjects.keys() 
                                if s != primary_subject]
            n_secondary = np.random.randint(0, 3)
            secondary_subjects = np.random.choice(available_subjects, 
                                                size=min(n_secondary, len(available_subjects)), 
                                                replace=False).tolist()
            
            user = {
                'user_id': f"user_{i+1:06d}",
                'primary_subject': primary_subject,
                'primary_grades': primary_grades,
                'primary_grades_str': ', '.join(primary_grades),
                'secondary_subjects': secondary_subjects,
                'secondary_subjects_str': ', '.join(secondary_subjects),
                'school_type': np.random.choice(self.taxonomy.school_types),
                'price_sensitivity': np.random.choice(['low', 'medium', 'high'], 
                                                    p=self.data_config.price_sensitivity_distribution),
                'engagement_style': np.random.choice(['browser', 'focused', 'power_user'], 
                                                   p=self.data_config.engagement_distribution),
                'experience_level': np.random.choice(['novice', 'experienced', 'expert'], 
                                                   p=[0.3, 0.5, 0.2]),
                'days_since_registration': np.random.randint(30, 365*2),
                'avg_monthly_purchases': np.random.poisson(3) + 1,
                'preferred_material_types': self._select_preferred_material_types()
            }
            
            users.append(user)
        
        df = pd.DataFrame(users)
        logger.info(f"Generated users with engagement styles: {df['engagement_style'].value_counts().to_dict()}")
        
        return df
    
    def generate_interactions(self, users_df: pd.DataFrame, materials_df: pd.DataFrame) -> pd.DataFrame:
        """Generate realistic user-material interactions"""
        logger.info(f"Generating {self.data_config.n_interactions} interactions...")
        
        interactions = []
        
        for _ in range(self.data_config.n_interactions):
            # Select random user
            user = users_df.sample(1).iloc[0]
            
            # Select material based on user preferences (70% relevant, 30% exploration)
            if np.random.random() < 0.7:
                material = self._select_relevant_material(user, materials_df)
            else:
                material = materials_df.sample(1).iloc[0]
            
            # Generate event type based on user engagement style
            event_type = self._select_event_type(user['engagement_style'])
            
            # Calculate relevance based on user-material match
            relevance_score = self._calculate_relevance(user, material, event_type)
            
            # Generate timestamp (within last 90 days)
            timestamp = datetime.now() - timedelta(days=np.random.randint(1, 91))
            
            interaction = {
                'user_id': user['user_id'],
                'material_id': material['material_id'],
                'event_type': event_type,
                'relevance_score': relevance_score,
                'timestamp': timestamp,
                'date': timestamp.date(),
                'device': np.random.choice(['desktop', 'mobile', 'tablet'], p=[0.6, 0.3, 0.1]),
                'session_id': f"session_{np.random.randint(1, 100000):06d}",
                'position_in_results': np.random.randint(1, 21) if event_type in ['viewMaterial', 'showMaterialPreview'] else None
            }
            
            interactions.append(interaction)
        
        df = pd.DataFrame(interactions)
        logger.info(f"Generated interactions with events: {df['event_type'].value_counts().to_dict()}")
        
        return df
    
    def _select_grade_levels(self) -> List[str]:
        """Select grade levels for a material"""
        n_grades = np.random.choice([1, 2, 3, 4], p=[0.4, 0.3, 0.2, 0.1])
        
        # Tend to select consecutive grades
        start_idx = np.random.randint(0, len(self.taxonomy.grade_levels) - n_grades + 1)
        return self.taxonomy.grade_levels[start_idx:start_idx + n_grades]
    
    def _select_primary_grades(self) -> List[str]:
        """Select primary teaching grades for a user"""
        n_grades = np.random.choice([1, 2, 3], p=[0.3, 0.5, 0.2])
        start_idx = np.random.randint(0, len(self.taxonomy.grade_levels) - n_grades + 1)
        return self.taxonomy.grade_levels[start_idx:start_idx + n_grades]
    
    def _select_preferred_material_types(self) -> List[str]:
        """Select preferred material types for a user"""
        n_types = np.random.choice([2, 3, 4], p=[0.3, 0.5, 0.2])
        return np.random.choice(self.taxonomy.material_types, size=n_types, replace=False).tolist()
    
    def _generate_price(self) -> float:
        """Generate realistic price following log-normal distribution"""
        price = np.random.lognormal(self.data_config.price_log_mean, 
                                   self.data_config.price_log_std)
        return round(max(0.5, min(50.0, price)), 2)  # Clamp between 0.5 and 50 euros
    
    def _select_relevant_material(self, user: pd.Series, materials_df: pd.DataFrame) -> pd.Series:
        """Select a material relevant to user preferences"""
        # Filter materials by subject preference
        relevant_materials = materials_df[
            (materials_df['subject'] == user['primary_subject']) |
            (materials_df['subject'].isin(user['secondary_subjects']))
        ]
        
        if len(relevant_materials) == 0:
            return materials_df.sample(1).iloc[0]
        
        # Further filter by grade overlap
        grade_overlap_materials = relevant_materials[
            relevant_materials['grade_levels_str'].apply(
                lambda x: bool(set(x.split(', ')) & set(user['primary_grades']))
            )
        ]
        
        if len(grade_overlap_materials) > 0:
            return grade_overlap_materials.sample(1).iloc[0]
        else:
            return relevant_materials.sample(1).iloc[0]
    
    def _select_event_type(self, engagement_style: str) -> str:
        """Select event type based on user engagement style"""
        pattern = INTERACTION_PATTERNS[engagement_style]
        event_types = list(pattern['event_probs'].keys())
        probabilities = list(pattern['event_probs'].values())
        return np.random.choice(event_types, p=probabilities)
    
    def _calculate_relevance(self, user: pd.Series, material: pd.Series, event_type: str) -> float:
        """Calculate relevance score based on user-material match and event type"""
        # Base score from event type
        base_score = self.relevance_config.event_weights[event_type]
        
        # Subject match bonus
        if material['subject'] == user['primary_subject']:
            base_score *= self.relevance_config.subject_match_primary
        elif material['subject'] in user['secondary_subjects']:
            base_score *= self.relevance_config.subject_match_secondary
        
        # Grade level match bonus
        material_grades = set(material['grade_levels'])
        user_grades = set(user['primary_grades'])
        grade_overlap = material_grades & user_grades
        
        if grade_overlap:
            bonus = 1 + (self.relevance_config.grade_overlap_bonus * len(grade_overlap))
            base_score *= bonus
        
        # Price sensitivity adjustment
        if user['price_sensitivity'] == 'high' and material['price'] > 10:
            base_score *= self.relevance_config.price_sensitivity_penalty
        elif user['price_sensitivity'] == 'low' and material['price'] > 20:
            base_score *= self.relevance_config.price_insensitive_bonus
        
        # Material type preference bonus
        if material['material_type'] in user['preferred_material_types']:
            base_score *= 1.1
        
        # Author category bonus (higher category = higher quality)
        author_multipliers = {
            'Eggs': 0.9, 'Cub': 1.0, 'Bear': 1.1, 'Dragon': 1.2, 'Innovators': 1.3
        }
        base_score *= author_multipliers.get(material['author_category'], 1.0)
        
        # Add some realistic noise
        noise = np.random.normal(0, 0.1)
        final_score = max(0, base_score + noise)
        
        return round(final_score, 4)
    
    def save_data(self, materials_df: pd.DataFrame, users_df: pd.DataFrame, 
                  interactions_df: pd.DataFrame) -> None:
        """Save generated data to CSV files"""
        logger.info("Saving generated data...")
        
        materials_df.to_csv(config.raw_materials_file, index=False)
        users_df.to_csv(config.raw_users_file, index=False)
        interactions_df.to_csv(config.raw_interactions_file, index=False)
        
        logger.info(f"Data saved to {config.data_dir}")
    
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load previously generated data"""
        logger.info("Loading existing data...")
        
        materials_df = pd.read_csv(config.raw_materials_file)
        users_df = pd.read_csv(config.raw_users_file)
        interactions_df = pd.read_csv(config.raw_interactions_file)
        
        # Convert string lists back to actual lists
        for df, list_cols in [
            (materials_df, ['grade_levels']),
            (users_df, ['primary_grades', 'secondary_subjects', 'preferred_material_types']),
        ]:
            for col in list_cols:
                if col in df.columns:
                    df[col] = df[f'{col}_str'].apply(lambda x: x.split(', ') if pd.notna(x) and x else [])
        
        return materials_df, users_df, interactions_df
    
    def generate_and_save_all(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Generate all data and save to files"""
        materials_df = self.generate_materials()
        users_df = self.generate_users()
        interactions_df = self.generate_interactions(users_df, materials_df)
        
        self.save_data(materials_df, users_df, interactions_df)
        
        return materials_df, users_df, interactions_df

if __name__ == "__main__":
    # Example usage
    generator = EdukiDataGenerator()
    materials_df, users_df, interactions_df = generator.generate_and_save_all()
    
    print("\n📊 Dataset Summary:")
    print(f"Materials: {len(materials_df):,}")
    print(f"Users: {len(users_df):,}")
    print(f"Interactions: {len(interactions_df):,}")
    
    print(f"\nSubject distribution:")
    print(materials_df['subject'].value_counts())
    
    print(f"\nEvent type distribution:")
    print(interactions_df['event_type'].value_counts())
    
    print(f"\nPrice statistics:")
    print(materials_df['price'].describe())