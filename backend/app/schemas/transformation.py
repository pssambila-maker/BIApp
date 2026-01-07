"""Pydantic schemas for transformation pipelines."""
from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field


# ==================== Transformation Step Schemas ====================

class TransformationStepBase(BaseModel):
    """Base schema for transformation step."""
    step_order: int = Field(..., ge=0, description="Execution order (0-indexed)")
    step_type: str = Field(..., description="Type: source, filter, join, aggregate, select, sort, union")
    step_name: str = Field(..., min_length=1, max_length=255, description="Human-readable step name")
    configuration: dict[str, Any] = Field(..., description="Step-specific configuration")
    output_alias: Optional[str] = Field(None, max_length=255, description="Alias for intermediate result")


class TransformationStepCreate(TransformationStepBase):
    """Schema for creating a transformation step."""
    pass


class TransformationStepUpdate(BaseModel):
    """Schema for updating a transformation step."""
    step_order: Optional[int] = Field(None, ge=0)
    step_type: Optional[str] = None
    step_name: Optional[str] = Field(None, min_length=1, max_length=255)
    configuration: Optional[dict[str, Any]] = None
    output_alias: Optional[str] = Field(None, max_length=255)


class TransformationStepResponse(TransformationStepBase):
    """Schema for transformation step response."""
    id: UUID
    pipeline_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Transformation Pipeline Schemas ====================

class TransformationPipelineBase(BaseModel):
    """Base schema for transformation pipeline."""
    name: str = Field(..., min_length=1, max_length=255, description="Pipeline name")
    description: Optional[str] = Field(None, description="Pipeline description")
    is_active: bool = Field(True, description="Whether pipeline is active")
    schedule_config: Optional[dict[str, Any]] = Field(None, description="Schedule configuration")


class TransformationPipelineCreate(TransformationPipelineBase):
    """Schema for creating a transformation pipeline."""
    steps: list[TransformationStepCreate] = Field(default_factory=list, description="Pipeline steps")


class TransformationPipelineUpdate(BaseModel):
    """Schema for updating a transformation pipeline."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    schedule_config: Optional[dict[str, Any]] = None


class TransformationPipelineResponse(TransformationPipelineBase):
    """Schema for transformation pipeline response."""
    id: UUID
    owner_id: UUID
    last_run_at: Optional[datetime]
    last_run_status: Optional[str]
    created_at: datetime
    updated_at: datetime
    steps: list[TransformationStepResponse] = []

    class Config:
        from_attributes = True


class TransformationPipelineList(BaseModel):
    """Schema for listing transformation pipelines."""
    id: UUID
    name: str
    description: Optional[str]
    is_active: bool
    last_run_at: Optional[datetime]
    last_run_status: Optional[str]
    step_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Pipeline Run Schemas ====================

class PipelineRunResponse(BaseModel):
    """Schema for pipeline run response."""
    id: UUID
    pipeline_id: UUID
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    rows_processed: Optional[int]
    error_message: Optional[str]
    execution_log: Optional[dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Pipeline Execution Schemas ====================

class PipelineExecuteRequest(BaseModel):
    """Schema for pipeline execution request."""
    limit: Optional[int] = Field(None, ge=0, le=10000, description="Limit output rows (0 or None = no limit)")
    preview_mode: bool = Field(True, description="Preview mode (don't save results)")


class PipelineExecuteResponse(BaseModel):
    """Schema for pipeline execution response."""
    run_id: UUID
    status: str
    rows_processed: int
    execution_time_seconds: float
    data: Optional[dict[str, Any]] = Field(None, description="Preview data if preview_mode=True")
    error_message: Optional[str] = None


# ==================== Step Configuration Examples ====================

class SourceStepConfig(BaseModel):
    """Configuration for source step."""
    data_source_id: UUID
    table_name: str
    schema_name: Optional[str] = None
    columns: Optional[list[str]] = None  # None = all columns


class FilterStepConfig(BaseModel):
    """Configuration for filter step."""
    conditions: list[dict[str, Any]]  # [{"column": "age", "operator": ">", "value": 18}]
    logical_operator: str = "AND"  # AND or OR


class JoinStepConfig(BaseModel):
    """Configuration for join step."""
    left_source: str  # Step alias or source
    right_source: str  # Step alias or source
    join_type: str = "inner"  # inner, left, right, full
    left_on: str  # Column name
    right_on: str  # Column name
    suffix_left: str = "_left"
    suffix_right: str = "_right"


class AggregateStepConfig(BaseModel):
    """Configuration for aggregate step."""
    group_by: list[str]  # Column names
    aggregations: list[dict[str, Any]]  # [{"column": "sales", "function": "sum", "alias": "total_sales"}]


class SelectStepConfig(BaseModel):
    """Configuration for select step."""
    columns: list[str]  # Column names to keep
    rename: Optional[dict[str, str]] = None  # {"old_name": "new_name"}


class SortStepConfig(BaseModel):
    """Configuration for sort step."""
    columns: list[str]  # Column names
    ascending: list[bool]  # Corresponding sort order for each column


class UnionStepConfig(BaseModel):
    """Configuration for union step."""
    sources: list[str]  # Step aliases to union
    remove_duplicates: bool = True
