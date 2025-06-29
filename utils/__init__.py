from .common import generate_short_code
from .sentiment_analysis import analyze_sentiment, get_star_rating

# Imports condicionais para evitar erros na inicialização
try:
    from .smart_model import predict_sentiment_smart
    from .demographic_model import classify_demographic, global_model_exists
    from .model_manager import CampaignModelManager
    from .auto_train import ensure_global_model_exists
except Exception as e:
    print(f"Warning: ML models not available: {e}")
    
    # Funções fallback
    def predict_sentiment_smart(*args, **kwargs):
        return {
            "predictions": {
                "global_model": "model_not_available",
                "campaign_model": "model_not_available"
            },
            "model_status": {
                "global_model_exists": False,
                "campaign_model_exists": False,
                "message": "Models not initialized"
            }
        }
    
    def classify_demographic(*args, **kwargs):
        return "model_not_available"
    
    def global_model_exists(*args, **kwargs):
        return False
    
    def ensure_global_model_exists(*args, **kwargs):
        return False
    
    class CampaignModelManager:
        def __init__(self):
            pass
        
        def ensure_model_ready(self, *args, **kwargs):
            return {
                'model_exists': False,
                'model_trained': False,
                'model_retrained': False,
                'should_use_global': True,
                'message': 'Model manager not available'
            }