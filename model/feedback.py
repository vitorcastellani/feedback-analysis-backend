from sqlalchemy import Column, Integer, String, ForeignKey
from model import BaseModel
from sqlalchemy.orm import relationship

# Feedback model
class Feedback(BaseModel):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String(4000), nullable=False)
    campaign_id = Column(Integer, ForeignKey('campaign.id'), nullable=False)

    # Relationship with FeedbackAnalysis
    analysis = relationship("FeedbackAnalysis", uselist=False, back_populates="feedback")

    # Relationship with Campaign
    campaign = relationship('Campaign', back_populates='feedbacks')

    def __repr__(self):
        return f"<Feedback {self.id}: {self.message}>"