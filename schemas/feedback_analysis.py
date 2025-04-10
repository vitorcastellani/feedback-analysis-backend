from pydantic import BaseModel, ConfigDict
from datetime import datetime
from model.enums import SentimentCategory

class FeedbackAnalysisCreate(BaseModel):
    feedback_id: int

class FeedbackAnalysisResponse(BaseModel):
    id: int
    feedback_id: int
    sentiment: float
    sentiment_category: SentimentCategory
    star_rating: int
    detected_language: str
    word_count: int
    feedback_length: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class FeedbackCampaignAnalysisRequest(BaseModel):
    campaign_ids: list[int]

class FeedbackProgressResponse(BaseModel):
    queue_size: int
    processing: int