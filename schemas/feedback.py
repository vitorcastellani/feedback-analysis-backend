from pydantic import BaseModel, ConfigDict
from datetime import datetime

# Feedback Create Schema
class FeedbackCreate(BaseModel):
    message: str

# Feedback ID Param Schema
class FeedbackIDParam(BaseModel):
    feedback_id: int

# Feedback Response Schema
class FeedbackResponse(BaseModel):
    id: int
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)