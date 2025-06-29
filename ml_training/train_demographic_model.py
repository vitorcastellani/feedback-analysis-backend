import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
import numpy as np

df = pd.read_csv("ml_data/feedback_dataset.csv")

print(f"Dataset shape: {df.shape}")
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

gender_encoder = LabelEncoder()
age_encoder = LabelEncoder()
education_encoder = LabelEncoder()
country_encoder = LabelEncoder()
state_encoder = LabelEncoder()
label_encoder = LabelEncoder()

df["gender"] = gender_encoder.fit_transform(df["gender"])
df["age_range"] = age_encoder.fit_transform(df["age_range"])
df["education_level"] = education_encoder.fit_transform(df["education_level"])
df["country"] = country_encoder.fit_transform(df["country"])
df["state"] = state_encoder.fit_transform(df["state"])
df["sentiment_category"] = label_encoder.fit_transform(df["sentiment_category"])

X = df[["gender", "age_range", "education_level", "country", "state"]]
y = df["sentiment_category"]

if use_test_split:
    if use_stratify:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
else:
    X_train, y_train = X, y
    X_test, y_test = X, y

model = GaussianNB()
model.fit(X_train, y_train)

if use_test_split and len(X_test) > 0:
    y_pred = model.predict(X_test)
    print(f"\nTest Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    
    unique_classes_test = np.unique(y_test)
    unique_classes_pred = np.unique(y_pred)
    
    if len(unique_classes_test) > 1 and len(unique_classes_pred) > 1:
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, zero_division=0))
    else:
        print("Skipping classification report: insufficient class diversity in test set")
else:
    print("No test evaluation performed due to small dataset size.")

train_pred = model.predict(X_train)
print(f"\nTrain Accuracy: {accuracy_score(y_train, train_pred):.4f}")

os.makedirs("ml_models", exist_ok=True)
joblib.dump(model, "ml_models/demographic_sentiment_model.joblib")
joblib.dump(gender_encoder, "ml_models/gender_encoder.joblib")
joblib.dump(age_encoder, "ml_models/age_encoder.joblib")
joblib.dump(education_encoder, "ml_models/education_encoder.joblib")
joblib.dump(country_encoder, "ml_models/country_encoder.joblib")
joblib.dump(state_encoder, "ml_models/state_encoder.joblib")
joblib.dump(label_encoder, "ml_models/label_encoder.joblib")

print("\nModel and encoders saved successfully!")
print(f"Classes found: {label_encoder.classes_}")