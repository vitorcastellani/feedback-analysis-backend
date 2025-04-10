from threading import Thread
from queue import Queue
from config import SessionLocal
from model import Feedback, FeedbackAnalysis
from utils import analyze_sentiment, get_star_rating

# Queue to process feedbacks
feedback_queue = Queue()
processing_feedbacks = set()

def process_feedback_queue():
    """
    Processes feedback messages from a queue in a worker thread.
    This function continuously retrieves feedback IDs from a queue, processes
    the corresponding feedback messages, performs sentiment analysis, and
    stores the results in the database. It stops processing when a `None`
    value is retrieved from the queue, which acts as a termination signal.
    
    Workflow:
    1. Retrieves a feedback ID from the queue.
    2. Fetches the corresponding feedback record from the database.
    3. Performs sentiment analysis on the feedback message, extracting:
       - Sentiment score
       - Sentiment category
       - Detected language
       - Word count
       - Feedback length
    4. Calculates a star rating based on the sentiment score.
    5. Creates a new `FeedbackAnalysis` entry in the database with the analysis results.
    6. Commits the changes to the database and refreshes the new entry.
    7. Removes the feedback ID from the processing set and marks the task as done.
    
    Notes:
    - This function assumes the existence of a `feedback_queue` for task management,
      a `processing_feedbacks` set to track in-progress feedbacks, and a `SessionLocal`
      database session factory.
    - The function runs indefinitely until a stop signal (`None`) is encountered.
    
    Raises:
        Any exceptions raised during database operations or sentiment analysis
        will propagate to the caller.
    """
    with SessionLocal() as db:
        while True:
            feedback_id = feedback_queue.get()
            if feedback_id is None:  # Stop signal
                break

            # Retrieve the feedback by ID
            feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
            if feedback:
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

# Start the worker thread for processing the feedback queue
worker_thread = Thread(target=process_feedback_queue, daemon=True)
worker_thread.start()