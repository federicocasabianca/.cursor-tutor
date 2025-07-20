#!/usr/bin/env python3
"""
Complete Learning-to-Rank pipeline runner
"""

import sys
import os
import argparse

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ltr.data_generator import TrainingDataGenerator
from ltr.train_model import train_ltr_model
from ltr.test_ranking import test_ranking_service, test_feature_extraction


def run_complete_pipeline(min_queries: int = 50, 
                         test_size: float = 0.2,
                         skip_data_generation: bool = False,
                         skip_training: bool = False,
                         skip_testing: bool = False):
    """
    Run the complete LTR pipeline
    
    Args:
        min_queries: Minimum number of queries to process
        test_size: Fraction of data for testing
        skip_data_generation: Skip data generation step
        skip_training: Skip model training step
        skip_testing: Skip testing step
    """
    print("=" * 80)
    print("LEARNING-TO-RANK COMPLETE PIPELINE")
    print("=" * 80)
    
    # Step 1: Generate Training Data
    if not skip_data_generation:
        print("\n" + "="*60)
        print("STEP 1: GENERATING TRAINING DATA")
        print("="*60)
        
        try:
            generator = TrainingDataGenerator(max_documents_per_query=100)
            training_data = generator.generate_training_data(min_queries=min_queries)
            
            if training_data:
                generator.save_training_data(training_data)
                print(f"✓ Generated {len(training_data)} training examples")
            else:
                print("✗ No training data generated!")
                return
                
        except Exception as e:
            print(f"✗ Error generating training data: {e}")
            return
    else:
        print("\n" + "="*60)
        print("STEP 1: SKIPPING DATA GENERATION")
        print("="*60)
        print("Using existing training data...")
    
    # Step 2: Train Model
    if not skip_training:
        print("\n" + "="*60)
        print("STEP 2: TRAINING LTR MODEL")
        print("="*60)
        
        try:
            model = train_ltr_model(
                training_data_file='training_data.json',
                min_queries=min_queries,
                test_size=test_size,
                random_state=42
            )
            
            if model:
                print("✓ Model training completed successfully")
            else:
                print("✗ Model training failed!")
                return
                
        except Exception as e:
            print(f"✗ Error training model: {e}")
            return
    else:
        print("\n" + "="*60)
        print("STEP 2: SKIPPING MODEL TRAINING")
        print("="*60)
        print("Using existing model...")
    
    # Step 3: Test System
    if not skip_testing:
        print("\n" + "="*60)
        print("STEP 3: TESTING LTR SYSTEM")
        print("="*60)
        
        try:
            # Test feature extraction
            test_feature_extraction()
            
            # Test ranking service
            test_ranking_service()
            
            print("✓ System testing completed successfully")
            
        except Exception as e:
            print(f"✗ Error testing system: {e}")
            return
    else:
        print("\n" + "="*60)
        print("STEP 3: SKIPPING SYSTEM TESTING")
        print("="*60)
        print("Skipping tests...")
    
    print("\n" + "="*80)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*80)
    print("Your Learning-to-Rank system is now ready to use!")
    print("\nNext steps:")
    print("1. Start your Flask application: python app.py")
    print("2. Perform searches to see LTR ranking in action")
    print("3. Monitor the ranking_info in API responses")


def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(description='Run complete LTR pipeline')
    parser.add_argument('--min-queries', type=int, default=50,
                       help='Minimum number of queries to process (default: 50)')
    parser.add_argument('--test-size', type=float, default=0.2,
                       help='Fraction of data for testing (default: 0.2)')
    parser.add_argument('--skip-data-generation', action='store_true',
                       help='Skip data generation step')
    parser.add_argument('--skip-training', action='store_true',
                       help='Skip model training step')
    parser.add_argument('--skip-testing', action='store_true',
                       help='Skip testing step')
    parser.add_argument('--data-only', action='store_true',
                       help='Only generate training data')
    parser.add_argument('--train-only', action='store_true',
                       help='Only train the model (assumes data exists)')
    parser.add_argument('--test-only', action='store_true',
                       help='Only test the system (assumes model exists)')
    
    args = parser.parse_args()
    
    # Handle convenience flags
    if args.data_only:
        args.skip_training = True
        args.skip_testing = True
    elif args.train_only:
        args.skip_data_generation = True
        args.skip_testing = True
    elif args.test_only:
        args.skip_data_generation = True
        args.skip_training = True
    
    try:
        run_complete_pipeline(
            min_queries=args.min_queries,
            test_size=args.test_size,
            skip_data_generation=args.skip_data_generation,
            skip_training=args.skip_training,
            skip_testing=args.skip_testing
        )
    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nPipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 