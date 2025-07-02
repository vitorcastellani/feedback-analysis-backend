## 🧠 ML Model Training (`ml_training/`) & Smart Prediction System (`utils/`)

This system contains scripts for training machine learning models and an intelligent prediction system that automatically manages global and campaign-specific models.

### 📄 ML Training Scripts (`ml_training/`)

- **`export_feedback_dataset.py`**  
  Extracts hierarchical feedback data from the database including `campaign_id` and demographic features. Exports data as CSV file for model training with campaign-specific information.  
  **Usage example:**
  ```sh
  python -m ml_training.export_feedback_dataset
  ```
  **Output:** `ml_data/hierarchical_feedback_dataset.csv`

- **`train_demographic_model.py`**  
  Trains a machine learning model (Gaussian Naive Bayes) using demographic features: `gender`, `age_range`, `education_level`, `country`, and `state` to predict sentiment category. Features automatic handling of small datasets and imbalanced classes.  
  **Usage example:**
  ```sh
  python -m ml_training.train_demographic_model
  ```
  **Input:** `ml_data/hierarchical_feedback_dataset.csv`  
  **Output:** Global model and encoders saved to `ml_models/` directory

- **`generate_sample_data.py`**  
  Generates realistic sample feedback data directly into the database. Creates thousands of feedback entries with demographic diversity and realistic sentiment patterns. Essential for testing and development.  
  **Usage example:**
  ```sh
  python -m ml_training.generate_sample_data
  ```

### 🤖 Smart Prediction System (`utils/`)

#### Core ML Components:

- **`auto_train.py`**  
  **Automatic Model Training Engine** - Automatically exports data from database and trains the global demographic model when needed. Handles edge cases like small datasets and class imbalances.
  
- **`demographic_model.py`**  
  **Global Model Manager** - Loads and manages the global demographic sentiment model. Features lazy loading and automatic training when model files don't exist.

- **`model_manager.py`**  
  **Campaign Model Manager** - Manages campaign-specific models with automatic training, retraining based on new data, and intelligent fallback to global model.

- **`smart_model.py`**  
  **Intelligent Prediction Router** - Chooses between campaign-specific and global models automatically. Provides unified interface for sentiment prediction.

#### Support Components:

- **`sentiment_analysis.py`**  
  Advanced sentiment analysis using VADER with language detection, translation, and text preprocessing.

- **`common.py`**  
  Utility functions including short code generation for campaigns.

### 🎯 Smart Model Features

#### Hierarchical Model System:
- **Global Model:** Trained on all available data across campaigns
- **Campaign Models:** Trained specifically for individual campaigns when sufficient data exists
- **Automatic Fallback:** Uses global model when campaign-specific model unavailable

#### Intelligent Training:
- **Auto-Detection:** Automatically detects when models need training or retraining
- **Data Validation:** Ensures sufficient data quality before training
- **Incremental Updates:** Retrains models when new data exceeds threshold (50 feedbacks)
- **Graceful Degradation:** Handles missing models, insufficient data, and training failures

#### Smart Prediction Logic:
```python
# The system automatically:
# 1. Checks if campaign-specific model exists
# 2. Trains new model if data is sufficient
# 3. Retrains if model is outdated
# 4. Falls back to global model when needed
# 5. Creates global model if it doesn't exist
```

### 🔁 Automated Workflow

#### On First API Call:
1. **Check Global Model** - If missing, automatically train using all available data
2. **Check Campaign Model** - If missing and sufficient data exists (20+ samples), train campaign-specific model
3. **Predict** - Use best available model (campaign-specific preferred, global fallback)

#### On Subsequent Calls:
1. **Check Freshness** - If 50+ new feedbacks since last training, retrain campaign model
2. **Predict** - Use most appropriate model
3. **Cache** - Keep models loaded in memory for performance

#### Model Files Generated:
- **Global Model:**
  - `demographic_sentiment_model.joblib` - Main classification model
  - `gender_encoder.joblib`, `age_encoder.joblib`, etc. - Feature encoders
  - `label_encoder.joblib` - Sentiment category encoder

- **Campaign Models:**
  - `campaign_{id}_model.joblib` - Campaign-specific model and encoders
  - `campaign_{id}_metadata.joblib` - Training metadata and timestamps

### 🚀 API Integration

The system integrates seamlessly with the API:

```python
# Endpoint: POST /feedback/classify-demographic
# Automatically handles:
# - Model availability checking
# - Auto-training when needed
# - Campaign vs global model selection
# - Graceful error handling

Response format:
{
  "campaign_id": 1,
  "predictions": {
    "global_model": "positive",
    "campaign_model": "neutral"
  },
  "model_status": {
    "campaign_model_exists": true,
    "campaign_model_trained": false,
    "campaign_model_retrained": false,
    "global_model_exists": true,
    "message": "Using existing campaign model"
  }
}
```

### 📊 Model Performance Features

#### Data Quality Handling:
- **Minimum Samples:** Requires 20+ samples for campaign models, 5+ for global
- **Class Balance:** Handles imbalanced datasets with appropriate train/test splits
- **Missing Values:** Gracefully handles unknown demographic values
- **Edge Cases:** Manages single-class datasets and insufficient data scenarios

#### Training Intelligence:
- **Demographic Patterns:** Learns that higher education correlates with positive sentiment
- **Age Influence:** Captures that younger users tend to be more optimistic
- **Geographic Bias:** Accounts for cultural differences in sentiment expression
- **Temporal Awareness:** Automatically retrains as sentiment patterns evolve

### 📌 Development Notes

- **Zero Configuration:** The system works out-of-the-box without manual model training
- **Production Ready:** Handles all edge cases and provides detailed status reporting
- **Scalable:** Efficiently manages multiple campaign models with metadata tracking
- **Robust:** Comprehensive error handling and graceful degradation
- **Fast:** In-memory model caching for optimal performance

### 🏁 Quick Start

```sh
# 1. Generate sample data (optional, for testing)
python -m ml_training.generate_sample_data

# 2. Start the API - everything else is automatic!
python app.py

# 3. Make a prediction request - models will be created automatically
curl -X POST http://localhost:5000/api/feedback/classify-demographic \
  -H "Content-Type: application/json" \
  -d '{"feedback_id": 1}'
```

The system will automatically:
- ✅ Check for global model (create if missing)
- ✅ Check for campaign model (create if sufficient data)
- ✅ Return predictions from both models
- ✅ Provide detailed status information

**No manual training required!** The ML system is fully automated and production-ready.