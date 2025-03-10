from flask_openapi3 import APIBlueprint, Tag
from flask import jsonify
from sqlalchemy.orm import Session
from config import SessionLocal
from model import Feedback
from schemas import FeedbackCreate, FeedbackResponse, FeedbackIDParam, PaginationSchema, ListResponseSchema

# Create a new Tag
feedback_tag = Tag(name="Feedback", description="Operations related to feedbacks.")

# Create a new Blueprint
feedback_bp = APIBlueprint('feedback', __name__)

# Create a new feedback
@feedback_bp.post("/feedback", responses={201: FeedbackResponse}, tags=[feedback_tag])
def create_feedback(body: FeedbackCreate):
    """Create a new feedback"""
    db: Session = SessionLocal()
    new_feedback = Feedback(campaign_id=body.campaign_id, message=body.message)
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    db.close()
    return FeedbackResponse.model_validate(new_feedback).model_dump(), 201

# List all feedbacks
@feedback_bp.get("/feedbacks", responses={200: ListResponseSchema[FeedbackResponse]}, tags=[feedback_tag])
def get_feedbacks(query: PaginationSchema):
    """List all feedbacks with pagination"""
    db: Session = SessionLocal()
    total = db.query(Feedback).count()
    feedbacks = db.query(Feedback).offset(query.offset).limit(query.limit).all()
    db.close()
    
    response = ListResponseSchema(
        total=total,
        items=[FeedbackResponse.model_validate(f) for f in feedbacks]
    )
    return jsonify(response.model_dump()), 200

# Get a feedback by ID
@feedback_bp.get("/feedback/<int:feedback_id>", responses={200: FeedbackResponse, 404: {"message": "Feedback not found"}}, tags=[feedback_tag])
def get_feedback(path: FeedbackIDParam):
    """Get a feedback by ID"""
    db: Session = SessionLocal()
    feedback = db.query(Feedback).filter(Feedback.id == path.feedback_id).first()
    db.close()
    if feedback:
        return jsonify(FeedbackResponse.model_validate(feedback).model_dump()), 200
    return jsonify({"message": "Feedback not found"}), 404

# Delete a feedback by ID
@feedback_bp.delete("/feedback/<int:feedback_id>", responses={200: {"message": "Feedback removido"}, 404: {"message": "Feedback not found"}}, tags=[feedback_tag])
def delete_feedback(path: FeedbackIDParam):
    """Delete a feedback by ID"""
    db: Session = SessionLocal()
    feedback = db.query(Feedback).filter(Feedback.id == path.feedback_id).first()
    if feedback:
        db.delete(feedback)
        db.commit()
        db.close()
        return jsonify({"message": "Feedback was removed"}), 200
    db.close()
    return jsonify({"message": "Feedback not found"}), 404
