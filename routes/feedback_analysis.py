import re
from flask_openapi3 import APIBlueprint, Tag
from flask import jsonify
from model import Feedback, FeedbackAnalysis
from schemas import FeedbackAnalysisResponse, FeedbackAnalysisCreate, FeedbackCampaignAnalysisRequest, FeedbackProgressResponse
from config import SessionLocal
from services import feedback_queue, processing_feedbacks
import subprocess
from utils import get_star_rating, analyze_sentiment, predict_sentiment

# Create a new Tag for the API documentation
feedback_analysis_tag = Tag(
    name="Feedback Analysis",
    description="Operations related to feedback sentiment analysis."
)

# Create a new API Blueprint for feedback analysis routes
feedback_analysis_bp = APIBlueprint('feedback_analysis', __name__)

@feedback_analysis_bp.post(
    "/feedback/analyze",
    responses={201: FeedbackAnalysisResponse, 404: {"message": "Feedback not found"}},
    tags=[feedback_analysis_tag]
)
def analyze_feedback(body: FeedbackAnalysisCreate):
    """
    Analyze the sentiment of a feedback message in multiple languages and store the result.

    Args:
        body (FeedbackAnalysisCreate): The request body containing the feedback ID.

    Returns:
        Response: JSON response with the analysis result or an error message.
    """
    with SessionLocal() as db:
        # Retrieve the feedback by ID
        feedback = db.query(Feedback).filter(Feedback.id == body.feedback_id).first()

        if not feedback:
            return jsonify({"message": "Feedback not found"}), 404

        # Check if the feedback has already been analyzed
        existing_analysis = db.query(FeedbackAnalysis).filter(
            FeedbackAnalysis.feedback_id == body.feedback_id
        ).first()
        if existing_analysis:
            return jsonify(
                FeedbackAnalysisResponse.model_validate(existing_analysis.__dict__).model_dump()
            ), 200

        # Perform sentiment analysis
        sentiment_score, sentiment_category, detected_language, word_count, feedback_length = analyze_sentiment(feedback.message)
        star_rating = get_star_rating(sentiment_score)

        # Create a new FeedbackAnalysis entry
        new_analysis = FeedbackAnalysis(
            feedback_id=body.feedback_id,
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

        # Prepare the response
        response = FeedbackAnalysisResponse.model_validate(new_analysis.__dict__).model_dump()

        return jsonify(response), 201

@feedback_analysis_bp.post(
    "/feedback/analyze-all",
    responses={200: {"message": "Analysis started"}},
    tags=[feedback_analysis_tag]
)
def analyze_all_feedbacks(body: FeedbackCampaignAnalysisRequest):
    """
    Analyze all feedbacks for specific campaigns that have not been analyzed yet.

    Args:
        body (FeedbackCampaignAnalysisRequest): The request body containing campaign IDs.

    Returns:
        Response: JSON response indicating the number of feedbacks added to the queue or an error message.
    """
    campaign_ids = body.campaign_ids
    if not campaign_ids:
        return jsonify({"message": "Campaign IDs are required"}), 400

    with SessionLocal() as db:
        # Fetch all feedbacks for the given campaigns that do not have an associated analysis
        feedbacks_to_analyze = (
            db.query(Feedback)
            .outerjoin(FeedbackAnalysis)
            .filter(Feedback.campaign_id.in_(campaign_ids), FeedbackAnalysis.id == None)
            .all()
        )

        if not feedbacks_to_analyze:
            return jsonify({"message": "No feedbacks to analyze for the given campaigns"}), 200

        # Add feedbacks to the processing queue
        added_to_queue = 0
        for feedback in feedbacks_to_analyze:
            if feedback.id not in processing_feedbacks:
                feedback_queue.put(feedback.id)
                processing_feedbacks.add(feedback.id)
                added_to_queue += 1

        return jsonify({"message": f"Added {added_to_queue} feedback(s) to the processing queue"}), 200

@feedback_analysis_bp.get(
    "/feedback/progress",
    responses={200: FeedbackProgressResponse},
    tags=[feedback_analysis_tag]
)
def get_feedback_progress():
    """
    Get the current progress of the feedback analysis queue.

    Returns:
        Response: JSON response with the queue size and the number of feedbacks being processed.
    """
    queue_size = feedback_queue.qsize()
    return jsonify({"queue_size": queue_size, "processing": len(processing_feedbacks)}), 200

@feedback_analysis_bp.post(
    "/feedback/classify-demographic",
    responses={200: {"message": "Success"}},
    tags=[feedback_analysis_tag]
)
def classify_feedback_demographic(body: FeedbackAnalysisCreate):
    with SessionLocal() as db:
        feedback = db.query(Feedback).filter(Feedback.id == body.feedback_id).first()
        if not feedback:
            return jsonify({"message": "Feedback not found"}), 404

        result = predict_sentiment(
            message=feedback.message,
            gender=feedback.gender.value if feedback.gender else "unknown",
            age_range=feedback.age_range.value if feedback.age_range else "unknown",
            education_level=feedback.education_level.value if feedback.education_level else "unknown",
            detected_language=feedback.detected_language if hasattr(feedback, 'detected_language') and feedback.detected_language else "pt"
        )

        return jsonify(result), 200