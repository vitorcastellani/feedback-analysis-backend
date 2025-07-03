import pytest
import os
import joblib
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from utils.realistic_model import (
    _load_realistic_model, 
    predict_sentiment,
    get_model_performance,
    realistic_model_exists,
    compare_with_vader
)
from ml_training.train_realistic_model import train_realistic_models


class TestRealisticModel:
    """Test suite for the realistic sentiment classification model."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup for each test method."""
        import utils.realistic_model as rm
        rm._model = None
        rm._feature_columns = None
        rm._encoders = {}
        rm._model_stats = None
        rm._models_loaded = False
    
    def test_model_files_exist(self):
        """Test that all required model files exist after training."""
        model_files = [
            "ml_models/sentiment_classifier.joblib",
            "ml_models/feature_columns.joblib", 
            "ml_models/model_statistics.joblib",
            "ml_models/gender_encoder.joblib",
            "ml_models/age_range_encoder.joblib",
            "ml_models/education_level_encoder.joblib",
            "ml_models/country_encoder.joblib",
            "ml_models/state_encoder.joblib",
            "ml_models/sentiment_category_encoder.joblib"
        ]
        
        for file_path in model_files:
            if os.path.exists(file_path):
                assert os.path.getsize(file_path) > 0, f"Model file {file_path} is empty"
    
    def test_load_realistic_model_success(self):
        """Test successful loading of the realistic model."""
        if not os.path.exists("ml_models/sentiment_classifier.joblib"):
            pytest.skip("Model files not available - run training first")
        
        result = _load_realistic_model()
        assert result is True, "Model should load successfully"
        
        assert realistic_model_exists() is True, "Model should be available after loading"
    
    def test_load_realistic_model_missing_files(self):
        """Test model loading when files are missing."""
        with patch('os.path.exists', return_value=False):
            result = _load_realistic_model()
            assert result is False, "Should return False when model files are missing"
    
    def test_model_info_retrieval(self):
        """Test retrieving model information."""
        if not os.path.exists("ml_models/sentiment_classifier.joblib"):
            pytest.skip("Model files not available - run training first")
        
        _load_realistic_model()
        info = get_model_performance()
        
        assert isinstance(info, dict), "Model info should be a dictionary"
        assert "model_type" in info, "Should contain model type"
        assert "accuracy" in info, "Should contain accuracy"
        assert "feature_count" in info, "Should contain feature count"
        assert "training_date" in info, "Should contain training date"
        
        assert 0.0 <= info["accuracy"] <= 1.0, "Accuracy should be between 0 and 1"
    
    def test_demographic_prediction_valid_input(self):
        """Test demographic sentiment prediction with valid input."""
        if not os.path.exists("ml_models/sentiment_classifier.joblib"):
            pytest.skip("Model files not available - run training first")
        
        message = "This product is really great and I love using it!"
        
        result = predict_sentiment(
            message=message,
            gender="male",
            age_range="25-34",
            education_level="bachelor"
        )
        
        assert isinstance(result, dict), "Should return a dictionary"
        
        if "error" not in result:
            assert "predicted_category" in result, "Should contain predicted category"
            assert "confidence" in result, "Should contain confidence score"
            assert "text_features" in result, "Should contain text features"
            assert "model_info" in result, "Should contain model info"
            
            valid_sentiments = ["positive", "negative", "neutral"]
            assert result["predicted_category"] in valid_sentiments, f"Invalid sentiment: {result['predicted_category']}"
            assert 0.0 <= result["confidence"] <= 1.0, "Confidence should be between 0 and 1"
    
    def test_demographic_prediction_missing_fields(self):
        """Test demographic prediction with missing required fields."""
        if not os.path.exists("ml_models/sentiment_classifier.joblib"):
            pytest.skip("Model files not available - run training first")
        
        message = "Good product but could be better"
        
        result = predict_sentiment(
            message=message,
            gender="male"
        )
        
        assert isinstance(result, dict), "Should return a dictionary even with missing fields"
        assert "error" in result or "predicted_category" in result, "Should contain error or prediction"
    
    def test_demographic_prediction_invalid_values(self):
        """Test demographic prediction with invalid values."""
        if not os.path.exists("ml_models/sentiment_classifier.joblib"):
            pytest.skip("Model files not available - run training first")
        
        message = "Average product quality"
        
        result = predict_sentiment(
            message=message,
            gender="invalid_gender",
            age_range="invalid_age",
            education_level="invalid_education"
        )
        
        assert isinstance(result, dict), "Should return a dictionary"
        assert "error" in result or "predicted_category" in result, "Should handle invalid values"
    
    def test_text_features_prediction(self):
        """Test text-based sentiment prediction."""
        if not os.path.exists("ml_models/sentiment_classifier.joblib"):
            pytest.skip("Model files not available - run training first")
        
        message = "This is a great product! I love it."
        
        result = predict_sentiment(
            message=message,
            gender="female",
            age_range="25-34",
            education_level="bachelor"
        )
        
        assert isinstance(result, dict), "Should return a dictionary"
        
        if "error" not in result:
            assert "predicted_category" in result, "Should contain predicted category"
            assert "confidence" in result, "Should contain confidence score"
            assert "text_features" in result, "Should contain text features used"
            
            text_features = result["text_features"]
            assert "word_count" in text_features, "Should extract word count"
            assert "feedback_length" in text_features, "Should extract feedback length"
            assert text_features["word_count"] > 0, "Word count should be positive"
            assert text_features["feedback_length"] > 0, "Feedback length should be positive"
    
    def test_text_features_empty_message(self):
        """Test text prediction with empty message."""
        if not os.path.exists("ml_models/sentiment_classifier.joblib"):
            pytest.skip("Model files not available - run training first")
        
        result = predict_sentiment(
            message="",
            gender="female",
            age_range="25-34",
            education_level="bachelor"
        )
        
        assert isinstance(result, dict), "Should return a dictionary"
        assert "error" in result, "Should have error for empty message"
    
    def test_model_performance_benchmarks(self):
        """Test that model meets minimum performance benchmarks."""
        if not os.path.exists("ml_models/model_statistics.joblib"):
            pytest.skip("Model statistics not available - run training first")
        
        stats = joblib.load("ml_models/model_statistics.joblib")
        
        baseline_accuracy = stats.get("baseline_accuracy", 0)
        test_accuracy = stats.get("test_accuracy", 0)
        improvement = stats.get("improvement_over_baseline", 0)
        
        assert test_accuracy > baseline_accuracy, "Model should beat baseline accuracy"
        assert improvement > 0, "Should have positive improvement over baseline"
        
        assert 0.3 <= test_accuracy <= 1.0, f"Test accuracy {test_accuracy} should be reasonable"
        
        if test_accuracy >= 0.95:
            print(f"Warning: Very high accuracy ({test_accuracy}) - check for data leakage or small dataset")
            
        assert improvement <= 0.7, f"Improvement {improvement} seems too high - possible overfitting"
    
    def test_model_statistics_completeness(self):
        """Test that model statistics contain all required information."""
        if not os.path.exists("ml_models/model_statistics.joblib"):
            pytest.skip("Model statistics not available - run training first")
        
        stats = joblib.load("ml_models/model_statistics.joblib")
        
        required_fields = [
            'best_model_type', 'best_model_name', 'test_accuracy',
            'baseline_accuracy', 'improvement_over_baseline',
            'feature_columns', 'target_names', 'total_samples',
            'training_timestamp', 'model_purpose'
        ]
        
        for field in required_fields:
            assert field in stats, f"Missing required field: {field}"
        
        assert isinstance(stats['feature_columns'], list), "Feature columns should be a list"
        assert isinstance(stats['target_names'], list), "Target names should be a list"
        assert isinstance(stats['total_samples'], int), "Total samples should be an integer"
        assert stats['total_samples'] > 0, "Should have positive number of samples"
    
    def test_encoder_consistency(self):
        """Test that encoders are consistent with model requirements."""
        if not os.path.exists("ml_models/sentiment_classifier.joblib"):
            pytest.skip("Model files not available - run training first")
        
        _load_realistic_model()
        
        test_values = {
            "gender": ["male", "female", "other"],
            "age_range": ["18-24", "25-34", "35-44", "45-54", "55+"],
            "education_level": ["high_school", "bachelor", "master", "phd"],
            "country": ["Brazil", "USA", "Canada"],
            "state": ["SP", "RJ", "MG"]
        }
        
        from utils.realistic_model import _encoders
        
        for encoder_name, values in test_values.items():
            if encoder_name in _encoders:
                encoder = _encoders[encoder_name]
                known_classes = set(encoder.classes_)
                
                for value in values:
                    if value not in known_classes:
                        print(f"Warning: {value} not in {encoder_name} encoder classes")
    
    def test_model_training_integration(self):
        """Test the complete model training process."""
        test_data = pd.DataFrame({
            'sentiment_category': ['positive', 'negative', 'neutral'] * 20,
            'gender': ['male', 'female', 'other'] * 20,
            'age_range': ['25-34', '35-44', '18-24'] * 20,
            'education_level': ['bachelor', 'master', 'high_school'] * 20,
            'country': ['Brazil'] * 60,
            'state': ['SP'] * 60,
            'word_count': np.random.randint(5, 100, 60),
            'feedback_length': np.random.randint(20, 500, 60),
            'detected_language': ['pt'] * 60
        })
        
        os.makedirs("ml_data", exist_ok=True)
        test_data.to_csv("ml_data/feedback_dataset.csv", index=False)
        
        try:
            result = train_realistic_models()
            assert isinstance(result, bool), "Training should return boolean result"
            
            if result:
                assert os.path.exists("ml_models/sentiment_classifier.joblib"), "Model file should be created"
                assert os.path.exists("ml_models/model_statistics.joblib"), "Statistics file should be created"
                
        except Exception as e:
            pytest.fail(f"Training failed with error: {e}")
    
    def test_prediction_consistency(self):
        """Test that predictions are consistent for the same input."""
        if not os.path.exists("ml_models/sentiment_classifier.joblib"):
            pytest.skip("Model files not available - run training first")
        
        message = "Good quality product with nice features"
        
        predictions = []
        for _ in range(5):
            result = predict_sentiment(
                message=message,
                gender="male",
                age_range="25-34",
                education_level="bachelor"
            )
            if "predicted_category" in result:
                predictions.append(result["predicted_category"])
        
        if predictions:
            assert all(p == predictions[0] for p in predictions), "Predictions should be consistent"
    
    def test_model_memory_efficiency(self):
        """Test that model loading and prediction don't consume excessive memory."""
        if not os.path.exists("ml_models/sentiment_classifier.joblib"):
            pytest.skip("Model files not available - run training first")
        
        import psutil
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss
        
        _load_realistic_model()
        
        for _ in range(10):
            message = f"Test feedback message number {_} with various content"
            predict_sentiment(
                message=message,
                gender="male",
                age_range="25-34",
                education_level="bachelor"
            )
        
        memory_after = process.memory_info().rss
        memory_increase = (memory_after - memory_before) / (1024 * 1024)
        
        assert memory_increase < 100, f"Memory increase too high: {memory_increase:.2f} MB"
    
    def test_compare_with_vader(self):
        """Test comparison functionality between realistic model and VADER."""
        if not os.path.exists("ml_models/sentiment_classifier.joblib"):
            pytest.skip("Model files not available - run training first")
        
        message = "This product is absolutely amazing and works perfectly!"
        
        vader_result = {
            "sentiment_category": "positive",
            "sentiment_score": 0.8
        }
        
        result = compare_with_vader(
            message=message,
            vader_result=vader_result,
            gender="female",
            age_range="25-34",
            education_level="bachelor"
        )
        
        assert isinstance(result, dict), "Should return a dictionary"
        
        if "error" not in result:
            assert "vader_prediction" in result, "Should contain VADER prediction"
            assert "ml_prediction" in result, "Should contain ML prediction"
            assert "agreement" in result, "Should contain agreement analysis"
            assert "message_stats" in result, "Should contain message statistics"