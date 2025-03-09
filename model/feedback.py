from sqlalchemy import Column, Integer, String
from model.base import BaseModel
from sqlalchemy.orm import relationship

# Feedback model
class Feedback(BaseModel):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String(4000), nullable=False)

    # Relationship with FeedbackAnalysis
    analysis = relationship("FeedbackAnalysis", uselist=False, back_populates="feedback")

    def __repr__(self):
        return f"<Feedback {self.id}: {self.message}>"