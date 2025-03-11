from flask_openapi3 import APIBlueprint, Tag
from flask import jsonify
import random
import string
from sqlalchemy.orm import Session
from config import SessionLocal
from model import Campaign
from schemas import CampaignResponse, CampaignIDParam, PaginationSchema, ListResponseSchema, CampaignCreate

# Create a new Tag
campaign_tag = Tag(name="Campaign", description="Operations related to campaigns.")

# Create a new Blueprint
campaign_bp = APIBlueprint('campaign', __name__)

# Create a short code for the campaign using random characters with case sensitivity and numbers
def generate_short_code(length: int = 6) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Create a new campaign
@campaign_bp.post("/campaign", responses={201: CampaignResponse}, tags=[campaign_tag])
def create_campaign(body: CampaignCreate):
    """Create a new campaign"""
    short_code = generate_short_code()
    with SessionLocal() as db:
        new_campaign = Campaign(
            name=body.name,
            description=body.description,
            active=body.active,
            multiple_answers_from_user=body.multiple_answers_from_user,
            max_answers=body.max_answers,
            short_code=short_code
        )
        db.add(new_campaign)
        db.commit()
        db.refresh(new_campaign)
        return CampaignResponse.model_validate(new_campaign).model_dump(), 201

# List all campaigns
@campaign_bp.get("/campaigns", responses={200: ListResponseSchema[CampaignResponse]}, tags=[campaign_tag])
def get_campaigns(query: PaginationSchema):
    """List all campaigns with pagination"""
    with SessionLocal() as db:
        total = db.query(Campaign).count()
        campaigns = db.query(Campaign).offset(query.offset).limit(query.limit).all()
        response = ListResponseSchema(
            total=total,
            items=[CampaignResponse.model_validate(c) for c in campaigns]
        )
        return jsonify(response.model_dump()), 200

# Get a campaign by ID
@campaign_bp.get("/campaign/<int:campaign_id>", responses={200: CampaignResponse, 404: {"message": "Campaign not found"}}, tags=[campaign_tag])
def get_campaign(path: CampaignIDParam):
    """Get a campaign by ID"""
    with SessionLocal() as db:
        campaign = db.query(Campaign).filter(Campaign.id == path.campaign_id).first()
        if campaign:
            return jsonify(CampaignResponse.model_validate(campaign).model_dump()), 200
        return jsonify({"message": "Campaign not found"}), 404

# Update a campaign by ID
@campaign_bp.put("/campaign/<int:campaign_id>", responses={200: CampaignResponse, 404: {"message": "Campaign not found"}}, tags=[campaign_tag])
def update_campaign(path: CampaignIDParam, body: CampaignCreate):
    """Update a campaign by ID"""
    with SessionLocal() as db:
        campaign = db.query(Campaign).filter(Campaign.id == path.campaign_id).first()
        if campaign:
            campaign.name = body.name
            campaign.description = body.description
            campaign.active = body.active
            campaign.multiple_answers_from_user = body.multiple_answers_from_user
            campaign.max_answers = body.max_answers
            db.commit()
            db.refresh(campaign)
            return CampaignResponse.model_validate(campaign).model_dump(), 200
        return jsonify({"message": "Campaign not found"}), 404

# Delete a campaign by ID
@campaign_bp.delete("/campaign/<int:campaign_id>", responses={200: {"message": "Campaign deleted"}, 404: {"message": "Campaign not found"}}, tags=[campaign_tag])
def delete_campaign(path: CampaignIDParam):
    """Delete a campaign by ID"""
    with SessionLocal() as db:
        campaign = db.query(Campaign).filter(Campaign.id == path.campaign_id).first()
        if campaign:
            db.delete(campaign)
            db.commit()
            return jsonify({"message": "Campaign deleted"}), 200
        return jsonify({"message": "Campaign not found"}), 404
