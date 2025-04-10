from queue import Queue
from threading import Thread
from config import SessionLocal
from model import Feedback, FeedbackAnalysis
from utils import analyze_sentiment, get_star_rating

# Queue to process feedbacks
feedback_queue = Queue()
processing_feedbacks = set()

def process_feedback_queue():
    """
    Worker function to process feedbacks in the queue.
    This function runs in a separate thread and processes feedbacks one by one.
    """
    with SessionLocal() as db:
        while True:
            feedback_id = feedback_queue.get()
            if feedback_id is None:  # Stop signal
                break

            # Retrieve the feedback by ID
            feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
            if feedback:
                # Check if the feedback has already been analyzed
                existing_analysis = db.query(FeedbackAnalysis).filter(
                    FeedbackAnalysis.feedback_id == feedback_id
                ).first()
                if existing_analysis:
                    # Skip processing if analysis already exists
                    processing_feedbacks.discard(feedback_id)
                    feedback_queue.task_done()
                    continue

                # Perform sentiment analysis
                sentiment_score, sentiment_category, detected_language, word_count, feedback_length = analyze_sentiment(feedback.message)
                star_rating = get_star_rating(sentiment_score)

                # Create a new FeedbackAnalysis entry
                new_analysis = FeedbackAnalysis(
                    feedback_id=feedback.id,
                    sentiment=sentiment_score,
                    sentiment_category=sentiment_category,
                    star_rating=star_rating,
                    detected_language=detected_language,
                    word_count=word_count,
                    feedback_length=feedback_length
                )
                db.add(new_analysis)
                db.commit()
                db.refresh(new_analysis)

            # Remove the feedback ID from the processing set
            processing_feedbacks.discard(feedback_id)
            feedback_queue.task_done()

# Start the worker thread
worker_thread = Thread(target=process_feedback_queue, daemon=True)
worker_thread.start()