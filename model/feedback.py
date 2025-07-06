from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SqlEnum
from model import BaseModel
from model.enums import AgeRange, Gender, EducationLevel, Country, State
from sqlalchemy.orm import relationship

# Feedback model definition
class Feedback(BaseModel):
    __tablename__ = "feedbacks"  # Table name in the database

    # Primary key column
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Column to store the age range of the user using Enum
    age_range = Column(SqlEnum(AgeRange), nullable=False, default=AgeRange.other.value)

    # Column to store the gender of the user using Enum
    gender = Column(SqlEnum(Gender), nullable=False, default=Gender.prefer_not_to_say.value)

    # Column to store the education level of the user using Enum
    education_level = Column(SqlEnum(EducationLevel), nullable=False, default=EducationLevel.other.value)

    # Column to store the country of the user using Enum
    country = Column(SqlEnum(Country), nullable=False, default=Country.other.value)

    # Column to store the state of the user using Enum
    state = Column(SqlEnum(State), nullable=False, default=State.other.value)
    
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