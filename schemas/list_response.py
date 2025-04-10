from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")

class ListResponseSchema(BaseModel, Generic[T]):
    total: int
    items: List[T]
