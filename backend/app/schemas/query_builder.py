"""Query Builder schemas for request and response validation."""
from typing import List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field


class FilterCondition(BaseModel):
    """Filter condition for query."""
    dimension_id: UUID
    operator: str = Field(
        ...,
        pattern="^(=|!=|>|<|>=|<=|IN|NOT IN|LIKE|IS NULL|IS NOT NULL)$"
    )
    value: Optional[Any] = None  # Can be single value or list for IN operator


class QueryRequest(BaseModel):
    """Request schema for query execution."""
    entity_id: UUID
    dimension_ids: List[UUID] = Field(
        default_factory=list,
        description="Dimensions for GROUP BY"
    )
    measure_ids: List[UUID] = Field(
        ...,
        min_length=1,
        description="Measures to calculate"
    )
    filters: List[FilterCondition] = Field(default_factory=list)
    limit: Optional[int] = Field(
        default=1000,
        le=10000,
        description="Row limit"
    )


class QueryResponse(BaseModel):
    """Response schema for query results."""
    columns: List[str]
    data: List[dict]  # Each row as a dictionary
    row_count: int
    generated_sql: str
    entity_name: str
