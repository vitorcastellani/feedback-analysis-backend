from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from model.enums import ComponentType

class DashboardMetricsResponse(BaseModel):
    total_campaigns: int
    total_feedbacks: int
    active_campaigns: int

class DashboardIDParam(BaseModel):
    dashboard_id: int

class DashboardCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=255)
    campaign_ids: List[int] = Field(..., min_length=0)
    components: List[Dict] = Field(..., min_length=1)

class DashboardUpdate(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=255)
    campaign_ids: List[int] = Field(..., min_length=0)
    components: List[Dict] = Field(..., min_length=1)

class DashboardResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    campaigns: List[int]
    components: List[Dict]

class DashboardListResponse(BaseModel):
    total: int
    items: List[DashboardResponse]

class DashboardComponentIDParam(BaseModel):
    dashboard_id: int
    component_id: int

class DashboardComponentResponse(BaseModel):
    id: int
    name: str
    type: str
    settings: Dict
    data: Dict