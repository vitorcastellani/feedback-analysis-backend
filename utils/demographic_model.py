import joblib
import os
import numpy as np
import pandas as pd
from typing import Dict, List, Optional

BASE_PATH = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_PATH, "../ml_models/sentiment_classifier.joblib")
FEATURES_PATH = os.path.join(BASE_PATH, "../ml_models/feature_columns.joblib")
STATS_PATH = os.path.join(BASE_PATH, "../ml_models/model_statistics.joblib")

# Cache variables
_model = None
_feature_columns = None
_encoders = {}
_model_stats = None
_models_loaded = False

def _load_realistic_model():
    """Load the realistic sentiment classification model"""
    global _model, _feature_columns, _encoders, _model_stats, _models_loaded
    
    if _models_loaded:
        return _model is not None
    
    required_files = [MODEL_PATH, FEATURES_PATH, STATS_PATH]
    if not all(os.path.exists(path) for path in required_files):
        print("Realistic model files not found. Please train the model first.")
        _models_loaded = True
        return False
    
    try:
        # Load main model and components
        _model = joblib.load(MODEL_PATH)
        _feature_columns = joblib.load(FEATURES_PATH)
        _model_stats = joblib.load(STATS_PATH)
        
        print(f"Loaded realistic model: {_model_stats.get('best_model_name', 'unknown')}")
        print(f"Model accuracy: {_model_stats.get('test_accuracy', 0):.3f}")
        
        # Load required encoders based on feature columns
        encoder_names = ['gender', 'age_range', 'education_level', 'country', 'state', 
                        'detected_language', 'sentiment_category']
        
        for name in encoder_names:
            encoder_path = os.path.join(BASE_PATH, f"../ml_models/{name}_encoder.joblib")
            if os.path.exists(encoder_path):
                _encoders[name] = joblib.load(encoder_path)
        
        _models_loaded = True
        return True
        
    except Exception as e:
        print(f"Error loading realistic model: {e}")
        _models_loaded = True
        return False

