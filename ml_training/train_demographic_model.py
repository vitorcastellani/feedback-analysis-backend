import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

def train_demographic_model():
    """Trains the demographic model using exported data"""
    
    # Check if data file exists
    data_file = "ml_data/hierarchical_feedback_dataset.csv"
    if not os.path.exists(data_file):
        print(f"Error: Data file {data_file} not found!")
        print("Please run export_feedback_dataset.py first.")
        return False
    
    # Load data
    print("Loading dataset...")
    df = pd.read_csv(data_file)
    print(f"Dataset shape: {df.shape}")
    
    # Check required columns
    required_columns = ['gender', 'age_range', 'education_level', 'country', 'state', 'sentiment_category']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"Error: Missing required columns: {missing_columns}")
        return False
    
    # Initial data analysis
    print("\nClass distribution:")
    class_counts = df['sentiment_category'].value_counts()
    print(class_counts)
    
    total_samples = len(df)
    min_class_count = class_counts.min()
    num_classes = df['sentiment_category'].nunique()
    
    print(f"\nTotal samples: {total_samples}")
    print(f"Minimum class count: {min_class_count}")
    print(f"Number of classes: {num_classes}")
    
    # Viability checks
    if total_samples < 10:
        print("Error: Not enough samples to train a model (minimum 10 required)")
        return False
    
    if num_classes < 2:
        print("Error: Need at least 2 different classes to train a classifier")
        return False
    
    # Determine data splitting strategy
    use_test_split = total_samples >= 20
    use_stratify = min_class_count >= 2 and total_samples >= 20
    
    print(f"\nTraining strategy:")
    print(f"  Use test split: {use_test_split}")
    print(f"  Use stratified split: {use_stratify}")
    
    # Prepare encoders
    print("\nEncoding categorical variables...")
    encoders = {}
    feature_columns = ['gender', 'age_range', 'education_level', 'country', 'state']
    
    # Make a copy to avoid modifying original DataFrame
    df_encoded = df.copy()
    
    # Encode features
    for col in feature_columns:
        encoders[col] = LabelEncoder()
        df_encoded[col] = encoders[col].fit_transform(df_encoded[col])
        print(f"  {col}: {len(encoders[col].classes_)} unique values")
    
    # Encode target
    encoders['sentiment_category'] = LabelEncoder()
    df_encoded['sentiment_category'] = encoders['sentiment_category'].fit_transform(df_encoded['sentiment_category'])
    
    target_names = encoders['sentiment_category'].classes_
    print(f"  Target classes: {target_names}")
    
    # Prepare training data
    X = df_encoded[feature_columns].values
    y = df_encoded['sentiment_category'].values
    
    print(f"\nFeature matrix shape: {X.shape}")
    print(f"Target vector shape: {y.shape}")
    
    # Split data
    if use_test_split:
        try:
            if use_stratify:
                print("Using stratified train-test split...")
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, stratify=y, random_state=42
                )
            else:
                print("Using random train-test split...")
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
            
            # Check if all classes are present in test set
            train_classes = set(np.unique(y_train))
            test_classes = set(np.unique(y_test))
            
            print(f"Classes in training set: {sorted(train_classes)}")
            print(f"Classes in test set: {sorted(test_classes)}")
            
            missing_test_classes = train_classes - test_classes
            if missing_test_classes:
                print(f"Warning: Classes {missing_test_classes} missing from test set")
                print("Adjusting test size to ensure class representation...")
                
                # Try with smaller test_size
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.1, stratify=y, random_state=42
                )
                test_classes = set(np.unique(y_test))
                print(f"New test classes: {sorted(test_classes)}")
                
                # If still not working, use full dataset for evaluation
                if train_classes != test_classes:
                    print("Still missing classes. Using full dataset for evaluation.")
                    X_test, y_test = X, y
                    
        except ValueError as e:
            print(f"Error in stratified split: {e}")
            print("Falling back to simple train-test split...")
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
    else:
        print("Using all data for training (no test split due to small dataset)")
        X_train, y_train = X, y
        X_test, y_test = X, y
    
    print(f"\nFinal data split:")
    print(f"  Training set: {X_train.shape[0]} samples")
    print(f"  Test set: {X_test.shape[0]} samples")
    
    # Train model
    print("\nTraining Gaussian Naive Bayes model...")
    model = GaussianNB()
    model.fit(X_train, y_train)
    print("Model training completed!")
    
    # Evaluate model
    print("\n" + "="*50)
    print("MODEL EVALUATION")
    print("="*50)
    
    # Training accuracy
    y_train_pred = model.predict(X_train)
    train_accuracy = accuracy_score(y_train, y_train_pred)
    print(f"\nTrain Accuracy: {train_accuracy:.4f}")
    
    # Test accuracy
    y_test_pred = model.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_test_pred)
    print(f"Test Accuracy: {test_accuracy:.4f}")
    
    if use_test_split and X_train.shape[0] != X_test.shape[0]:
        overfitting = train_accuracy - test_accuracy
        print(f"Overfitting measure: {overfitting:.4f}")
        if overfitting > 0.1:
            print("⚠️  Warning: Possible overfitting detected!")
    
    # Classification Report
    print(f"\n" + "="*50)
    print("CLASSIFICATION REPORT")
    print("="*50)
    
    try:
        # Check classes present again
        unique_test_classes = np.unique(y_test)
        unique_pred_classes = np.unique(y_test_pred)
        
        print(f"Classes in y_test: {unique_test_classes}")
        print(f"Classes in predictions: {unique_pred_classes}")
        print(f"Target names available: {target_names}")
        
        # Generate report
        if len(unique_test_classes) > 1:  # Only generate if more than one class
            report = classification_report(
                y_test, y_test_pred,
                target_names=target_names,
                labels=range(len(target_names)),
                zero_division=0
            )
            print("\nDetailed Classification Report:")
            print(report)
        else:
            print("Cannot generate classification report: only one class in test set")
            
    except Exception as e:
        print(f"Error generating classification report: {e}")
        print("Generating basic accuracy metrics instead...")
    
    # Confusion Matrix
    print(f"\n" + "="*50)
    print("CONFUSION MATRIX")
    print("="*50)
    
    try:
        cm = confusion_matrix(y_test, y_test_pred)
        print("\nConfusion Matrix (raw):")
        print(cm)
        
        # Confusion matrix with class names
        if len(target_names) == cm.shape[0]:
            print(f"\nConfusion Matrix with class names:")
            cm_df = pd.DataFrame(
                cm,
                index=[f"True_{name}" for name in target_names],
                columns=[f"Pred_{name}" for name in target_names]
            )
            print(cm_df)
        
    except Exception as e:
        print(f"Error generating confusion matrix: {e}")
    
    # Save model and encoders
    print(f"\n" + "="*50)
    print("SAVING MODEL")
    print("="*50)
    
    os.makedirs("ml_models", exist_ok=True)
    
    try:
        # Save model
        joblib.dump(model, "ml_models/demographic_sentiment_model.joblib")
        print("Model saved: demographic_sentiment_model.joblib")
        
        # Save encoders
        for name, encoder in encoders.items():
            filename = f"ml_models/{name}_encoder.joblib"
            joblib.dump(encoder, filename)
            print(f"Encoder saved: {filename}")
        
        # Save model statistics
        model_stats = {
            'total_samples': total_samples,
            'train_samples': X_train.shape[0],
            'test_samples': X_test.shape[0],
            'train_accuracy': train_accuracy,
            'test_accuracy': test_accuracy,
            'feature_columns': feature_columns,
            'target_classes': target_names.tolist(),
            'class_distribution': class_counts.to_dict(),
            'model_type': 'GaussianNB',
            'training_timestamp': pd.Timestamp.now().isoformat()
        }
        
        joblib.dump(model_stats, "ml_models/model_statistics.joblib")
        print("Model statistics saved: model_statistics.joblib")
        
        # Final summary
        print(f"\n" + "="*50)
        print("TRAINING SUMMARY")
        print("="*50)
        print(f"Model trained successfully!")
        print(f"Dataset: {total_samples} samples, {len(feature_columns)} features")
        print(f"Classes: {len(target_names)} ({', '.join(target_names)})")
        print(f"Accuracy: {test_accuracy:.3f}")
        print(f"Files saved in ml_models/ directory")
        
        return True
        
    except Exception as e:
        print(f"Error saving model: {e}")
        return False

if __name__ == "__main__":
    print("Starting demographic model training...")
    success = train_demographic_model()
    
    if success:
        print("\nTraining completed successfully!")
    else:
        print("\nTraining failed!")