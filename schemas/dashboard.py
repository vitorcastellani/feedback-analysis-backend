from pydantic import BaseModel

class DashboardMetricsResponse(BaseModel):
    total_campaigns: int
    total_feedbacks: int
    active_campaigns: int