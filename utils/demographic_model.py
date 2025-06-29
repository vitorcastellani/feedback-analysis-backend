import joblib
import os
import numpy as np

BASE_PATH = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_PATH, "../ml_models/demographic_sentiment_model.joblib")
GENDER_ENCODER_PATH = os.path.join(BASE_PATH, "../ml_models/gender_encoder.joblib")
AGE_ENCODER_PATH = os.path.join(BASE_PATH, "../ml_models/age_encoder.joblib")
EDUCATION_ENCODER_PATH = os.path.join(BASE_PATH, "../ml_models/education_encoder.joblib")
COUNTRY_ENCODER_PATH = os.path.join(BASE_PATH, "../ml_models/country_encoder.joblib")
STATE_ENCODER_PATH = os.path.join(BASE_PATH, "../ml_models/state_encoder.joblib")
LABEL_ENCODER_PATH = os.path.join(BASE_PATH, "../ml_models/label_encoder.joblib")

# Variáveis globais para cache dos modelos
_model = None
_gender_encoder = None
_age_encoder = None
_education_encoder = None
_country_encoder = None
_state_encoder = None
_label_encoder = None
_model_loaded = False

def _check_model_files_exist():
    """Verifica se todos os arquivos do modelo existem"""
    return all(os.path.exists(path) for path in [
        MODEL_PATH, GENDER_ENCODER_PATH, AGE_ENCODER_PATH, 
        EDUCATION_ENCODER_PATH, COUNTRY_ENCODER_PATH, 
        STATE_ENCODER_PATH, LABEL_ENCODER_PATH
    ])

def _load_global_model():
    """Carrega o modelo global e encoders (lazy loading)"""
    global _model, _gender_encoder, _age_encoder, _education_encoder, _country_encoder, _state_encoder, _label_encoder, _model_loaded
    
    if _model_loaded:
        return _model is not None
    
    if not _check_model_files_exist():
        # Tentar treinar o modelo automaticamente
        try:
            from .auto_train import export_and_train_global_model
            print("Global model not found. Training automatically...")
            if export_and_train_global_model():
                print("Global model trained successfully!")
            else:
                print("Failed to train global model automatically")
                _model_loaded = True
                return False
        except Exception as e:
            print(f"Error auto-training global model: {e}")
            _model_loaded = True
            return False
    
    try:
        _model = joblib.load(MODEL_PATH)
        _gender_encoder = joblib.load(GENDER_ENCODER_PATH)
        _age_encoder = joblib.load(AGE_ENCODER_PATH)
        _education_encoder = joblib.load(EDUCATION_ENCODER_PATH)
        _country_encoder = joblib.load(COUNTRY_ENCODER_PATH)
        _state_encoder = joblib.load(STATE_ENCODER_PATH)
        _label_encoder = joblib.load(LABEL_ENCODER_PATH)
        _model_loaded = True
        return True
    except Exception as e:
        print(f"Error loading global model: {e}")
        _model_loaded = True
        return False

def global_model_exists():
    """Verifica se o modelo global existe, criando/treinando automaticamente se não existir"""
    if not _check_model_files_exist():
        try:
            from .auto_train import export_and_train_global_model
            print("Global model not found. Training automatically...")
            if export_and_train_global_model():
                print("Global model trained successfully!")
                return True
            else:
                print("Failed to train global model automatically")
                return False
        except Exception as e:
            print(f"Error auto-training global model: {e}")
            return False
    return True

def classify_demographic(gender: str, age_range: str, education_level: str, country: str, state: str) -> str:
    """Classifica sentimento baseado em dados demográficos"""
    global _model
    
    # Verificar se modelo está carregado ou tentar carregar
    if _model is None:
        if not _load_global_model():
            return "model_not_available"
    
    try:
        # Codificar features
        try:
            gender_code = _gender_encoder.transform([gender])[0]
        except (ValueError, AttributeError):
            gender_code = 0
        
        try:
            age_code = _age_encoder.transform([age_range])[0]
        except (ValueError, AttributeError):
            age_code = 0
        
        try:
            education_code = _education_encoder.transform([education_level])[0]
        except (ValueError, AttributeError):
            education_code = 0
        
        try:
            country_code = _country_encoder.transform([country])[0]
        except (ValueError, AttributeError):
            country_code = 0
        
        try:
            state_code = _state_encoder.transform([state])[0]
        except (ValueError, AttributeError):
            state_code = 0

        # Usar array numpy sem nomes de features
        features = np.array([[gender_code, age_code, education_code, country_code, state_code]])
        pred = _model.predict(features)[0]
        return _label_encoder.inverse_transform([pred])[0]
        
    except Exception as e:
        print(f"Error in demographic classification: {e}")
        return "classification_error"