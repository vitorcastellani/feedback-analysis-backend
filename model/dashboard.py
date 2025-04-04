from model import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# Dashboard Model
class Dashboard(BaseModel):
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=True)
    name = Column(String, nullable=False)
    components = relationship("Component", back_populates="dashboard", cascade="all, delete-orphan")
    campaigns = relationship(
        "Campaign",
        secondary="dashboard_campaign",
        back_populates="dashboards"
    )