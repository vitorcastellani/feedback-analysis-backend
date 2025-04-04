from sqlalchemy import Column, Integer, String, Boolean
from model import BaseModel
from sqlalchemy.orm import relationship

# Campaign model
class Campaign(BaseModel):
    __tablename__ = "campaign"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    multiple_answers_from_user = Column(Boolean, default=True)
    max_answers = Column(Integer, default=0)
    short_code = Column(String, nullable=False, unique=True)
    
    feedbacks = relationship('Feedback', back_populates='campaign', cascade="all, delete-orphan")
    dashboards = relationship(
        "Dashboard",
        secondary="dashboard_campaign",
        back_populates="campaigns"
    )
    
    def __repr__(self):
        return f"<Campaign {self.id}: {self.name}>"