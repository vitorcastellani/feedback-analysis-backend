from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

# Campaign Create Schema
class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: str | None = None
    active: bool = True
    multiple_answers_from_user: bool = True
    max_answers: int = 0

# Campaign Response Schema
class CampaignResponse(BaseModel):
    id: int
    name: str
    description: str | None
    active: bool
    multiple_answers_from_user: bool
    max_answers: int
    short_code: str
    feedback_count: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Campaign ID Param Schema
class CampaignIDParam(BaseModel):
    campaign_id: int

# Campaign Short Code Param Schema
class CampaignShortCodeParam(BaseModel):
    short_code: str