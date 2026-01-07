"""Pydantic schemas for data sources."""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DataSourceBase(BaseModel):
    """Base schema for data source."""

    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., pattern="^(csv|excel|postgresql|mysql)$")
    description: Optional[str] = None


class DataSourceCreate(DataSourceBase):
    """Schema for creating a data source."""

    connection_config: dict[str, Any] = Field(
        ...,
        description="Connection configuration (encrypted credentials)"
    )


class DataSourceUpdate(BaseModel):
    """Schema for updating a data source."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    connection_config: Optional[dict[str, Any]] = None
    is_certified: Optional[bool] = None


class DataSourceResponse(DataSourceBase):
    """Schema for data source response."""

    id: UUID
    owner_id: UUID
    is_certified: bool
    schema_metadata: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DataSourceTableResponse(BaseModel):
    """Schema for table/sheet information."""

    table_name: str
    schema_name: Optional[str] = None
    columns: Optional[list[dict[str, Any]]] = None
    row_count: Optional[int] = None
    size_bytes: Optional[int] = None


class ConnectionTestResponse(BaseModel):
    """Schema for connection test response."""

    status: str = Field(..., pattern="^(success|error)$")
    message: str


class DataPreviewResponse(BaseModel):
    """Schema for data preview response."""

    columns: list[str]
    data: list[dict[str, Any]]
    row_count: int
