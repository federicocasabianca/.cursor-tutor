# Eduki Learning to Rank (LTR) System

A comprehensive Learning to Rank implementation for the Eduki teaching materials marketplace, designed to improve material discovery and recommendations for teachers.

## 🎯 Project Overview

This project implements a pointwise Learning to Rank system that predicts relevance scores for user-material pairs based on realistic user behavior patterns and material characteristics from the Eduki platform.

### Key Features

- **Realistic Data Simulation**: Generates synthetic data based on actual Eduki taxonomy and user behavior patterns
- **Comprehensive Feature Engineering**: Creates 50+ features from user profiles, material characteristics, and interaction patterns
- **XGBoost-based LTR Model**: Implements pointwise ranking with regression objective
- **Extensive Evaluation**: Includes RMSE, R², NDCG@k, and cross-validation metrics
- **Recommendation Engine**: Generates top-k recommendations for users
- **Visualization Suite**: Comprehensive plots for model analysis and feature importance

## 📁 Project Structure

```
LTR-simulation/
├── config.py                 # Configuration management
├── data_generator.py          # Synthetic data generation
├── feature_engineering.py     # Feature creation pipeline
├── ltr_model.py              # LTR model training & evaluation
├── main_experiment.py        # Complete experiment pipeline
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── data/                     # Generated datasets
│   ├── materials.csv
│   ├── users.csv
│   ├── interactions.csv
│   └── features.csv
├── results/                  # Experiment outputs
│   ├── models/              # Trained models
│   ├── experiment_results.json
│   ├── feature_importance.csv
│   └── experiment.log
└── notebooks/               # Jupyter notebooks for analysis
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd LTR-simulation

# Install dependencies
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

### 2. Run Complete Experiment

```bash
# Run with default settings (5K materials, 1K users, 50K interactions)
python main_experiment.py

# Run with custom parameters
python main_experiment.py --materials 10000 --users 2000 --interactions 100000

# Force regenerate data and features
python main_experiment.py --force-data --force-features
```

### 3. Run Individual Components

```bash
# Generate data only
python data_generator.py

# Create features only (requires existing data)
python feature_engineering.py

# Train model only (requires existing features)
python ltr_model.py
```

## 📊 Data Generation

The system generates realistic synthetic data based on Eduki's actual taxonomy:

### Materials
- **Subjects**: Mathematik, Deutsch, Englisch, Kunst, Fachunterricht
- **Material Types**: Arbeitsblätter, Unterrichtsreihen, Stundenentwürfe, etc.
- **Grade Levels**: 1. Klasse through 13. Klasse
- **Author Categories**: Eggs → Cub → Bear → Dragon → Innovators (performance tiers)
- **Content Types**: standalone, hybrid, interactive

### Users (Teachers)
- **Teaching Preferences**: Primary and secondary subjects, grade levels
- **Behavioral Profiles**: browser, focused, power_user engagement styles
- **Price Sensitivity**: low, medium, high categories
- **Experience Levels**: novice, experienced, expert

### Interactions
- **Event Types**: viewMaterial, showMaterialPreview, addToFavorites, addToCart, freeDownload, purchase
- **Relevance Scoring**: Weighted by event importance (view=1, purchase=5)
- **Realistic Patterns**: Subject/grade matching, price sensitivity effects

## 🔧 Feature Engineering

The system creates comprehensive features across multiple categories:

### Material Features (15+ features)
- Price, bestseller rating, engagement score, page count
- Subject, material type, content type (one-hot encoded)
- Author category, bundle status, creation recency

### User Features (10+ features)
- Registration tenure, purchase frequency, experience level
- Price sensitivity, engagement style (one-hot encoded)
- Primary subject preferences

### Interaction Features (15+ features)
- Subject matching (primary/secondary)
- Grade level overlap counting
- Price-sensitivity alignment
- Material type preferences
- Quality-experience matching

### Temporal Features (10+ features)
- Time of day, day of week patterns
- Material age at interaction
- User tenure effects
- Seasonal considerations

### Context Features (5+ features)
- Device type (desktop/mobile/tablet)
- Position in search results
- Cross-feature interactions

## 🤖 Model Architecture

### Pointwise LTR with XGBoost
- **Objective**: Regression (predicts relevance scores)
- **Features**: 50+ engineered features
- **Evaluation**: RMSE for regression + NDCG@k for ranking
- **Validation**: Train/Val/Test split + Cross-validation

### Model Configuration
```python
XGBRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    objective='reg:squarederror'
)
```

## 📈 Evaluation Metrics

### Regression Metrics
- **RMSE**: Root Mean Square Error
- **MAE**: Mean Absolute Error  
- **R²**: Coefficient of determination

### Ranking Metrics
- **NDCG@5, @10, @20**: Normalized Discounted Cumulative Gain
- **Cross-Validation**: 5-fold CV with RMSE

### Business Metrics
- Feature importance analysis
- Prediction distribution analysis
- User-level recommendation quality

## 🎯 Results Interpretation

### Expected Performance
- **Test RMSE**: ~0.3-0.5 (relevance scores 0-5 range)
- **Test R²**: ~0.6-0.8 (good predictive power)
- **NDCG@5**: ~0.7-0.9 (excellent ranking quality)
- **NDCG@10**: ~0.8-0.95 (very good ranking quality)

### Key Feature Insights
Top features typically include:
1. `subject_match_primary` - Primary subject alignment
2. `grade_overlap_count` - Grade level matching
3. `material_bestseller_rating` - Material popularity
4. `price_affordable_for_user` - Price sensitivity matching
5. `user_engagement_power_user` - User engagement style

## 🔄 Extending the System

### Adding New Features
1. Modify `feature_engineering.py` in `_create_*_features()` methods
2. Update feature column lists in `prepare_data()`
3. Test with ablation studies

### Alternative Models
```python
# LightGBM alternative
from lightgbm import LGBMRegressor

