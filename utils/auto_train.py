import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import joblib
from config import SessionLocal
from model import Feedback, FeedbackAnalysis

def export_and_train_global_model():
    """Exporta dados e treina o modelo global automaticamente"""
    try:
        print("Starting automatic global model training...")
        
        # Exportar dados do banco
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
            ).all()

            if len(records) < 5:
                print(f"Not enough data to train global model. Found {len(records)} records, need at least 5.")
                return False

            print(f"Found {len(records)} records for training")

            # Converter para DataFrame
            df = pd.DataFrame([{
                'gender': r.gender.value if r.gender else "unknown",
                'age_range': r.age_range.value if r.age_range else "unknown",
                'education_level': r.education_level.value if r.education_level else "unknown",
                'country': r.country.value if r.country else "unknown",
                'state': r.state.value if r.state else "unknown",
                'sentiment_category': r.sentiment_category.value
            } for r in records])

        print("\nClass distribution:")
        print(df["sentiment_category"].value_counts())

        total_samples = len(df)
        min_class_count = df["sentiment_category"].value_counts().min()
        print(f"\nTotal samples: {total_samples}")
        print(f"Minimum class count: {min_class_count}")

        if total_samples < 10:
            print("Warning: Very small dataset. Training on all data without test split.")
            use_test_split = False
        elif min_class_count < 2:
            print("Warning: Some classes have only 1 sample. Cannot use stratified split.")
            use_stratify = False
            use_test_split = True
        else:
            use_stratify = True
            use_test_split = True

        # Preparar encoders
        encoders = {}
        feature_columns = ['gender', 'age_range', 'education_level', 'country', 'state']
        
        for col in feature_columns + ['sentiment_category']:
            encoders[col] = LabelEncoder()
            df[col] = encoders[col].fit_transform(df[col])

        # Usar valores numéricos puros (sem nomes de features)
        X = df[feature_columns].values
        y = df['sentiment_category'].values

        # Dividir dados se possível
        if use_test_split:
            if use_stratify:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
            else:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        else:
            X_train, y_train = X, y
            X_test, y_test = X, y

        # Treinar modelo
        model = GaussianNB()
        model.fit(X_train, y_train)

        # Avaliar modelo
        if use_test_split and len(X_test) > 0:
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            print(f"\nTest Accuracy: {accuracy:.4f}")
        
        train_pred = model.predict(X_train)
        train_accuracy = accuracy_score(y_train, train_pred)
        print(f"Train Accuracy: {train_accuracy:.4f}")

        # Salvar modelo e encoders
        os.makedirs("ml_models", exist_ok=True)
        
        joblib.dump(model, "ml_models/demographic_sentiment_model.joblib")
        joblib.dump(encoders['gender'], "ml_models/gender_encoder.joblib")
        joblib.dump(encoders['age_range'], "ml_models/age_encoder.joblib")
        joblib.dump(encoders['education_level'], "ml_models/education_encoder.joblib")
        joblib.dump(encoders['country'], "ml_models/country_encoder.joblib")
        joblib.dump(encoders['state'], "ml_models/state_encoder.joblib")
        joblib.dump(encoders['sentiment_category'], "ml_models/label_encoder.joblib")

        print("\nGlobal model and encoders saved successfully!")
        print(f"Classes found: {encoders['sentiment_category'].classes_}")
        
        return True
        
    except Exception as e:
        print(f"Error training global model: {e}")
        return False

def ensure_global_model_exists():
    """Garante que o modelo global existe, treinando se necessário"""
    from .demographic_model import global_model_exists
    
    if not global_model_exists():
        print("Global model not found. Training automatically...")
        return export_and_train_global_model()
    else:
        print("Global model already exists.")
        return True