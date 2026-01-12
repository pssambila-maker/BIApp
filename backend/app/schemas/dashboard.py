"""Dashboard schemas for request/response validation."""
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


# Widget Grid Position
class GridPosition(BaseModel):
    """Grid position for dashboard widgets."""
    x: int = Field(..., ge=0, description="X position in grid")
    y: int = Field(..., ge=0, description="Y position in grid")
    w: int = Field(..., ge=1, le=12, description="Width in grid units (max 12)")
    h: int = Field(..., ge=1, description="Height in grid units")


# Dashboard Widget Schemas
class DashboardWidgetBase(BaseModel):
    """Base schema for dashboard widgets."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    query_config: dict = Field(..., description="Query configuration (entity, dimensions, measures, filters)")
    chart_config: dict = Field(..., description="Chart configuration (type, axes, colors, sorting)")
    grid_position: GridPosition
    position_order: int = Field(default=0, description="Order of widget in dashboard")
    refresh_interval: Optional[int] = Field(None, description="Auto-refresh interval in seconds")


class DashboardWidgetCreate(DashboardWidgetBase):
    """Schema for creating a dashboard widget."""
    pass


class DashboardWidgetUpdate(BaseModel):
    """Schema for updating a dashboard widget."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    query_config: Optional[dict] = None
    chart_config: Optional[dict] = None
    grid_position: Optional[GridPosition] = None
    position_order: Optional[int] = None
    refresh_interval: Optional[int] = None


class DashboardWidgetResponse(DashboardWidgetBase):
    """Schema for dashboard widget responses."""
    id: UUID
    dashboard_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Dashboard Schemas
class DashboardBase(BaseModel):
    """Base schema for dashboards."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    layout_config: dict = Field(default_factory=dict, description="Grid layout configuration")
    global_filters: List[dict] = Field(default_factory=list, description="Global filters for all widgets")
    is_public: bool = Field(default=False, description="Whether dashboard is publicly accessible")
    is_favorite: bool = Field(default=False, description="Whether dashboard is marked as favorite")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing dashboard")


class DashboardCreate(DashboardBase):
    """Schema for creating a dashboard."""
    widgets: List[DashboardWidgetCreate] = Field(default_factory=list, description="Initial widgets")


class DashboardUpdate(BaseModel):
    """Schema for updating a dashboard."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    layout_config: Optional[dict] = None
    global_filters: Optional[List[dict]] = None
    is_public: Optional[bool] = None
    is_favorite: Optional[bool] = None
    tags: Optional[List[str]] = None


class DashboardResponse(DashboardBase):
    """Schema for dashboard responses."""
    id: UUID
    owner_id: UUID
    widgets: List[DashboardWidgetResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DashboardListResponse(BaseModel):
    """Schema for dashboard list responses."""
    dashboards: List[DashboardResponse]
    total: int


# Dashboard Widget Data Response (for fetching widget data)
class WidgetDataRequest(BaseModel):
    """Request schema for fetching widget data."""
    widget_id: UUID
    apply_global_filters: bool = Field(default=True, description="Whether to apply dashboard global filters")


class WidgetDataResponse(BaseModel):
    """Response schema for widget data."""
    widget_id: UUID
    columns: List[str]
    data: List[dict]
    row_count: int
    generated_sql: str
    execution_time_ms: int
