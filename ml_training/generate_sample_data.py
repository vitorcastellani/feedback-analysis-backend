import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import datetime, timedelta
from config import SessionLocal
from model import Feedback, AgeRange, Gender, EducationLevel, Country, State

# Dados base para geração usando os Enums
AGE_RANGES = [e.name for e in AgeRange]
GENDERS = [e.name for e in Gender]
EDUCATION_LEVELS = [e.name for e in EducationLevel]
COUNTRIES = [e.name for e in Country]
STATES = [e.name for e in State]

# Templates de mensagens por categoria de sentimento
POSITIVE_MESSAGES = [
    "Amei o curso de engenharia de software da puc rio.",
    "Adorei o curso de direito",
    "Me encantó el curso. Fue muy interesante, bien estructurado y me ayudó a aprender muchísimo. ¡Muchas gracias!",
    "I loved the course. It was very interesting, well-structured, and helped me learn a lot. Thank you so much!",
    "Excelente programa, superou minhas expectativas!",
    "Fantastic experience, highly recommend!",
    "O melhor curso que já fiz na vida!",
    "Perfect course structure and amazing professors!",
    "Curso incrível, aprendi muito!",
    "Outstanding quality and content!",
    "Maravilhoso, vale cada centavo!",
    "Amazing learning experience!",
    "Curso excepcional, muito bem organizado!",
    "Great course, learned so much!",
    "Perfeito em todos os aspectos!",
    "Wonderful program, thank you!",
    "Ótima didática e conteúdo!",
    "Excellent professors and materials!",
    "Curso fantástico, recomendo!",
    "Love everything about this course!"
]

NEUTRAL_MESSAGES = [
    "O curso está ok, dentro do esperado.",
    "The course is fine, nothing special.",
    "Curso regular, tem pontos bons e ruins.",
    "It's an average course.",
    "Nem bom nem ruim, mediano.",
    "The course is okay.",
    "Curso padrão, normal.",
    "It's fine, I guess.",
    "Está dentro da média.",
    "Regular course quality.",
    "Não é ruim, mas também não é excelente.",
    "The course is acceptable.",
    "Curso comum, nada demais.",
    "Standard course experience.",
    "É um curso normal.",
    "Nothing extraordinary.",
    "Mediano, dentro do esperado.",
    "Average quality.",
    "Curso básico.",
    "It's okay."
]

NEGATIVE_MESSAGES = [
    "Não gostei do curso, muito confuso.",
    "I didn't like the course, very confusing.",
    "Curso péssimo, perda de tempo.",
    "Terrible course, waste of time.",
    "Muito ruim, não recomendo.",
    "Very bad, don't recommend.",
    "Decepcionante, esperava mais.",
    "Disappointing, expected more.",
    "Curso fraco, professores ruins.",
    "Weak course, bad professors.",
    "Não vale o dinheiro.",
    "Not worth the money.",
    "Conteúdo desatualizado.",
    "Outdated content.",
    "Muito chato e longo.",
    "Very boring and long.",
    "Péssima experiência.",
    "Terrible experience.",
    "Não aprendi nada.",
    "Learned nothing.",
    "Curso horrível.",
    "Horrible course.",
    "Totalmente insatisfeito.",
    "Completely unsatisfied."
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"
]

def generate_ip():
    return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

def generate_datetime():
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 6, 29)
    
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    
    random_date = start_date + timedelta(days=random_days)
    
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    
    return random_date.replace(hour=random_hour, minute=random_minute, second=random_second)

def get_message_by_demographics(age_range, gender, education, country):
    sentiment_weights = [0.6, 0.25, 0.15]
    
    if education in ["master", "phd"]:
        sentiment_weights = [0.7, 0.2, 0.1]
    elif education in ["elementary", "highschool"]:
        sentiment_weights = [0.5, 0.3, 0.2]
    
    if age_range in ["age_18_24", "age_25_34"]:
        sentiment_weights[0] += 0.1
        sentiment_weights[2] -= 0.1
    
    if country in ["brazil", "portugal"]:
        sentiment_weights[0] += 0.05
        sentiment_weights[2] -= 0.05
    
    total = sum(sentiment_weights)
    sentiment_weights = [w/total for w in sentiment_weights]
    
    sentiment = random.choices(
        ["positive", "neutral", "negative"], 
        weights=sentiment_weights
    )[0]
    
    if sentiment == "positive":
        return random.choice(POSITIVE_MESSAGES)
    elif sentiment == "neutral":
        return random.choice(NEUTRAL_MESSAGES)
    else:
        return random.choice(NEGATIVE_MESSAGES)

def get_realistic_state_for_country(country):
    """Retorna estados realistas baseado no país"""
    if country == "brazil":
        return random.choice(["RJ", "SP", "MG", "RS", "PR", "SC", "BA", "GO", "PE", "CE", "DF"])
    else:
        return "other"

def insert_feedback_to_db(num_records=5000, campaign_id=1, batch_size=100):
    with SessionLocal() as db:
        total_inserted = 0
        batch = []
        
        for i in range(num_records):
            age_range = random.choice(AGE_RANGES)
            gender = random.choice(GENDERS)
            education = random.choice(EDUCATION_LEVELS)
            country = random.choice(COUNTRIES)
            
            # Estado baseado no país para ser mais realista
            state = get_realistic_state_for_country(country)
            
            message = get_message_by_demographics(age_range, gender, education, country)
            user_ip = generate_ip()
            user_agent = random.choice(USER_AGENTS)
            created_at = generate_datetime()
            
            feedback = Feedback(
                age_range=age_range,
                gender=gender,
                education_level=education,
                country=country,
                state=state,
                message=message,
                campaign_id=campaign_id,
                user_ip=user_ip,
                user_agent=user_agent,
                created_at=created_at
            )
            
            batch.append(feedback)
            
            if len(batch) >= batch_size:
                try:
                    db.add_all(batch)
                    db.commit()
                    total_inserted += len(batch)
                    print(f"Inserted {total_inserted} / {num_records} records...")
                    batch = []
                except Exception as e:
                    print(f"Error inserting batch: {e}")
                    db.rollback()
                    batch = []
        
        if batch:
            try:
                db.add_all(batch)
                db.commit()
                total_inserted += len(batch)
                print(f"Inserted final batch. Total: {total_inserted} records")
            except Exception as e:
                print(f"Error inserting final batch: {e}")
                db.rollback()
    
    print(f"Successfully inserted {total_inserted} feedback records for campaign {campaign_id}")
    return total_inserted

if __name__ == "__main__":
    print("Starting data generation...")
    print(f"Available age ranges: {AGE_RANGES}")
    print(f"Available genders: {GENDERS}")
    print(f"Available education levels: {EDUCATION_LEVELS}")
    print(f"Available countries: {COUNTRIES}")
    print(f"Available states: {STATES}")
    
    insert_feedback_to_db(2500, campaign_id=4)
    
    print("Data generation completed!")