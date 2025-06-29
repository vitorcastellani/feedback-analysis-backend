from .model_manager import CampaignModelManager
from .demographic_model import classify_demographic, global_model_exists

model_manager = CampaignModelManager()

def predict_sentiment_smart(campaign_id: int, gender: str, age_range: str, education_level: str, country: str, state: str) -> dict:
    # Garantir que o modelo esteja pronto
    model_status = model_manager.ensure_model_ready(campaign_id)
    
    # Tentar obter predição do modelo específico da campanha
    campaign_prediction = "no_model_available"
    
    if not model_status['should_use_global']:
        campaign_pred = model_manager.predict(campaign_id, gender, age_range, education_level, country, state)
        if campaign_pred:
            campaign_prediction = campaign_pred
    
    # Tentar obter predição do modelo global
    global_prediction = "no_model_available"
    if global_model_exists():
        global_pred = classify_demographic(gender, age_range, education_level, country, state)
        if global_pred not in ["model_not_available", "classification_error"]:
            global_prediction = global_pred
    
    return {
        "campaign_id": campaign_id,
        "predictions": {
            "global_model": global_prediction,
            "campaign_model": campaign_prediction
        },
        "model_status": {
            "campaign_model_exists": model_status['model_exists'],
            "campaign_model_trained": model_status['model_trained'],
            "campaign_model_retrained": model_status['model_retrained'],
            "global_model_exists": global_model_exists(),
            "message": model_status['message']
        }
    }