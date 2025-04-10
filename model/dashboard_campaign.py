from sqlalchemy import Column, Integer, ForeignKey, Table
from model import BaseModel

# Define the association table for the many-to-many relationship between Dashboards and Campaigns
dashboard_campaign = Table(
    "dashboard_campaign",  # Name of the association table
    BaseModel.metadata,  # Use metadata from the BaseModel
    Column(
        "dashboard_id",  # Column name for the dashboard ID
        Integer,  # Data type is Integer
        ForeignKey("dashboards.id", ondelete="CASCADE"),  # Foreign key referencing the Dashboards table with cascade delete
        primary_key=True  # Set as a primary key
    ),
    Column(
        "campaign_id",  # Column name for the campaign ID
        Integer,  # Data type is Integer
        ForeignKey("campaign.id", ondelete="CASCADE"),  # Foreign key referencing the Campaigns table with cascade delete
        primary_key=True  # Set as a primary key
    )
)
