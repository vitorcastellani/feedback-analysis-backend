import sys
import os
import random
import pandas as pd
from datetime import datetime, timedelta
from config import SessionLocal
from model import Feedback, AgeRange, Gender, EducationLevel, Country, State

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

AGE_RANGES = [e.name for e in AgeRange]
GENDERS = [e.name for e in Gender]
EDUCATION_LEVELS = [e.name for e in EducationLevel]
COUNTRIES = [e.name for e in Country]

try:
    messages_df = pd.read_csv(os.path.join('ml_data', 'feedback_messages.csv'))
except FileNotFoundError:
    messages_df = pd.read_csv(os.path.join('..', 'ml_data', 'feedback_messages.csv'))
except Exception as e:
    print(f"Error reading feedback_messages.csv: {e}")
    raise

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0)..."
]

def generate_ip():
    return ".".join(str(random.randint(1, 255)) for _ in range(4))

def generate_datetime():
    start = datetime(2024, 1, 1)
    end = datetime(2025, 6, 29)
    delta = end - start
    rand_days = random.randint(0, delta.days)
    rand_time = timedelta(
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    return start + timedelta(days=rand_days) + rand_time

def determine_sentiment(age, gender, education, country):
    weights = [0.6, 0.25, 0.15]

    if education in ["master", "phd"]:
        weights = [0.7, 0.2, 0.1]
    elif education in ["elementary", "highschool"]:
        weights = [0.5, 0.3, 0.2]

    if age in ["age_18_24", "age_25_34"]:
        weights[0] += 0.1
        weights[2] -= 0.1

    if country in ["brazil", "portugal"]:
        weights[0] += 0.05
        weights[2] -= 0.05

    total = sum(weights)
    normalized = [w / total for w in weights]
    return random.choices(["positive", "neutral", "negative"], weights=normalized)[0]

def get_state_for_country(country):
    return random.choice(["RJ", "SP", "MG", "RS", "BA", "PE", "DF"]) if country == "brazil" else "other"

def insert_feedback(num_records=5000, campaign_id=1, batch_size=100):
    with SessionLocal() as db:
        inserted = 0
        batch = []

        for _ in range(num_records):
            age = random.choice(AGE_RANGES)
            gender = random.choice(GENDERS)
            education = random.choice(EDUCATION_LEVELS)
            country = random.choice(COUNTRIES)
            state = get_state_for_country(country)
            sentiment = determine_sentiment(age, gender, education, country)
            
            message = messages_df[messages_df['sentiment'] == sentiment]['message'].sample(n=1).values[0]

            feedback = Feedback(
                age_range=age,
                gender=gender,
                education_level=education,
                country=country,
                state=state,
                message=message,
                campaign_id=campaign_id,
                user_ip=generate_ip(),
                user_agent=random.choice(USER_AGENTS),
                created_at=generate_datetime()
            )

            batch.append(feedback)

            if len(batch) >= batch_size:
                try:
                    db.add_all(batch)
                    db.commit()
                    inserted += len(batch)
                    print(f"Inserted {inserted}/{num_records}")
                    batch = []
                except Exception as e:
                    print(f"Batch insert error: {e}")
                    db.rollback()
                    batch = []

        if batch:
            try:
                db.add_all(batch)
                db.commit()
                inserted += len(batch)
                print(f"Inserted final batch. Total: {inserted}")
            except Exception as e:
                print(f"Final batch error: {e}")
                db.rollback()

    print(f"Successfully inserted {inserted} feedback records for campaign {campaign_id}")
    return inserted

if __name__ == "__main__":
    print("Starting data generation...")
    insert_feedback(num_records=500, campaign_id=1)
    insert_feedback(num_records=500, campaign_id=2)
    insert_feedback(num_records=500, campaign_id=3)
    insert_feedback(num_records=500, campaign_id=4)
    insert_feedback(num_records=500, campaign_id=5)
    print("Data generation completed!")
