# Learning-to-Rank (LTR) System

This module implements a Learning-to-Rank system using XGBoost to improve search result ranking beyond MongoDB's basic text search scoring.

## Overview

The LTR system consists of several components:

1. **Feature Engineering** (`feature_engineering.py`) - Extracts features from query-document pairs
2. **Data Generator** (`data_generator.py`) - Creates training data from search queries and documents
3. **LTR Model** (`model.py`) - XGBoost-based ranking model
4. **Ranking Service** (`ranking_service.py`) - Integrates with the search system
5. **Training Script** (`train_model.py`) - Trains the model offline
6. **Test Script** (`test_ranking.py`) - Tests the system

## Features

The current feature set includes:

- `mongodb_score` - Original MongoDB search score
- `title_length` - Length of document title
- `log_price` - Log-transformed price (log(1 + price))
- `recency_days` - Days since document creation
- `bestseller_rating` - Document's bestseller rating
- `is_free` - Boolean indicating if document is free
- `is_bundle` - Boolean indicating if document is a bundle

## Quick Start

### 1. Install Dependencies

Make sure you have the required packages installed:

```bash
pip install -r requirements.txt
```

### 2. Generate Training Data

Generate training data from existing search queries:

```bash
cd ltr
python data_generator.py
```

This will:
- Load search queries from MongoDB
- Simulate search results for each query
- Generate synthetic labels based on heuristics
- Save training data to `data/training_data.json`

### 3. Train the Model

Train the LTR model using the generated data:

```bash
python train_model.py --min-queries 50 --test-size 0.2
```

This will:
- Load or generate training data
- Split data into training and test sets
- Train an XGBoost model
- Evaluate model performance
- Save the model to `models/ltr_model.pkl`
- Save feature importance to `models/feature_importance.csv`

### 4. Test the System

Test the ranking system:

```bash
python test_ranking.py
```

This will:
- Test feature extraction
- Test the ranking service with a sample query
- Show before/after ranking comparison

## Usage in Application

The LTR system is automatically integrated into the search service. When you perform a search:

1. MongoDB returns initial results with scores
2. The LTR model predicts new relevance scores
3. Results are re-ranked based on LTR scores
4. Both original MongoDB scores and new LTR scores are preserved

### API Response

The search API now includes ranking information:

```json
{
  "results": [...],
  "total": 100,
  "ranking_info": {
    "model_loaded": true,
    "model_path": "models/ltr_model.pkl",
    "features": ["mongodb_score", "title_length", ...]
  }
}
```

## Model Training Details

### Training Data Generation

The system generates synthetic training data using heuristics:

1. **Base Relevance**: Based on search query frequency
2. **Title Matching**: Boost for exact title matches
3. **Content Quality**: Boost for free materials and high ratings
4. **Recency**: Penalty for very old content

### Model Configuration

The XGBoost model uses:
- **Objective**: `reg:squarederror` (pointwise ranking)
- **Trees**: 100 estimators
- **Depth**: 6 levels
- **Learning Rate**: 0.1
- **Early Stopping**: 10 rounds

### Evaluation Metrics

The model is evaluated using:
- **MSE**: Mean Squared Error
- **RMSE**: Root Mean Squared Error
- **Feature Importance**: XGBoost's built-in importance scores

## File Structure

```
ltr/
├── __init__.py
├── README.md
├── feature_engineering.py    # Feature extraction
├── data_generator.py         # Training data generation
├── model.py                  # XGBoost LTR model
├── ranking_service.py        # Integration service
├── train_model.py           # Training script
├── test_ranking.py          # Test script
├── data/                    # Training data
│   └── training_data.json
└── models/                  # Trained models
    ├── ltr_model.pkl
    └── feature_importance.csv
```

## Customization

### Adding New Features

To add new features:

1. Update `FeatureEngineer.feature_names` in `feature_engineering.py`
2. Implement feature extraction in `extract_features()` method
3. Retrain the model

### Modifying Label Generation

To improve label quality:

1. Update `generate_synthetic_labels()` in `feature_engineering.py`
2. Consider using actual user interaction data (clicks, purchases, etc.)
3. Implement more sophisticated relevance scoring

### Model Parameters

To tune the model:

1. Modify XGBoost parameters in `LTRModel.train()`
2. Experiment with different objectives (pairwise, listwise)
3. Adjust hyperparameters based on validation performance

## Troubleshooting

### Common Issues

1. **No training data**: Ensure search queries exist in MongoDB
2. **Model not loading**: Check if `models/ltr_model.pkl` exists
3. **Import errors**: Verify all dependencies are installed
4. **Memory issues**: Reduce `max_documents_per_query` in data generation

### Debug Mode

Enable debug output by setting environment variable:

```bash
export LTR_DEBUG=1
```

## Performance Considerations

- **Training**: Offline process, can be run periodically
- **Inference**: Fast prediction using pre-trained model
- **Memory**: Model size ~1-10MB depending on features
- **Latency**: Minimal overhead (~1-5ms per query)

## Future Improvements

1. **Real User Feedback**: Use actual click/purchase data
2. **Advanced Features**: Query-document interaction features
3. **Ensemble Methods**: Combine multiple ranking models
4. **Online Learning**: Incremental model updates
5. **A/B Testing**: Compare different ranking strategies 