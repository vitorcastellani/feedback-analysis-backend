from sqlalchemy import Column, Integer, String
from model import BaseModel
from sqlalchemy.orm import relationship

# Campaign model
class Campaign(BaseModel):
    __tablename__ = "campaign"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    feedbacks = relationship('Feedback', back_populates='campaign')
    
    def __repr__(self):
        return f"<Campaign {self.id}: {self.name}>"