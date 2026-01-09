from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID


class SavedQueryBase(BaseModel):
    """Base schema for saved queries."""
    name: str = Field(..., min_length=1, max_length=255, description="Query name")
    description: Optional[str] = Field(None, description="Query description")
    entity_id: UUID = Field(..., description="Semantic entity ID")
    query_config: dict = Field(..., description="Query configuration (dimension_ids, measure_ids, filters, limit)")
    is_favorite: bool = Field(default=False, description="Mark as favorite")


class SavedQueryCreate(SavedQueryBase):
    """Schema for creating a saved query."""
    pass


class SavedQueryUpdate(BaseModel):
    """Schema for updating a saved query."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    query_config: Optional[dict] = None
    is_favorite: Optional[bool] = None


class SavedQueryResponse(SavedQueryBase):
    """Schema for saved query response."""
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SavedQueryListResponse(BaseModel):
    """Schema for list of saved queries."""
    queries: List[SavedQueryResponse]
    total: int
