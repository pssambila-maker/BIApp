from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class QueryHistoryResponse(BaseModel):
    """Schema for query history response."""
    id: UUID
    owner_id: UUID
    entity_id: UUID
    query_config: dict
    generated_sql: str
    row_count: int
    execution_time_ms: int
    executed_at: datetime

    class Config:
        from_attributes = True


class QueryHistoryListResponse(BaseModel):
    """Schema for list of query history."""
    history: list[QueryHistoryResponse]
    total: int
