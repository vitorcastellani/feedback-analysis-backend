from sqlalchemy import Column, Integer, String
from model.base import BaseModel

# Feedback model
class Feedback(BaseModel):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String, nullable=False)

    def __repr__(self):
        return f"<Feedback {self.id}: {self.message}>"