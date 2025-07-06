from flask_openapi3 import APIBlueprint, Tag
from flask import jsonify, request
from config import SessionLocal
from model import Feedback, Campaign
from schemas import FeedbackCreate, FeedbackResponse, FeedbackIDParam, PaginationSchema, ListResponseSchema

# Create a new Tag for feedback operations
feedback_tag = Tag(name="Feedback", description="Operations related to feedbacks.")

# Create a new API Blueprint for feedback routes
feedback_bp = APIBlueprint('feedback', __name__)

# Create a new feedback
@feedback_bp.post(
    "/feedback",
    responses={
        201: FeedbackResponse,
        404: {"message": "Campaign not found"},
        400: {"message": "Campaign is not active or has reached the maximum number of answers or does not allow multiple answers from the same user"}
    },
    tags=[feedback_tag]
)
def create_feedback(body: FeedbackCreate):
    """
    Create a new feedback for a campaign.
    Validates campaign status and user restrictions before saving feedback.
    """
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
            age_range=body.age_range,
            gender=body.gender,
            education_level=body.education_level,
            country=body.country,
            state=body.state,
            message=body.message,
            user_ip=user_ip,
            user_agent=user_agent
        )
        db.add(new_feedback)
        db.commit()
        db.refresh(new_feedback)
        return jsonify(FeedbackResponse.model_validate(new_feedback).model_dump()), 201

# List all feedbacks with pagination and filters
@feedback_bp.get(
    "/feedbacks",
    responses={200: ListResponseSchema[FeedbackResponse]},
    tags=[feedback_tag]
)
def get_feedbacks(query: PaginationSchema):
    """
    Retrieve a paginated list of all feedbacks.
    Supports offset, limit, and filtering by campaign_id, age_range, gender, education_level, country, state.
    """
    with SessionLocal() as db:
        q = db.query(Feedback)

        # Optional filters from query params
        campaign_id = request.args.get("campaign_id", type=int)
        age_range = request.args.get("age_range")
        gender = request.args.get("gender")
        education_level = request.args.get("education_level")
        country = request.args.get("country")
        state = request.args.get("state")

        if campaign_id is not None:
            q = q.filter(Feedback.campaign_id == campaign_id)
        if age_range:
            q = q.filter(Feedback.age_range == age_range)
        if gender:
            q = q.filter(Feedback.gender == gender)
        if education_level:
            q = q.filter(Feedback.education_level == education_level)
        if country:
            q = q.filter(Feedback.country == country)
        if state:
            q = q.filter(Feedback.state == state)

        total = q.count()
        feedbacks = q.offset(query.offset).limit(query.limit).all()

        response = ListResponseSchema(
            total=total,
            items=[FeedbackResponse.model_validate(f) for f in feedbacks]
        )
        return jsonify(response.model_dump()), 200

# Get a feedback by its ID
@feedback_bp.get(
    "/feedback/<int:feedback_id>",
    responses={
        200: FeedbackResponse,
        404: {"message": "Feedback not found"}
    },
    tags=[feedback_tag]
)
def get_feedback(path: FeedbackIDParam):
    """
    Retrieve a specific feedback by its ID.
    Returns 404 if the feedback does not exist.
    """
    with SessionLocal() as db:
        feedback = db.query(Feedback).filter(Feedback.id == path.feedback_id).first()
        if feedback:
            return jsonify(FeedbackResponse.model_validate(feedback).model_dump()), 200
        return jsonify({"message": "Feedback not found"}), 404

# Delete a feedback by its ID
@feedback_bp.delete(
    "/feedback/<int:feedback_id>",
    responses={
        200: {"message": "Feedback was removed"},
        404: {"message": "Feedback not found"}
    },
    tags=[feedback_tag]
)
def delete_feedback(path: FeedbackIDParam):
    """
    Delete a specific feedback by its ID.
    Returns 404 if the feedback does not exist.
    """
    with SessionLocal() as db:
        feedback = db.query(Feedback).filter(Feedback.id == path.feedback_id).first()
        if feedback:
            db.delete(feedback)
            db.commit()
            return jsonify({"message": "Feedback was removed"}), 200
        return jsonify({"message": "Feedback not found"}), 404
