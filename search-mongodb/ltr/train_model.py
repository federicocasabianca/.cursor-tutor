#!/usr/bin/env python3
"""
Script to train the Learning-to-Rank model
"""

import sys
import os
import pandas as pd
from typing import List, Tuple, Dict, Any

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .data_generator import TrainingDataGenerator
from .feature_engineering import FeatureEngineer
from .model import LTRModel


def train_ltr_model(training_data_file: str = 'training_data.json', 
                   min_queries: int = 50,
                   test_size: float = 0.2,
                   random_state: int = 42):
    """
    Train the Learning-to-Rank model
    
    Args:
        training_data_file: Path to training data file
        min_queries: Minimum number of queries to process if generating new data
        test_size: Fraction of data to use for testing
        random_state: Random seed for reproducibility
    """
    print("=" * 60)
    print("LEARNING-TO-RANK MODEL TRAINING")
    print("=" * 60)
    
    # Initialize components
    generator = TrainingDataGenerator(max_documents_per_query=100)
    feature_engineer = FeatureEngineer()
    model = LTRModel()
    
    # Check if training data exists, otherwise generate it
    training_data_path = f'data/{training_data_file}'
    if os.path.exists(training_data_path):
        print(f"Loading existing training data from {training_data_path}")
        training_data = generator.load_training_data(training_data_file)
    else:
        print("No existing training data found. Generating new training data...")
        training_data = generator.generate_training_data(min_queries=min_queries)
        generator.save_training_data(training_data, training_data_file)
    
    if not training_data:
        print("Error: No training data available!")
        return
    
    print(f"\nTraining data summary:")
    print(f"  Total examples: {len(training_data)}")
    
    # Analyze label distribution
    labels = [label for _, _, _, label in training_data]
    label_counts = pd.Series(labels).value_counts().sort_index()
    print(f"  Label distribution:")
    for label, count in label_counts.items():
        print(f"    Label {label}: {count} examples ({count/len(labels)*100:.1f}%)")
    
    # Create training DataFrame
    print("\nCreating feature matrix...")
    training_df = feature_engineer.create_training_data(training_data)
    
    print(f"Feature matrix shape: {training_df.shape}")
    print(f"Features: {feature_engineer.feature_names}")
    
    # Train the model
    print("\nStarting model training...")
    model.train(training_df, test_size=test_size, random_state=random_state)
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Model saved to: {model.model_path}")
    print(f"Feature importance saved to: models/feature_importance.csv")
    print(f"Training data saved to: data/{training_data_file}")
    
    return model


def main():
    """Main function to run model training"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train Learning-to-Rank model')
    parser.add_argument('--training-data', default='training_data.json',
                       help='Training data file name (default: training_data.json)')
    parser.add_argument('--min-queries', type=int, default=50,
                       help='Minimum number of queries to process (default: 50)')
    parser.add_argument('--test-size', type=float, default=0.2,
                       help='Fraction of data for testing (default: 0.2)')
    parser.add_argument('--random-state', type=int, default=42,
                       help='Random seed (default: 42)')
    
    args = parser.parse_args()
    
    try:
        model = train_ltr_model(
            training_data_file=args.training_data,
            min_queries=args.min_queries,
            test_size=args.test_size,
            random_state=args.random_state
        )
        
        if model:
            print("\nModel is ready for use!")
            print("You can now use the ranking service in your search application.")
        
    except Exception as e:
        print(f"Error during training: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 