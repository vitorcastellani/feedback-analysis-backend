from sqlalchemy import Column, Integer, String, ForeignKey
from model import BaseModel
from sqlalchemy.orm import relationship

# Feedback model definition
class Feedback(BaseModel):
    __tablename__ = "feedbacks"  # Table name in the database

    # Primary key column
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Column to store the feedback message (up to 4000 characters)
    message = Column(String(4000), nullable=False)
    
    # Foreign key to associate feedback with a campaign
    campaign_id = Column(Integer, ForeignKey("campaign.id", ondelete="CASCADE"), nullable=False)
    
    # Column to store the user's IP address (optional)
    user_ip = Column(String(45), nullable=True)
    
    # Column to store the user's agent information (optional)
    user_agent = Column(String(255), nullable=True)

    # One-to-one relationship with FeedbackAnalysis
    analysis = relationship(
        "FeedbackAnalysis", 
        uselist=False, 
        back_populates="feedback", 
        cascade="all, delete-orphan"
    )

    # Many-to-one relationship with Campaign
    campaign = relationship(
        'Campaign', 
        back_populates='feedbacks'
    )

    # String representation of the Feedback object
    def __repr__(self):
        return f"<Feedback {self.id}: {self.message}>"