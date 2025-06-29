import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder
from config import SessionLocal
from model import Feedback, FeedbackAnalysis
from typing import Optional, Dict, Any

class CampaignModelManager:
    def __init__(self):
        self.models_dir = "ml_models"
        self.min_samples_for_training = 20
        self.retrain_threshold = 50
        
    def get_model_path(self, campaign_id: int) -> str:
        return f"{self.models_dir}/campaign_{campaign_id}_model.joblib"
    
    def get_model_metadata_path(self, campaign_id: int) -> str:
        return f"{self.models_dir}/campaign_{campaign_id}_metadata.joblib"
    
    def model_exists(self, campaign_id: int) -> bool:
        return os.path.exists(self.get_model_path(campaign_id))
    
    def get_model_metadata(self, campaign_id: int) -> Optional[Dict]:
        metadata_path = self.get_model_metadata_path(campaign_id)
        if os.path.exists(metadata_path):
            return joblib.load(metadata_path)
        return None
    
    def save_model_metadata(self, campaign_id: int, metadata: Dict):
        os.makedirs(self.models_dir, exist_ok=True)
        metadata_path = self.get_model_metadata_path(campaign_id)
        joblib.dump(metadata, metadata_path)
    
    def should_retrain_model(self, campaign_id: int) -> bool:
        if not self.model_exists(campaign_id):
            return False
            
        metadata = self.get_model_metadata(campaign_id)
        if not metadata:
            return True
            
        with SessionLocal() as db:
            # Buscar os últimos N feedbacks analisados da campanha
            recent_feedbacks = db.query(Feedback.created_at).join(
                FeedbackAnalysis, Feedback.id == FeedbackAnalysis.feedback_id
            ).filter(
                Feedback.campaign_id == campaign_id
            ).order_by(
                Feedback.created_at.desc()
            ).limit(self.retrain_threshold).all()
            
            if len(recent_feedbacks) < self.retrain_threshold:
                return False
            
            # Verificar se o feedback mais antigo dos últimos N é posterior ao último treino
            oldest_recent_feedback = recent_feedbacks[-1].created_at
            last_training_date = metadata.get('training_date')
            
            if isinstance(last_training_date, str):
                last_training_date = datetime.fromisoformat(last_training_date)
            
            return oldest_recent_feedback > last_training_date
    
    def get_campaign_data(self, campaign_id: int) -> pd.DataFrame:
        with SessionLocal() as db:
            records = db.query(
                Feedback.gender,
                Feedback.age_range,
                Feedback.education_level,
                Feedback.country,
                Feedback.state,
                FeedbackAnalysis.sentiment_category
            ).join(
                FeedbackAnalysis, Feedback.id == FeedbackAnalysis.feedback_id
            ).filter(
                Feedback.campaign_id == campaign_id
            ).all()
            
            if len(records) < self.min_samples_for_training:
                return None
                
            df = pd.DataFrame([{
                'gender': r.gender.value if r.gender else "unknown",
                'age_range': r.age_range.value if r.age_range else "unknown",
                'education_level': r.education_level.value if r.education_level else "unknown",
                'country': r.country.value if r.country else "unknown",
                'state': r.state.value if r.state else "unknown",
                'sentiment_category': r.sentiment_category.value
            } for r in records])
            
            return df
    
    def train_campaign_model(self, campaign_id: int) -> bool:
        df = self.get_campaign_data(campaign_id)
        if df is None:
            print(f"Not enough data to train model for campaign {campaign_id}")
            return False
        
        # Verificar se há pelo menos 2 classes diferentes
        if df['sentiment_category'].nunique() < 2:
            print(f"Need at least 2 different sentiment categories for campaign {campaign_id}")
            return False
        
        # Preparar encoders
        encoders = {}
        feature_columns = ['gender', 'age_range', 'education_level', 'country', 'state']
        
        for col in feature_columns + ['sentiment_category']:
            encoders[col] = LabelEncoder()
            df[col] = encoders[col].fit_transform(df[col])
        
        # Usar valores numpy sem nomes de features
        X = df[feature_columns].values
        y = df['sentiment_category'].values
        
        # Treinar modelo
        model = GaussianNB()
        model.fit(X, y)
        
        # Salvar modelo e encoders
        os.makedirs(self.models_dir, exist_ok=True)
        
        model_data = {
            'model': model,
            'encoders': encoders
        }
        
        joblib.dump(model_data, self.get_model_path(campaign_id))
        
        # Salvar metadata
        metadata = {
            'campaign_id': campaign_id,
            'training_date': datetime.now().isoformat(),
            'sample_count': len(df),
            'feature_columns': feature_columns,
            'classes': encoders['sentiment_category'].classes_.tolist()
        }
        
        self.save_model_metadata(campaign_id, metadata)
        
        print(f"Model trained for campaign {campaign_id} with {len(df)} samples")
        return True
    
    def predict(self, campaign_id: int, gender: str, age_range: str, education_level: str, country: str, state: str) -> Optional[str]:
        if not self.model_exists(campaign_id):
            return None
        
        try:
            model_data = joblib.load(self.get_model_path(campaign_id))
            model = model_data['model']
            encoders = model_data['encoders']
            
            # Codificar features
            features = []
            feature_values = [gender, age_range, education_level, country, state]
            feature_names = ['gender', 'age_range', 'education_level', 'country', 'state']
            
            for i, (name, value) in enumerate(zip(feature_names, feature_values)):
                try:
                    encoded_value = encoders[name].transform([value])[0]
                except ValueError:
                    # Valor não visto durante o treinamento, usar o primeiro valor conhecido
                    encoded_value = 0
                features.append(encoded_value)
            
            # Fazer predição usando array numpy
            prediction = model.predict(np.array([features]))[0]
            return encoders['sentiment_category'].inverse_transform([prediction])[0]
            
        except Exception as e:
            print(f"Error predicting with campaign model {campaign_id}: {e}")
            return None
    
    def ensure_model_ready(self, campaign_id: int) -> Dict[str, Any]:
        """
        Garante que o modelo esteja pronto para uso.
        Retorna informações sobre o status do modelo.
        """
        result = {
            'campaign_id': campaign_id,
            'model_exists': False,
            'model_trained': False,
            'model_retrained': False,
            'should_use_global': True,
            'message': ''
        }
        
        # Verificar se modelo existe
        if self.model_exists(campaign_id):
            result['model_exists'] = True
            
            # Verificar se precisa retreinar
            if self.should_retrain_model(campaign_id):
                if self.train_campaign_model(campaign_id):
                    result['model_retrained'] = True
                    result['should_use_global'] = False
                    result['message'] = 'Model retrained successfully'
                else:
                    result['message'] = 'Failed to retrain model, using global fallback'
            else:
                result['should_use_global'] = False
                result['message'] = 'Using existing campaign model'
        else:
            # Tentar criar novo modelo
            if self.train_campaign_model(campaign_id):
                result['model_trained'] = True
                result['should_use_global'] = False
                result['message'] = 'New model trained successfully'
            else:
                result['message'] = 'Not enough data for campaign model, using global fallback'
        
        return result