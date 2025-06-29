from pydantic import BaseModel, ConfigDict
from datetime import datetime
from model.enums import AgeRange, Gender, EducationLevel, Country, State

# Feedback Create Schema
class FeedbackCreate(BaseModel):
    age_range: AgeRange
    gender: Gender
    education_level: EducationLevel
    country: Country
    state: State
    message: str
    campaign_id: int

# Feedback ID Param Schema
class FeedbackIDParam(BaseModel):
    feedback_id: int

# Feedback Response Schema
class FeedbackResponse(BaseModel):
    id: int
    age_range: AgeRange
    gender: Gender
    education_level: EducationLevel
    country: Country
    state: State
    message: str
    campaign_id: int
    user_ip: str | None
    user_agent: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)