# ML Models Directory

This directory contains trained machine learning models and associated files used by the Feedback Analysis API for sentiment classification.

## Directory Contents

### **Main Model Files**
- **`sentiment_classifier.joblib`** - Primary Random Forest sentiment classification model
- **`feature_columns.joblib`** - List of feature columns used by the model
- **`model_statistics.joblib`** - Comprehensive model metadata and performance statistics

### **Label Encoders**
- **`age_range_encoder.joblib`** - Encoder for age ranges: `['18-24', '25-34', '35-44', '45-54', '55-64', '65+', 'other']`
- **`country_encoder.joblib`** - Encoder for 25 countries including Brazil, US, UK, etc.
- **`detected_language_encoder.joblib`** - Encoder for detected languages
- **`education_level_encoder.joblib`** - Encoder for education levels: `['bachelor', 'elementary', 'highschool', 'master', 'other', 'phd']`
- **`gender_encoder.joblib`** - Encoder for gender: `['female', 'male', 'other', 'prefer not to say']`
- **`sentiment_category_encoder.joblib`** - Encoder for sentiment classes: `['negative', 'neutral', 'positive']`
- **`state_encoder.joblib`** - Encoder for Brazilian states: `['BA', 'DF', 'MG', 'Other', 'PE', 'RJ', 'RS', 'SP']`

## **Current Model Specifications**

### **Model Type:** Text-Based Random Forest Classifier
- **Algorithm:** RandomForestClassifier
- **Training Approach:** Conservative, avoiding data leakage
- **Performance:** 69.6% test accuracy (33% improvement over baseline)
- **Cross-Validation:** 75.4% ± 1.4%

### **Features Used (12 total):**
1. **Demographic Context (3 features):**
   - `gender` - User gender
   - `age_range` - User age range  
   - `education_level` - User education level

2. **Text Analysis Features (9 features):**
   - `word_count` - Number of words in feedback
   - `feedback_length` - Character count of feedback
   - `avg_word_length` - Average characters per word
   - `is_very_short` - Binary flag for very short texts (≤5 words)
   - `is_short` - Binary flag for short texts (≤15 words)
   - `is_medium` - Binary flag for medium texts (16-50 words)
   - `is_long` - Binary flag for long texts (>50 words)
   - `text_density` - Word density (words per character)
   - `detected_language` - Language of the feedback

### **Feature Importance Ranking:**
1. **`feedback_length`** (26.4%) - Text length is highly predictive
2. **`text_density`** (21.7%) - Word density indicates writing style
3. **`avg_word_length`** (20.2%) - Longer words suggest formal language
4. **`detected_language`** (16.5%) - Language affects sentiment expression
5. **`word_count`** (8.1%) - Number of words provides context
6. **`is_very_short`** (4.8%) - Very short texts have distinct patterns
7. **Other features** (<1% each) - Demographic context

## 🚀 **Usage in API**

### **Available Functions:**
- **`predict_sentiment_realistic()`** - Main prediction function
- **`get_model_performance()`** - Model statistics and metadata
- **`compare_with_vader()`** - Compare ML prediction with VADER analysis
- **`realistic_model_exists()`** - Check if model files are available

## 🔄 **Retraining Process**

To retrain the model with new data:

1. **Export fresh dataset:**
   ```bash
   python -m ml_training.export_feedback_dataset
   ```

2. **Train realistic models:**
   ```bash
   python -m ml_training.train_realistic_model
   ```

3. **Verify model files:**
   - Check that all `.joblib` files are updated
   - Verify performance in `model_statistics.joblib`
   - Test predictions with `utils.realistic_model`
