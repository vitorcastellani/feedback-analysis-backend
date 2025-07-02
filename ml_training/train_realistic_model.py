import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from imblearn.under_sampling import RandomUnderSampler

def train_realistic_models():
    """Train both demographic-only and text-based models with proper evaluation"""
    
    data_file = "ml_data/feedback_dataset.csv"
    if not os.path.exists(data_file):
        print(f"Error: Data file {data_file} not found!")
        return False

    print("Loading dataset...")
    df = pd.read_csv(data_file)
    print(f"Dataset shape: {df.shape}")

    print("\nClass distribution:")
    class_counts = df['sentiment_category'].value_counts()
    print(class_counts)
    
    # Calculate baseline performance
    majority_baseline = class_counts.max() / len(df)
    random_baseline = 1 / len(class_counts)
    
    print(f"\nBaseline Performance:")
    print(f"  Majority class baseline: {majority_baseline:.3f}")
    print(f"  Random baseline: {random_baseline:.3f}")
    print(f"  Minimum acceptable accuracy: {majority_baseline + 0.05:.3f}")

    # Prepare common encodings
    df_model = df.copy()
    encoders = {}
    
    # Encode demographics
    demographic_features = ['gender', 'age_range', 'education_level', 'country', 'state']
    for col in demographic_features:
        encoders[col] = LabelEncoder()
        df_model[col] = encoders[col].fit_transform(df_model[col])

    # Encode target
    encoders['sentiment_category'] = LabelEncoder()
    df_model['sentiment_category_encoded'] = encoders['sentiment_category'].fit_transform(df_model['sentiment_category'])
    target_names = encoders['sentiment_category'].classes_

    # ═══════════════════════════════════════════════════════════════════
    # MODEL 1: DEMOGRAPHIC-ONLY MODEL (Conservative)
    # ═══════════════════════════════════════════════════════════════════
    
    print("\n" + "="*70)
    print("TRAINING MODEL 1: DEMOGRAPHIC-ONLY (for user profiling)")
    print("="*70)
    
    # Safe demographic features
    demo_features = demographic_features.copy()
    
    # Add simple demographic interactions
    df_model['age_education'] = df_model['age_range'] * df_model['education_level']
    df_model['is_higher_edu'] = (df_model['education_level'] >= 3).astype(int)  # Assuming 3+ is higher education
    demo_features.extend(['age_education', 'is_higher_edu'])
    
    X_demo = df_model[demo_features].values
    y = df_model['sentiment_category_encoded'].values
    
    # Balance classes for demographic model
    rus = RandomUnderSampler(random_state=42)
    X_demo_balanced, y_balanced = rus.fit_resample(X_demo, y)
    
    # Split data
    X_demo_train, X_demo_test, y_demo_train, y_demo_test = train_test_split(
        X_demo_balanced, y_balanced, test_size=0.2, stratify=y_balanced, random_state=42
    )
    
    print(f"Demographic model data: {X_demo_train.shape[0]} train, {X_demo_test.shape[0]} test")
    
    # Train very simple model
    demo_model = RandomForestClassifier(
        n_estimators=30,
        max_depth=3,
        min_samples_split=30,
        min_samples_leaf=15,
        random_state=42,
        class_weight='balanced'
    )
    
    demo_model.fit(X_demo_train, y_demo_train)
    
    # Evaluate demographic model
    demo_cv_scores = cross_val_score(demo_model, X_demo_train, y_demo_train, cv=5)
    demo_train_acc = accuracy_score(y_demo_train, demo_model.predict(X_demo_train))
    demo_test_acc = accuracy_score(y_demo_test, demo_model.predict(X_demo_test))
    
    print(f"\nDemographic Model Results:")
    print(f"  CV Accuracy: {demo_cv_scores.mean():.3f} (±{demo_cv_scores.std():.3f})")
    print(f"  Train Accuracy: {demo_train_acc:.3f}")
    print(f"  Test Accuracy: {demo_test_acc:.3f}")
    print(f"  Beats majority baseline: {'Yes' if demo_test_acc > majority_baseline else 'No'}")
    
    # ═══════════════════════════════════════════════════════════════════
    # MODEL 2: TEXT-BASED MODEL (for content analysis, without sentiment score)
    # ═══════════════════════════════════════════════════════════════════
    
    print("\n" + "="*70)
    print("TRAINING MODEL 2: TEXT-BASED (for content analysis)")
    print("="*70)
    
    # Safe text features (without sentiment score to avoid leakage)
    if 'detected_language' in df_model.columns:
        encoders['detected_language'] = LabelEncoder()
        df_model['detected_language'] = encoders['detected_language'].fit_transform(df_model['detected_language'])
    
    # Create text-based features
    text_features = []
    
    if 'word_count' in df_model.columns and 'feedback_length' in df_model.columns:
        # Basic text statistics
        df_model['avg_word_length'] = df_model['feedback_length'] / (df_model['word_count'] + 1)
        df_model['is_very_short'] = (df_model['word_count'] <= 5).astype(int)
        df_model['is_short'] = (df_model['word_count'] <= 15).astype(int)
        df_model['is_medium'] = ((df_model['word_count'] > 15) & (df_model['word_count'] <= 50)).astype(int)
        df_model['is_long'] = (df_model['word_count'] > 50).astype(int)
        
        text_features.extend([
            'word_count', 'feedback_length', 'avg_word_length',
            'is_very_short', 'is_short', 'is_medium', 'is_long'
        ])
        
        # Text complexity features
        df_model['text_density'] = df_model['word_count'] / (df_model['feedback_length'] + 1)
        text_features.append('text_density')
    
    if 'detected_language' in df_model.columns:
        text_features.append('detected_language')
    
    # Combine with basic demographics for context
    text_demo_features = ['gender', 'age_range', 'education_level'] + text_features
    
    print(f"Text-based features: {text_features}")
    print(f"Total features for text model: {len(text_demo_features)}")
    
    if len(text_features) > 0:
        X_text = df_model[text_demo_features].values
        
        # Balance classes for text model
        X_text_balanced, y_text_balanced = rus.fit_resample(X_text, y)
        
        # Split data
        X_text_train, X_text_test, y_text_train, y_text_test = train_test_split(
            X_text_balanced, y_text_balanced, test_size=0.2, stratify=y_text_balanced, random_state=42
        )
        
        print(f"Text model data: {X_text_train.shape[0]} train, {X_text_test.shape[0]} test")
        
        # Train text-based model
        text_model = RandomForestClassifier(
            n_estimators=50,
            max_depth=4,
            min_samples_split=20,
            min_samples_leaf=10,
            random_state=42,
            class_weight='balanced'
        )
        
        text_model.fit(X_text_train, y_text_train)
        
        # Evaluate text model
        text_cv_scores = cross_val_score(text_model, X_text_train, y_text_train, cv=5)
        text_train_acc = accuracy_score(y_text_train, text_model.predict(X_text_train))
        text_test_acc = accuracy_score(y_text_test, text_model.predict(X_text_test))
        
        print(f"\nText-Based Model Results:")
        print(f"  CV Accuracy: {text_cv_scores.mean():.3f} (±{text_cv_scores.std():.3f})")
        print(f"  Train Accuracy: {text_train_acc:.3f}")
        print(f"  Test Accuracy: {text_test_acc:.3f}")
        print(f"  Beats majority baseline: {'Yes' if text_test_acc > majority_baseline else 'No'}")
        
        # Feature importance for text model
        text_importance = pd.DataFrame({
            'feature': text_demo_features,
            'importance': text_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\nTop text-based features:")
        for _, row in text_importance.head(8).iterrows():
            print(f"  {row['feature']:20s}: {row['importance']:.3f}")
    
    else:
        print("WARNING: No text features available for text-based model")
        text_test_acc = 0
        text_model = None
        text_demo_features = []

    # ═══════════════════════════════════════════════════════════════════
    # MODEL COMPARISON AND DECISION
    # ═══════════════════════════════════════════════════════════════════
    
    print("\n" + "="*70)
    print("MODEL COMPARISON AND SELECTION")
    print("="*70)
    
    models_info = [
        ("Demographic-only", demo_test_acc, demo_model, demo_features, "demographic"),
        ("Text-based", text_test_acc, text_model, text_demo_features, "text")
    ]
    
    # Find best model
    best_acc = 0
    best_model_info = None
    acceptable_models = []
    
    minimum_acceptable = majority_baseline + 0.03  # At least 3% better than baseline
    
    for name, acc, model, features, model_type in models_info:
        print(f"\n{name} Model:")
        print(f"  Accuracy: {acc:.3f}")
        print(f"  Acceptable: {'Yes' if acc > minimum_acceptable else 'No'}")
        
        if acc > minimum_acceptable and model is not None:
            acceptable_models.append((name, acc, model, features, model_type))
            
        if acc > best_acc and model is not None:
            best_acc = acc
            best_model_info = (name, acc, model, features, model_type)
    
    # Save models based on performance
    os.makedirs("ml_models", exist_ok=True)
    saved_models = []
    
    if len(acceptable_models) > 0:
        print(f"\nFound {len(acceptable_models)} acceptable model(s)")
        
        # Save the best acceptable model as the main model
        best_name, best_acc, best_model, best_features, best_type = acceptable_models[0]
        
        # Sort by accuracy
        acceptable_models.sort(key=lambda x: x[1], reverse=True)
        best_name, best_acc, best_model, best_features, best_type = acceptable_models[0]
        
        print(f"\nSaving BEST model: {best_name} (accuracy: {best_acc:.3f})")
        
        try:
            # Save best model as main model
            joblib.dump(best_model, "ml_models/sentiment_classifier.joblib")
            
            # Save feature list
            joblib.dump(best_features, "ml_models/feature_columns.joblib")
            
            # Save all encoders
            for name, encoder in encoders.items():
                joblib.dump(encoder, f"ml_models/{name}_encoder.joblib")
            
            # Save comprehensive metadata
            model_stats = {
                'best_model_type': best_type,
                'best_model_name': best_name,
                'test_accuracy': float(best_acc),
                'baseline_accuracy': float(majority_baseline),
                'improvement_over_baseline': float(best_acc - majority_baseline),
                'feature_columns': best_features,
                'target_names': target_names.tolist(),
                'class_distribution': class_counts.to_dict(),
                'total_samples': len(df),
                'balanced_samples': len(y_balanced),
                'acceptable_models': [
                    {
                        'name': name,
                        'accuracy': float(acc),
                        'type': mtype
                    } for name, acc, _, _, mtype in acceptable_models
                ],
                'training_timestamp': pd.Timestamp.now().isoformat(),
                'model_purpose': f'Realistic sentiment classification using {best_type} features',
                'performance_notes': 'Conservative model avoiding data leakage'
            }
            
            if best_type == "text" and len(text_features) > 0:
                model_stats['feature_importance'] = text_importance.to_dict('records')
            
            joblib.dump(model_stats, "ml_models/model_statistics.joblib")
            
            print(f"Best model saved successfully!")
            print(f"   Model type: {best_type}")
            print(f"   Features: {len(best_features)}")
            print(f"   Accuracy: {best_acc:.3f}")
            print(f"   Improvement over baseline: {best_acc - majority_baseline:.3f}")
            
            return True
            
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    else:
        print(f"\nNo acceptable models found!")
        print(f"   Minimum required accuracy: {minimum_acceptable:.3f}")
        print(f"   Best achieved accuracy: {best_acc:.3f}")
        print(f"\nRecommendations:")
        print(f"   1. Collect more diverse training data")
        print(f"   2. Consider this is expected for demographic-only prediction")
        print(f"   3. Use VADER sentiment analysis directly for better accuracy")
        print(f"   4. Combine multiple weak predictors")
        
        return False

if __name__ == "__main__":
    print("Starting realistic sentiment model training...")
    print("This will train conservative models avoiding data leakage...")
    
    success = train_realistic_models()
    
    if success:
        print("\nRealistic model training completed successfully!")
        print("Note: Lower accuracy is expected and more honest than 100% accuracy!")
    else:
        print("\nTraining completed but no models met acceptance criteria.")
        print("This is normal for demographic-only sentiment prediction!")