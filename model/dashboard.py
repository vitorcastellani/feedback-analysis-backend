from model import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# Dashboard model definition
class Dashboard(BaseModel):
    __tablename__ = "dashboards"  # Table name in the database

    # Primary key column with auto-increment
    id = Column(Integer, primary_key=True, index=True)

    # Dashboard description, can be null
    description = Column(String, nullable=True)

    # Dashboard name, cannot be null
    name = Column(String, nullable=False)

    # One-to-many relationship with the Component model, with cascading delete
    components = relationship(
        "Component", 
        back_populates="dashboard", 
        cascade="all, delete-orphan"
    )

    # Many-to-many relationship with the Campaign model through the dashboard_campaign table
    campaigns = relationship(
        "Campaign",
        secondary="dashboard_campaign",
        back_populates="dashboards"
    )