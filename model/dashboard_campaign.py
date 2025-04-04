from sqlalchemy import Column, Integer, ForeignKey, Table
from model import BaseModel

# Dashboard-Campaign association table
dashboard_campaign = Table(
    "dashboard_campaign",
    BaseModel.metadata,
    Column("dashboard_id", Integer, ForeignKey("dashboards.id", ondelete="CASCADE"), primary_key=True),
    Column("campaign_id", Integer, ForeignKey("campaign.id", ondelete="CASCADE"), primary_key=True)
)
