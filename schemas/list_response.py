from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")

class ListResponseSchema(BaseModel, Generic[T]):
    """Generic schema for list responses"""
    total: int
    items: List[T]
