from pydantic import BaseModel, Field

class PaginationSchema(BaseModel):
    """Schema for pagination parameters used in GET requests"""
    limit: int = Field(default=10, ge=1, le=100, description="Max number of items to return (1 to 100)")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
