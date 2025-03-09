from sqlalchemy import Column, Integer, Float, ForeignKey, String
from sqlalchemy.orm import relationship
from model.base import BaseModel
from model.enums import SentimentCategory

class FeedbackAnalysis(BaseModel):
    __tablename__ = "feedback_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    feedback_id = Column(Integer, ForeignKey("feedbacks.id"), unique=True, nullable=False)
    detected_language = Column(String(5), nullable=False)
    word_count = Column(Integer, nullable=False)
    feedback_length = Column(Integer, nullable=False)
    sentiment = Column(Float, nullable=False)
    sentiment_category = Column(String, nullable=False, default=SentimentCategory.NEUTRAL.value)
    star_rating = Column(Integer, nullable=False)

    # Relationship to link analysis with the feedback entry
    feedback = relationship("Feedback", back_populates="analysis")