# Pairwise ranking
from xgboost import XGBRanker

# Neural networks
from sklearn.neural_network import MLPRegressor
```

### Advanced Techniques
- **Hyperparameter Tuning**: Use Optuna or GridSearchCV
- **Feature Selection**: RFE, LASSO, or importance-based
- **Ensemble Methods**: Combine multiple models
- **Online Learning**: Incremental model updates

## 🛠️ Configuration

All parameters are centrally managed in `config.py`:

```python
# Data generation
n_materials = 5000
n_users = 1000
n_interactions = 50000

# Model parameters
n_estimators = 100
max_depth = 6
learning_rate = 0.1

# Evaluation
ndcg_k_values = [5, 10, 20]
```

## 📝 Logging and Monitoring

- **Experiment Logs**: Saved to `results/experiment.log`
- **Model Metrics**: JSON format in `results/experiment_results.json`
- **Feature Importance**: CSV format for analysis
- **Model Artifacts**: Saved with joblib for reuse

## 🚦 Troubleshooting

### Common Issues

1. **Memory Errors**: Reduce dataset size or use batch processing
2. **Feature Scaling Issues**: Check for missing/infinite values
3. **NDCG Calculation Fails**: Ensure users have multiple interactions
4. **Model Convergence**: Adjust learning rate or max_depth

### Performance Tuning

- **Speed**: Reduce n_estimators, use early stopping
- **Memory**: Process data in batches, reduce feature count  
- **Accuracy**: Increase n_estimators, tune hyperparameters

## 📚 References

- **XGBoost Documentation**: https://xgboost.readthedocs.io/
- **Learning to Rank**: Liu, T.Y. "Learning to Rank for Information Retrieval"
- **NDCG Metric**: Järvelin & Kekäläinen, ACM TOIS 2002
- **Feature Engineering**: Zheng & Casari, "Feature Engineering for Machine Learning"

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

**Built for Eduki's personalization strategy - helping teachers find the perfect materials for their students! 🎓**

## 🔍 Command-Line Search & Ranking

You can search for materials and get them ranked for a specific user using the trained LTR model.

### Usage

```bash
python search_and_rank.py --user <USER_ID> --keyword <SEARCH_KEYWORD> [--topk <N>]
```

- `<USER_ID>`: The user ID (e.g., user_000123)
- `<SEARCH_KEYWORD>`: The keyword to search for in material titles, subjects, or subcategories
- `--topk <N>`: (Optional) Number of top results to show (default: 10)

### Example

```bash
python search_and_rank.py --user user_000123 --keyword Mathematik --topk 5
```

This will print the top 5 materials matching 'Mathematik' for user_000123, ranked by the LTR model.