from flask_openapi3 import APIBlueprint, Tag
from flask import jsonify
from config import SessionLocal
from model import Campaign, Feedback
from schemas import (
    CampaignResponse,
    CampaignIDParam,
    PaginationSchema,
    ListResponseSchema,
    CampaignCreate,
    CampaignShortCodeParam,
)
from utils import generate_short_code

# Create a new Tag for grouping campaign-related operations in the API documentation
campaign_tag = Tag(name="Campaign", description="Operations related to campaigns.")

# Create a new API Blueprint for campaign routes
campaign_bp = APIBlueprint("campaign", __name__)


# Endpoint to create a new campaign
@campaign_bp.post(
    "/campaign",
    responses={201: CampaignResponse},
    tags=[campaign_tag],
)
def create_campaign(body: CampaignCreate):
    """
    Create a new campaign.
    """
    short_code = generate_short_code()  # Generate a unique short code for the campaign
    with SessionLocal() as db:
        # Create a new campaign instance
        new_campaign = Campaign(
            name=body.name,
            description=body.description,
            active=body.active,
            multiple_answers_from_user=body.multiple_answers_from_user,
            max_answers=body.max_answers,
            short_code=short_code,
        )
        db.add(new_campaign)  # Add the campaign to the database session
        db.commit()  # Commit the transaction to save the campaign
        db.refresh(new_campaign)  # Refresh the instance to get the updated data
        return CampaignResponse.model_validate(new_campaign).model_dump(), 201


# Endpoint to list all campaigns with pagination
@campaign_bp.get(
    "/campaigns",
    responses={200: ListResponseSchema[CampaignResponse]},
    tags=[campaign_tag],
)
def get_campaigns(query: PaginationSchema):
    """
    List all campaigns with pagination.
    """
    with SessionLocal() as db:
        # Query campaigns with pagination
        campaigns = db.query(Campaign).offset(query.offset).limit(query.limit).all()
        items = []
        for campaign in campaigns:
            # Count the number of feedback entries associated with the campaign
            feedback_count = db.query(Feedback).filter(Feedback.campaign_id == campaign.id).count()
            # Add feedback count to the campaign data
            campaign_data = CampaignResponse.model_validate(
                {**campaign.__dict__, "feedback_count": feedback_count}
            ).model_dump()
            items.append(campaign_data)
        return jsonify({"items": items, "total": len(items)})


# Endpoint to retrieve a campaign by its ID
@campaign_bp.get(
    "/campaign/<int:campaign_id>",
    responses={200: CampaignResponse, 404: {"message": "Campaign not found"}},
    tags=[campaign_tag],
)
def get_campaign(path: CampaignIDParam):
    """
    Retrieve a campaign by its ID.
    """
    with SessionLocal() as db:
        # Query the campaign by its ID
        campaign = db.query(Campaign).filter(Campaign.id == path.campaign_id).first()
        if campaign:
            # Count the number of feedback entries associated with the campaign
            feedback_count = db.query(Feedback).filter(Feedback.campaign_id == campaign.id).count()
            # Add feedback count to the campaign data
            campaign = {**campaign.__dict__, "feedback_count": feedback_count}
            return jsonify(CampaignResponse.model_validate(campaign).model_dump()), 200
        return jsonify({"message": "Campaign not found"}), 404


# Endpoint to retrieve a campaign by its short code
@campaign_bp.get(
    "/campaign/short_code/<string:short_code>",
    responses={200: CampaignResponse, 404: {"message": "Campaign not found"}},
    tags=[campaign_tag],
)
def get_campaign_by_short_code(path: CampaignShortCodeParam):
    """
    Retrieve a campaign by its short code.
    """
    with SessionLocal() as db:
        # Query the campaign by its short code
        campaign = db.query(Campaign).filter(Campaign.short_code == path.short_code).first()
        if campaign:
            # Count the number of feedback entries associated with the campaign
            feedback_count = db.query(Feedback).filter(Feedback.campaign_id == campaign.id).count()
            # Add feedback count to the campaign data
            campaign = {**campaign.__dict__, "feedback_count": feedback_count}
            return jsonify(CampaignResponse.model_validate(campaign).model_dump()), 200
        return jsonify({"message": "Campaign not found"}), 404


# Endpoint to update a campaign by its ID
@campaign_bp.put(
    "/campaign/<int:campaign_id>",
    responses={200: CampaignResponse, 404: {"message": "Campaign not found"}},
    tags=[campaign_tag],
)
def update_campaign(path: CampaignIDParam, body: CampaignCreate):
    """
    Update a campaign by its ID.
    """
    with SessionLocal() as db:
        # Query the campaign by its ID
        campaign = db.query(Campaign).filter(Campaign.id == path.campaign_id).first()
        if campaign:
            # Update the campaign fields with the new data
            campaign.name = body.name
            campaign.description = body.description
            campaign.active = body.active
            campaign.multiple_answers_from_user = body.multiple_answers_from_user
            campaign.max_answers = body.max_answers
            db.commit()  # Commit the transaction to save the changes
            db.refresh(campaign)  # Refresh the instance to get the updated data
            return CampaignResponse.model_validate(campaign).model_dump(), 200
        return jsonify({"message": "Campaign not found"}), 404


# Endpoint to delete a campaign by its ID
@campaign_bp.delete(
    "/campaign/<int:campaign_id>",
    responses={200: {"message": "Campaign deleted"}, 404: {"message": "Campaign not found"}},
    tags=[campaign_tag],
)
def delete_campaign(path: CampaignIDParam):
    """
    Delete a campaign by its ID.
    """
    with SessionLocal() as db:
        # Query the campaign by its ID
        campaign = db.query(Campaign).filter(Campaign.id == path.campaign_id).first()
        if campaign:
            db.delete(campaign)  # Delete the campaign from the database
            db.commit()  # Commit the transaction to save the changes
            return jsonify({"message": "Campaign deleted"}), 200
        return jsonify({"message": "Campaign not found"}), 404
