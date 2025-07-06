from pydantic import BaseModel, Field

class PaginationSchema(BaseModel):
    campaign_id: int | None = Field(
        default=None, description="Filter by campaign ID (optional)"
    )
    age_range: str | None = Field(
        default=None, description="Filter by age range (optional)"
    )
    gender: str | None = Field(
        default=None, description="Filter by gender (optional)"
    )
    education_level: str | None = Field(
        default=None, description="Filter by education level (optional)"
    )
    country: str | None = Field(
        default=None, description="Filter by country (optional)"
    )
    state: str | None = Field(
        default=None, description="Filter by state (optional)"
    )
    limit: int = Field(
        default=10, ge=1, le=100, description="Max number of items to return (1 to 100)"
    )
    offset: int = Field(
        default=0, ge=0, description="Number of items to skip"
    )
