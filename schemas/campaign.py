from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

# Campaign Create Schema
class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: str | None = None

# Campaign Response Schema
class CampaignResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Campaign ID Param Schema
class CampaignIDParam(BaseModel):
    campaign_id: int