from sqlalchemy import Column, Integer, String, Boolean
from model import BaseModel
from sqlalchemy.orm import relationship

# Campaign model definition
class Campaign(BaseModel):
    __tablename__ = "campaign"  # Table name in the database

    # Primary key column with auto-increment
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Campaign name, cannot be null
    name = Column(String, nullable=False)

    # Campaign description, can be null
    description = Column(String, nullable=True)

    # Indicates if the campaign is active, defaults to True
    active = Column(Boolean, default=True)

    # Allows multiple answers from the same user, defaults to True
    multiple_answers_from_user = Column(Boolean, default=True)

    # Maximum number of answers allowed, defaults to 0 (no limit)
    max_answers = Column(Integer, default=0)

    # Short code for the campaign, must be unique and cannot be null
    short_code = Column(String, nullable=False, unique=True)

    # Relationship with the Feedback model, with cascading delete
    feedbacks = relationship(
        'Feedback', 
        back_populates='campaign', 
        cascade="all, delete-orphan"
    )

    # Many-to-many relationship with the Dashboard model through the dashboard_campaign table
    dashboards = relationship(
        "Dashboard",
        secondary="dashboard_campaign",
        back_populates="campaigns"
    )

    # String representation of the Campaign object
    def __repr__(self):
        return f"<Campaign {self.id}: {self.name}>"