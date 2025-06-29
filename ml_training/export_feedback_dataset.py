import csv
from config import SessionLocal
from model import Feedback, FeedbackAnalysis

OUTPUT_FILE = "ml_data/hierarchical_feedback_dataset.csv"

def export_hierarchical_feedback_data():
    with SessionLocal() as db:
        records = db.query(
            Feedback.campaign_id,
            Feedback.gender,
            Feedback.age_range,
            Feedback.education_level,
            Feedback.country,
            Feedback.state,
            FeedbackAnalysis.sentiment_category
        ).join(
            FeedbackAnalysis, Feedback.id == FeedbackAnalysis.feedback_id
        ).all()

        with open(OUTPUT_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["campaign_id", "gender", "age_range", "education_level", "country", "state", "sentiment_category"])
            for row in records:
                writer.writerow([
                    row.campaign_id,
                    row.gender.value if row.gender else "unknown",
                    row.age_range.value if row.age_range else "unknown", 
                    row.education_level.value if row.education_level else "unknown",
                    row.country.value if row.country else "unknown",
                    row.state.value if row.state else "unknown",
                    row.sentiment_category.value
                ])

        print(f"Exported {len(records)} rows to {OUTPUT_FILE}")

if __name__ == "__main__":
    export_hierarchical_feedback_data()