def predict_sentiment(
    message: str,
    gender: str = "unknown",
    age_range: str = "unknown", 
    education_level: str = "unknown",
    detected_language: str = "pt"
) -> Dict:
    """
    Predict sentiment using the realistic text-based model
    
    Args:
        message: The feedback message text
        gender: User gender (for context, if text model includes it)
        age_range: User age range (for context, if text model includes it) 
        education_level: User education level (for context, if text model includes it)
        detected_language: Detected language of the message
    
    Returns:
        Dict with prediction results and confidence
    """
    if not _load_realistic_model():
        return {"error": "realistic_model_not_available"}
    
    try:
        # Calculate text-based features from message
        word_count = len(message.split()) if message else 0
        feedback_length = len(message) if message else 0
        
        if word_count == 0:
            return {
                "error": "empty_message",
                "message": "Cannot analyze empty message"
            }
        
        # Calculate derived text features
        avg_word_length = feedback_length / word_count
        is_very_short = 1 if word_count <= 5 else 0
        is_short = 1 if word_count <= 15 else 0
        is_medium = 1 if 15 < word_count <= 50 else 0
        is_long = 1 if word_count > 50 else 0
        text_density = word_count / feedback_length if feedback_length > 0 else 0
        
        # Prepare feature vector based on model's expected features
        feature_dict = {}
        
        # Text features (most important for this model)
        feature_dict.update({
            'word_count': word_count,
            'feedback_length': feedback_length,
            'avg_word_length': avg_word_length,
            'is_very_short': is_very_short,
            'is_short': is_short,
            'is_medium': is_medium,
            'is_long': is_long,
            'text_density': text_density
        })
        
        # Demographic features (if used by the model)
        if 'gender' in _feature_columns and 'gender' in _encoders:
            try:
                feature_dict['gender'] = _encoders['gender'].transform([gender])[0]
            except (ValueError, AttributeError):
                feature_dict['gender'] = 0  # Unknown category
        
        if 'age_range' in _feature_columns and 'age_range' in _encoders:
            try:
                feature_dict['age_range'] = _encoders['age_range'].transform([age_range])[0]
            except (ValueError, AttributeError):
                feature_dict['age_range'] = 0
        
        if 'education_level' in _feature_columns and 'education_level' in _encoders:
            try:
                feature_dict['education_level'] = _encoders['education_level'].transform([education_level])[0]
            except (ValueError, AttributeError):
                feature_dict['education_level'] = 0
        
        # Language feature
        if 'detected_language' in _feature_columns and 'detected_language' in _encoders:
            try:
                feature_dict['detected_language'] = _encoders['detected_language'].transform([detected_language])[0]
            except (ValueError, AttributeError):
                feature_dict['detected_language'] = 0
        
        # Build feature vector in the correct order
        feature_vector = []
        missing_features = []
        
        for feature_name in _feature_columns:
            if feature_name in feature_dict:
                feature_vector.append(feature_dict[feature_name])
            else:
                feature_vector.append(0)  # Default value for missing features
                missing_features.append(feature_name)
        
        if missing_features:
            print(f"Warning: Missing features filled with defaults: {missing_features}")
        
        # Convert to numpy array for prediction
        X = np.array([feature_vector])
        
        # Make prediction
        prediction = _model.predict(X)[0]
        probabilities = _model.predict_proba(X)[0]
        
        # Decode prediction
        if 'sentiment_category' in _encoders:
            predicted_category = _encoders['sentiment_category'].inverse_transform([prediction])[0]
            class_names = _encoders['sentiment_category'].classes_
        else:
            predicted_category = f"class_{prediction}"
            class_names = [f"class_{i}" for i in range(len(probabilities))]
        
        # Build probability dictionary
        prob_dict = {class_names[i]: float(prob) for i, prob in enumerate(probabilities)}
        confidence = float(max(probabilities))
        
        # Get model performance info
        model_accuracy = _model_stats.get('test_accuracy', 0.0)
        baseline_accuracy = _model_stats.get('baseline_accuracy', 0.33)
        
        return {
            "predicted_category": predicted_category,
            "confidence": confidence,
            "probabilities": prob_dict,
            "text_features": {
                "word_count": word_count,
                "feedback_length": feedback_length,
                "avg_word_length": round(avg_word_length, 2),
                "text_density": round(text_density, 3),
                "length_category": "very_short" if is_very_short else 
                                "short" if is_short else 
                                "medium" if is_medium else "long"
            },
            "model_info": {
                "model_type": _model_stats.get('best_model_type', 'text'),
                "model_accuracy": round(model_accuracy, 3),
                "baseline_accuracy": round(baseline_accuracy, 3),
                "improvement_over_baseline": round(model_accuracy - baseline_accuracy, 3),
                "features_used": len(_feature_columns),
                "most_important_features": _model_stats.get('feature_importance', [])[:3] if _model_stats.get('feature_importance') else []
            }
        }
        
    except Exception as e:
        print(f"Error in realistic sentiment prediction: {e}")
        return {"error": "prediction_failed", "details": str(e)}

