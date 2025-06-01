"""
Configuration file for Eduki LTR System
Contains all constants, taxonomy definitions, and hyperparameters
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Any

# Project paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')
MODELS_DIR = os.path.join(RESULTS_DIR, 'models')

# Create directories if they don't exist
for dir_path in [DATA_DIR, RESULTS_DIR, MODELS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

@dataclass
class TaxonomyConfig:
    """Eduki taxonomy configuration based on real data"""
    
    # Focus subjects as requested
    focus_subjects: Dict[str, List[str]] = None
    
    # Grade levels (German system)
    grade_levels: List[str] = None
    
    # Material types from taxonomy
    material_types: List[str] = None
    
    # School types (focused on German system)
    school_types: List[str] = None
    
    # Author categories based on sales performance
    author_categories: List[str] = None
    
    # Content structure types
    content_types: List[str] = None
    
    def __post_init__(self):
        if self.focus_subjects is None:
            self.focus_subjects = {
                'Mathematik': ['Grundrechenarten', 'Geometrie', 'Funktionen', 'Stochastik', 'Zahlen & Operationen'],
                'Deutsch': ['Lesen', 'Schreiben', 'Sprache untersuchen', 'Sprechen & Zuhören', 'Anfangsunterricht'],
                'Englisch': ['Grammatik', 'Wortschatz', 'Leseverstehen', 'Schreiben', 'Sprechen'],
                'Kunst': ['Malen & Zeichnen', 'Theorie', 'Basteln', 'Werken', 'Epochen'],
                'Fachunterricht': ['Biologie', 'Chemie', 'Geschichte', 'Erdkunde', 'Religion']
            }
        
        if self.grade_levels is None:
            self.grade_levels = [
                '1. Klasse', '2. Klasse', '3. Klasse', '4. Klasse', '5. Klasse',
                '6. Klasse', '7. Klasse', '8. Klasse', '9. Klasse', '10. Klasse',
                '11. Klasse', '12. Klasse', '13. Klasse'
            ]
        
        if self.material_types is None:
            self.material_types = [
                'Arbeitsblätter', 'Unterrichtsreihen', 'Stundenentwürfe', 'Merkblätter',
                'Präsentationen/Tafelbilder', 'Stationenlernen', 'Test', 'Spiele',
                'Klassenarbeiten', 'Experimente', 'Mal- und Bastelvorlagen', 'Bildkarten',
                'Fördermaterial/Inklusion', 'Videos', 'Interaktives Material', 'Quiz'
            ]
        
        if self.school_types is None:
            self.school_types = [
                'Kita / Vorschule', 'Grundschule', 'Sek I Mittlere Schulform',
                'Sek I Gymnasium', 'Sek II', 'Berufsschule', 'Förderunterricht'
            ]
        
        if self.author_categories is None:
            self.author_categories = ['Eggs', 'Cub', 'Bear', 'Dragon', 'Innovators']
        
        if self.content_types is None:
            self.content_types = ['standalone', 'hybrid', 'interactive']

@dataclass
class RelevanceConfig:
    """Configuration for relevance scoring"""
    
    # Event weights based on Eduki user behavior
    event_weights: Dict[str, float] = None
    
    # Bonus multipliers for matching features
    subject_match_primary: float = 1.5
    subject_match_secondary: float = 1.2
    grade_overlap_bonus: float = 0.1
    price_sensitivity_penalty: float = 0.7
    price_insensitive_bonus: float = 1.1
    
    def __post_init__(self):
        if self.event_weights is None:
            self.event_weights = {
                'viewMaterial': 1.0,
                'showMaterialPreview': 2.0,
                'addToFavorites': 3.0,
                'addToCart': 4.0,
                'freeDownload': 4.0,
                'purchase': 5.0
            }

@dataclass
class DataGenerationConfig:
    """Configuration for synthetic data generation"""
    
    # Dataset sizes
    n_materials: int = 5000
    n_users: int = 1000
    n_interactions: int = 50000
    
    # Distribution parameters
    bundle_probability: float = 0.2
    price_log_mean: float = 1.5
    price_log_std: float = 0.8
    
    # Author category distribution (pyramid structure)
    author_distribution: List[float] = None
    
    # User engagement patterns
    engagement_distribution: List[float] = None
    price_sensitivity_distribution: List[float] = None
    
    def __post_init__(self):
        if self.author_distribution is None:
            self.author_distribution = [0.3, 0.25, 0.2, 0.15, 0.1]  # Eggs to Innovators
        
        if self.engagement_distribution is None:
            self.engagement_distribution = [0.4, 0.4, 0.2]  # browser, focused, power_user
        
        if self.price_sensitivity_distribution is None:
            self.price_sensitivity_distribution = [0.2, 0.5, 0.3]  # low, medium, high

@dataclass
class ModelConfig:
    """Configuration for LTR model training"""
    
    # XGBoost parameters
    n_estimators: int = 100
    max_depth: int = 6
    learning_rate: float = 0.1
    random_state: int = 42
    objective: str = 'reg:squarederror'
    
    # Training parameters
    test_size: float = 0.2
    validation_size: float = 0.1
    
    # Evaluation parameters
    ndcg_k_values: List[int] = None
    
    def __post_init__(self):
        if self.ndcg_k_values is None:
            self.ndcg_k_values = [5, 10, 20]

@dataclass
class ExperimentConfig:
    """Configuration for experiments"""
    
    # Experiment tracking
    experiment_name: str = "baseline_ltr"
    save_results: bool = True
    save_model: bool = True
    
    # Visualization
    plot_results: bool = True
    save_plots: bool = True
    
    # Random seeds for reproducibility
    numpy_seed: int = 42
    random_seed: int = 42

# Main configuration object
class Config:
    """Main configuration class combining all configs"""
    
    def __init__(self):
        self.taxonomy = TaxonomyConfig()
        self.relevance = RelevanceConfig()
        self.data_generation = DataGenerationConfig()
        self.model = ModelConfig()
        self.experiment = ExperimentConfig()
        
        # File paths
        self.raw_materials_file = os.path.join(DATA_DIR, 'materials.csv')
        self.raw_users_file = os.path.join(DATA_DIR, 'users.csv')
        self.raw_interactions_file = os.path.join(DATA_DIR, 'interactions.csv')
        self.features_file = os.path.join(DATA_DIR, 'features.csv')
        
        # Model paths
        self.model_file = os.path.join(MODELS_DIR, 'ltr_model.pkl')
        self.scaler_file = os.path.join(MODELS_DIR, 'scaler.pkl')
        
        # Results paths
        self.results_file = os.path.join(RESULTS_DIR, 'experiment_results.json')
        self.feature_importance_file = os.path.join(RESULTS_DIR, 'feature_importance.csv')
        
        # Public attributes
        self.results_dir = RESULTS_DIR
        self.data_dir = DATA_DIR
        self.models_dir = MODELS_DIR

# Global config instance
config = Config()

# Interaction patterns for different user types
INTERACTION_PATTERNS = {
    'browser': {
        'events_per_session': (2, 6),
        'conversion_rate': 0.05,
        'event_probs': {
            'viewMaterial': 0.43, 
            'showMaterialPreview': 0.32, 
            'addToFavorites': 0.15, 
            'addToCart': 0.08, 
            'purchase': 0.02
        }
    },
    'focused': {
        'events_per_session': (3, 8),
        'conversion_rate': 0.15,
        'event_probs': {
            'viewMaterial': 0.3, 
            'showMaterialPreview': 0.25, 
            'addToFavorites': 0.2, 
            'addToCart': 0.15, 
            'purchase': 0.1
        }
    },
    'power_user': {
        'events_per_session': (5, 15),
        'conversion_rate': 0.25,
        'event_probs': {
            'viewMaterial': 0.2, 
            'showMaterialPreview': 0.2, 
            'addToFavorites': 0.25, 
            'addToCart': 0.2, 
            'purchase': 0.15
        }
    }
}