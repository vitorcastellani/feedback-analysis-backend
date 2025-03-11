from flask_openapi3 import APIBlueprint, Tag
from flask import jsonify, request
from sqlalchemy.orm import Session
from config import SessionLocal
from model import Feedback, Campaign
from schemas import FeedbackCreate, FeedbackResponse, FeedbackIDParam, PaginationSchema, ListResponseSchema

# Create a new Tag
feedback_tag = Tag(name="Feedback", description="Operations related to feedbacks.")

# Create a new Blueprint
feedback_bp = APIBlueprint('feedback', __name__)

# Create a new feedback
@feedback_bp.post("/feedback", responses={201: FeedbackResponse, 404: {"message": "Campaign not found"}, 400: {"message": "Campaign is not active or has reached the maximum number of answers or does not allow multiple answers from the same user"}}, tags=[feedback_tag])
def create_feedback(body: FeedbackCreate):
    """Create a new feedback"""
    with SessionLocal() as db:
        campaign = db.query(Campaign).filter(Campaign.id == body.campaign_id).first()
        if not campaign:
            return jsonify({"message": "Campaign not found"}), 404
        if not campaign.active:
            return jsonify({"message": "Campaign is not active"}), 400
        if campaign.max_answers > 0 and db.query(Feedback).filter(Feedback.campaign_id == body.campaign_id).count() >= campaign.max_answers:
            return jsonify({"message": "Campaign has reached the maximum number of answers"}), 400
        user_ip = request.remote_addr
        user_agent = request.user_agent.string
        if not campaign.multiple_answers_from_user:
            existing_feedback = db.query(Feedback).filter(
                Feedback.campaign_id == body.campaign_id,
                Feedback.user_ip == user_ip
            ).first()
            if existing_feedback:
                return jsonify({"message": "Campaign does not allow multiple answers from the same user"}), 400
        new_feedback = Feedback(
            campaign_id=body.campaign_id, 
            message=body.message, 
            user_ip=user_ip, 
            user_agent=user_agent
        )
        db.add(new_feedback)
        db.commit()
        db.refresh(new_feedback)
        return jsonify(FeedbackResponse.model_validate(new_feedback).model_dump()), 201

# List all feedbacks
@feedback_bp.get("/feedbacks", responses={200: ListResponseSchema[FeedbackResponse]}, tags=[feedback_tag])
def get_feedbacks(query: PaginationSchema):
    """List all feedbacks with pagination"""
    with SessionLocal() as db:
        total = db.query(Feedback).count()
        feedbacks = db.query(Feedback).offset(query.offset).limit(query.limit).all()
        
        response = ListResponseSchema(
            total=total,
            items=[FeedbackResponse.model_validate(f) for f in feedbacks]
        )
        return jsonify(response.model_dump()), 200

# Get a feedback by ID
@feedback_bp.get("/feedback/<int:feedback_id>", responses={200: FeedbackResponse, 404: {"message": "Feedback not found"}}, tags=[feedback_tag])
def get_feedback(path: FeedbackIDParam):
    """Get a feedback by ID"""
    with SessionLocal() as db:
        feedback = db.query(Feedback).filter(Feedback.id == path.feedback_id).first()
        if feedback:
            return jsonify(FeedbackResponse.model_validate(feedback).model_dump()), 200
        return jsonify({"message": "Feedback not found"}), 404

# Delete a feedback by ID
@feedback_bp.delete("/feedback/<int:feedback_id>", responses={200: {"message": "Feedback was removed"}, 404: {"message": "Feedback not found"}}, tags=[feedback_tag])
def delete_feedback(path: FeedbackIDParam):
    """Delete a feedback by ID"""
    with SessionLocal() as db:
        feedback = db.query(Feedback).filter(Feedback.id == path.feedback_id).first()
        if feedback:
            db.delete(feedback)
            db.commit()
            return jsonify({"message": "Feedback was removed"}), 200
        return jsonify({"message": "Feedback not found"}), 404