def predict_sentiment_demographic(
    campaign_id: int,
    gender: str = "unknown",
    age_range: str = "unknown", 
    education_level: str = "unknown",
    country: str = "unknown",
    state: str = "unknown",
    detected_language: str = "pt"
) -> Dict:
    """
    Predict sentiment using the realistic demographic-based model
    
    Args:
        campaign_id: The campaign ID
        gender: User gender
        age_range: User age range
        education_level: User education level
        country: User country
        state: User state
        detected_language: Detected language of the message
    
    Returns:
        Dict with prediction results and confidence
    """
    if not _load_realistic_model():
        return {"error": "realistic_model_not_available"}
    
    try:
        # Prepare feature dictionary based on the advanced model features
        feature_dict = {}
        
        # Basic features
        feature_dict['campaign_id'] = campaign_id
        
        # Encode categorical features
        if 'gender' in _encoders:
            try:
                feature_dict['gender'] = _encoders['gender'].transform([gender])[0]
            except (ValueError, AttributeError):
                feature_dict['gender'] = 0  # Unknown category
        
        if 'age_range' in _encoders:
            try:
                feature_dict['age_range'] = _encoders['age_range'].transform([age_range])[0]
            except (ValueError, AttributeError):
                feature_dict['age_range'] = 0
        
        if 'education_level' in _encoders:
            try:
                feature_dict['education_level'] = _encoders['education_level'].transform([education_level])[0]
            except (ValueError, AttributeError):
                feature_dict['education_level'] = 0
                
        if 'country' in _encoders:
            try:
                feature_dict['country'] = _encoders['country'].transform([country])[0]
            except (ValueError, AttributeError):
                feature_dict['country'] = 0
                
        if 'state' in _encoders:
            try:
                feature_dict['state'] = _encoders['state'].transform([state])[0]
            except (ValueError, AttributeError):
                feature_dict['state'] = 0
        
        if 'detected_language' in _encoders:
            try:
                feature_dict['detected_language_encoded'] = _encoders['detected_language'].transform([detected_language])[0]
            except (ValueError, AttributeError):
                feature_dict['detected_language_encoded'] = 0
        
        # Calculate advanced features (similar to train_realistic_model.py)
        # Age-Education interaction
        age_val = feature_dict.get('age_range', 0)
        edu_val = feature_dict.get('education_level', 0)
        gender_val = feature_dict.get('gender', 0)
        feature_dict['age_education'] = age_val * 10 + edu_val
        
        # Higher education flag
        feature_dict['is_higher_edu'] = 1 if education_level.lower() in ['bachelor', 'master', 'phd'] else 0
        
        # Campaign encoded
        feature_dict['campaign_id_encoded'] = campaign_id % 100  # Simple encoding
        
        # Complex interactions (simplified versions)
        feature_dict['age_edu_gender'] = age_val * 100 + edu_val * 10 + gender_val
        feature_dict['demographic_profile'] = hash(f"{gender}_{age_range}_{education_level}") % 1000
        feature_dict['campaign_cultural_fit'] = campaign_id * feature_dict.get('country', 0) % 100
        
        # Additional missing features
        feature_dict['cultural_context'] = feature_dict.get('country', 0) * feature_dict.get('detected_language_encoded', 0)
        feature_dict['campaign_age_fit'] = campaign_id * age_val % 50
        feature_dict['campaign_edu_fit'] = campaign_id * edu_val % 50
        feature_dict['campaign_gender_fit'] = campaign_id * gender_val % 50
        
        # Trend features (simplified - in real implementation these would come from database)
        feature_dict['education_level_group_trend'] = 0.5  # Neutral trend
        feature_dict['country_group_trend'] = 0.5  # Neutral trend
        feature_dict['age_range_group_trend'] = 0.5  # Neutral trend
        feature_dict['edu_lang_sophistication'] = edu_val * feature_dict.get('detected_language_encoded', 0)
        feature_dict['edu_cultural_level'] = edu_val * feature_dict.get('country', 0)
        
        # Build feature vector in the correct order
        feature_vector = []
        missing_features = []
        
        for feature_name in _feature_columns:
            if feature_name in feature_dict:
                feature_vector.append(feature_dict[feature_name])
            else:
                feature_vector.append(0)  # Default value for missing features
                missing_features.append(feature_name)
        
        if missing_features:
            print(f"Warning: Missing features filled with defaults: {missing_features}")
        
        # Convert to numpy array for prediction
        X = np.array([feature_vector])
        
        # Make prediction
        prediction = _model.predict(X)[0]
        probabilities = _model.predict_proba(X)[0]
        
        # Decode prediction
        if 'sentiment_category' in _encoders:
            predicted_category = _encoders['sentiment_category'].inverse_transform([prediction])[0]
            class_names = _encoders['sentiment_category'].classes_
        else:
            predicted_category = f"class_{prediction}"
            class_names = [f"class_{i}" for i in range(len(probabilities))]
        
        # Build probability dictionary
        prob_dict = {class_names[i]: float(prob) for i, prob in enumerate(probabilities)}
        confidence = float(max(probabilities))
        
        # Get model performance info
        model_accuracy = _model_stats.get('test_accuracy', 0.0)
        baseline_accuracy = _model_stats.get('baseline_accuracy', 0.33)
        
        return {
            "predicted_category": predicted_category,
            "confidence": confidence,
            "probabilities": prob_dict,
            "demographic_features": {
                "campaign_id": campaign_id,
                "gender": gender,
                "age_range": age_range,
                "education_level": education_level,
                "country": country,
                "state": state,
                "detected_language": detected_language,
                "is_higher_edu": feature_dict.get('is_higher_edu', 0)
            },
            "model_info": {
                "model_type": _model_stats.get('best_model_type', 'demographic'),
                "model_accuracy": round(model_accuracy, 3),
                "baseline_accuracy": round(baseline_accuracy, 3),
                "improvement_over_baseline": round(model_accuracy - baseline_accuracy, 3),
                "features_used": len(_feature_columns),
                "most_important_features": _model_stats.get('feature_importance', [])[:5] if _model_stats.get('feature_importance') else []
            }
        }
        
    except Exception as e:
        print(f"Error in demographic sentiment prediction: {e}")
        return {"error": "prediction_failed", "details": str(e)}

