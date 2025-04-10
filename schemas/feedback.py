from pydantic import BaseModel, ConfigDict
from datetime import datetime

# Feedback Create Schema
class FeedbackCreate(BaseModel):
    message: str
    campaign_id: int

# Feedback ID Param Schema
class FeedbackIDParam(BaseModel):
    feedback_id: int

# Feedback Response Schema
class FeedbackResponse(BaseModel):
    id: int
    message: str
    campaign_id: int
    user_ip: str | None
    user_agent: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)