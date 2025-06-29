from sqlalchemy import Column, Integer, Float, ForeignKey, String, Enum as SqlEnum
from sqlalchemy.orm import relationship
from model.base import BaseModel
from model.enums import SentimentCategory

class FeedbackAnalysis(BaseModel):
    __tablename__ = "feedback_analysis"

    # Primary key for the feedback analysis table
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key linking to the feedbacks table, with cascade delete
    feedback_id = Column(Integer, ForeignKey("feedbacks.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Detected language of the feedback (e.g., 'en', 'es')
    detected_language = Column(String(5), nullable=False)

    # Number of words in the feedback
    word_count = Column(Integer, nullable=False)

    # Total length of the feedback (e.g., character count)
    feedback_length = Column(Integer, nullable=False)

    # Sentiment score of the feedback (e.g., -1.0 to 1.0)
    sentiment = Column(Float, nullable=False)

    # Sentiment category (e.g., Positive, Neutral, Negative)
    sentiment_category = Column(SqlEnum(SentimentCategory), nullable=False, default=SentimentCategory.NEUTRAL.value)

    # Star rating associated with the feedback (e.g., 1 to 5 stars)
    star_rating = Column(Integer, nullable=False)

    # Relationship to link the analysis with the corresponding feedback entry
    feedback = relationship("Feedback", back_populates="analysis")