def get_model_performance() -> Dict:
    """Get detailed information about the realistic model's performance"""
    if not _load_realistic_model():
        return {"error": "model_not_available"}
    
    return {
        "model_available": True,
        "model_name": _model_stats.get('best_model_name', 'unknown'),
        "model_type": _model_stats.get('best_model_type', 'unknown'),
        "accuracy": _model_stats.get('test_accuracy', 0.0),
        "baseline_accuracy": _model_stats.get('baseline_accuracy', 0.33),
        "improvement": _model_stats.get('improvement_over_baseline', 0.0),
        "total_samples": _model_stats.get('total_samples', 0),
        "balanced_samples": _model_stats.get('balanced_samples', 0),
        "feature_count": len(_feature_columns) if _feature_columns else 0,
        "target_classes": _model_stats.get('target_names', []),
        "class_distribution": _model_stats.get('class_distribution', {}),
        "training_date": _model_stats.get('training_timestamp', 'unknown'),
        "purpose": _model_stats.get('model_purpose', 'Realistic sentiment classification'),
        "notes": _model_stats.get('performance_notes', 'Conservative model avoiding data leakage')
    }

def realistic_model_exists() -> bool:
    """Check if the realistic model exists and is loadable"""
    required_files = [MODEL_PATH, FEATURES_PATH, STATS_PATH]
    return all(os.path.exists(path) for path in required_files)

def compare_with_vader(message: str, vader_result: Dict, **kwargs) -> Dict:
    """Compare realistic model prediction with VADER analysis"""
    
    realistic_result = predict_sentiment(message, **kwargs)
    
    if "error" in realistic_result:
        return realistic_result
    
    return {
        "message_stats": realistic_result["text_features"],
        "vader_prediction": {
            "category": vader_result.get("sentiment_category", "unknown"),
            "score": vader_result.get("sentiment_score", 0.0),
            "confidence": abs(vader_result.get("sentiment_score", 0.0))
        },
        "ml_prediction": {
            "category": realistic_result["predicted_category"],
            "confidence": realistic_result["confidence"],
            "probabilities": realistic_result["probabilities"]
        },
        "agreement": {
            "categories_match": vader_result.get("sentiment_category") == realistic_result["predicted_category"],
            "both_positive": vader_result.get("sentiment_category") == "positive" and realistic_result["predicted_category"] == "positive",
            "both_negative": vader_result.get("sentiment_category") == "negative" and realistic_result["predicted_category"] == "negative",
            "both_neutral": vader_result.get("sentiment_category") == "neutral" and realistic_result["predicted_category"] == "neutral"
        },
        "model_info": realistic_result["model_info"]
    }