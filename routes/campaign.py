from flask_openapi3 import APIBlueprint, Tag
from flask import jsonify
from sqlalchemy.orm import Session
from config import SessionLocal
from model import Campaign
from schemas import CampaignResponse, CampaignIDParam, PaginationSchema, ListResponseSchema, CampaignCreate

# Create a new Tag
campaign_tag = Tag(name="Campaign", description="Operations related to campaigns.")

# Create a new Blueprint
campaign_bp = APIBlueprint('campaign', __name__)

# Create a new campaign
@campaign_bp.post("/campaign", responses={201: CampaignResponse}, tags=[campaign_tag])
def create_campaign(body: CampaignCreate):
    """Create a new campaign"""
    db: Session = SessionLocal()
    new_campaign = Campaign(name=body.name, description=body.description)
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)
    db.close()
    return CampaignResponse.model_validate(new_campaign).model_dump(), 201

# List all campaigns
@campaign_bp.get("/campaigns", responses={200: ListResponseSchema[CampaignResponse]}, tags=[campaign_tag])
def get_campaigns(query: PaginationSchema):
    """List all campaigns with pagination"""
    db: Session = SessionLocal()
    total = db.query(Campaign).count()
    campaigns = db.query(Campaign).offset(query.offset).limit(query.limit).all()
    db.close()
    
    response = ListResponseSchema(
        total=total,
        items=[CampaignResponse.model_validate(c) for c in campaigns]
    )
    return jsonify(response.model_dump()), 200

# Get a campaign by ID
@campaign_bp.get("/campaign/<int:campaign_id>", responses={200: CampaignResponse, 404: {"message": "Campaign not found"}}, tags=[campaign_tag])
def get_campaign(path: CampaignIDParam):
    """Get a campaign by ID"""
    db: Session = SessionLocal()
    campaign = db.query(Campaign).filter(Campaign.id == path.campaign_id).first()
    db.close()
    if campaign:
        return jsonify(CampaignResponse.model_validate(campaign).model_dump()), 200
    return jsonify({"message": "Campaign not found"}), 404

# Delete a campaign by ID
@campaign_bp.delete("/campaign/<int:campaign_id>", responses={200: {"message": "Campaign deleted"}, 404: {"message": "Campaign not found"}}, tags=[campaign_tag])
def delete_campaign(path: CampaignIDParam):
    """Delete a campaign by ID"""
    db: Session = SessionLocal()
    campaign = db.query(Campaign).filter(Campaign.id == path.campaign_id).first()
    if campaign:
        db.delete(campaign)
        db.commit()
        db.close()
        return jsonify({"message": "Campaign deleted"}), 200
    db.close()
    return jsonify({"message": "Campaign not found"}), 404
