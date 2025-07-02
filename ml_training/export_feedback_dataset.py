import pandas as pd
from config import SessionLocal
from model import Feedback, FeedbackAnalysis

def export_feedback_dataset():
    """Export feedback data with demographic info and sentiment scores for training"""
    
    try:
        with SessionLocal() as db:
            # Query with sentiment score included
            records = db.query(
                Feedback.id,
                Feedback.campaign_id,
                Feedback.gender,
                Feedback.age_range,
                Feedback.education_level,
                Feedback.country,
                Feedback.state,
                Feedback.message,
                FeedbackAnalysis.sentiment_category,
                FeedbackAnalysis.sentiment,  # VADER score (-1 to 1)
                FeedbackAnalysis.word_count,
                FeedbackAnalysis.feedback_length,
                FeedbackAnalysis.detected_language
            ).join(
                FeedbackAnalysis, Feedback.id == FeedbackAnalysis.feedback_id
            ).all()

            if not records:
                print("No feedback data found in database!")
                return False

            print(f"Found {len(records)} feedback records")

            # Convert to DataFrame with sentiment score
            data = []
            for record in records:
                data.append({
                    'feedback_id': record.id,
                    'campaign_id': record.campaign_id,
                    'gender': record.gender.value if record.gender else "unknown",
                    'age_range': record.age_range.value if record.age_range else "unknown", 
                    'education_level': record.education_level.value if record.education_level else "unknown",
                    'country': record.country.value if record.country else "unknown",
                    'state': record.state.value if record.state else "unknown",
                    'message': record.message,
                    'sentiment_category': record.sentiment_category.value,
                    'sentiment_score': float(record.sentiment),  # VADER score
                    'word_count': record.word_count,
                    'feedback_length': record.feedback_length,
                    'detected_language': record.detected_language
                })

            df = pd.DataFrame(data)
            
            # Create output directory
            import os
            os.makedirs("ml_data", exist_ok=True)
            
            # Save enhanced dataset
            output_file = "ml_data/feedback_dataset.csv"
            df.to_csv(output_file, index=False)
            
            print(f"Dataset exported to: {output_file}")
            print(f"Columns: {list(df.columns)}")
            print(f"Shape: {df.shape}")
            
            # Show sentiment score statistics
            print(f"\nSentiment Score Statistics:")
            print(df['sentiment_score'].describe())
            
            print(f"\nSentiment Distribution:")
            print(df['sentiment_category'].value_counts())
            
            return True
            
    except Exception as e:
        print(f"Error exporting dataset: {e}")
        return False

if __name__ == "__main__":
    export_feedback_dataset()