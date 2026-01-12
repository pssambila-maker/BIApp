"""Pydantic schemas for scheduled reports."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class ScheduleConfigSchema(BaseModel):
    """Schedule configuration schema."""

    type: str = Field(..., pattern="^(daily|weekly|monthly)$")
    time: str = Field(..., pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="Time in HH:MM format (24-hour)")
    day_of_week: Optional[int] = Field(None, ge=0, le=6, description="0=Monday, 6=Sunday (for weekly)")
    day_of_month: Optional[int] = Field(None, ge=1, le=31, description="Day of month (for monthly)")

    @model_validator(mode='after')
    def validate_schedule_config(self):
        """Validate schedule configuration based on type."""
        if self.type == 'weekly' and self.day_of_week is None:
            raise ValueError("day_of_week is required for weekly schedules")
        if self.type == 'monthly' and self.day_of_month is None:
            raise ValueError("day_of_month is required for monthly schedules")
        if self.type == 'daily' and (self.day_of_week is not None or self.day_of_month is not None):
            raise ValueError("day_of_week and day_of_month should not be set for daily schedules")
        return self


class ScheduledReportBase(BaseModel):
    """Base schema for scheduled reports."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ScheduledReportCreate(ScheduledReportBase):
    """Schema for creating a scheduled report."""

    dashboard_id: Optional[UUID] = None
    saved_query_id: Optional[UUID] = None
    schedule_config: ScheduleConfigSchema
    recipients: List[EmailStr] = Field(..., min_length=1, description="At least one recipient required")
    formats: List[str] = Field(..., min_length=1, description="At least one format required")
    email_subject: Optional[str] = Field(None, max_length=255)
    email_body: Optional[str] = None
    is_active: bool = True

    @field_validator('formats')
    @classmethod
    def validate_formats(cls, v):
        """Validate export formats."""
        valid_formats = {'excel', 'csv', 'pdf', 'html'}
        for fmt in v:
            if fmt not in valid_formats:
                raise ValueError(f"Invalid format: {fmt}. Must be one of: {valid_formats}")
        return v

    @model_validator(mode='after')
    def validate_source(self):
        """Validate that exactly one of dashboard_id or saved_query_id is set."""
        if self.dashboard_id is None and self.saved_query_id is None:
            raise ValueError("Either dashboard_id or saved_query_id must be provided")
        if self.dashboard_id is not None and self.saved_query_id is not None:
            raise ValueError("Only one of dashboard_id or saved_query_id should be provided, not both")
        return self


class ScheduledReportUpdate(BaseModel):
    """Schema for updating a scheduled report."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    schedule_config: Optional[ScheduleConfigSchema] = None
    recipients: Optional[List[EmailStr]] = Field(None, min_length=1)
    formats: Optional[List[str]] = Field(None, min_length=1)
    email_subject: Optional[str] = Field(None, max_length=255)
    email_body: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator('formats')
    @classmethod
    def validate_formats(cls, v):
        """Validate export formats."""
        if v is None:
            return v
        valid_formats = {'excel', 'csv', 'pdf', 'html'}
        for fmt in v:
            if fmt not in valid_formats:
                raise ValueError(f"Invalid format: {fmt}. Must be one of: {valid_formats}")
        return v


class ReportExecutionResponse(BaseModel):
    """Schema for report execution response."""

    id: UUID
    scheduled_report_id: UUID
    status: str
    triggered_by: str
    generated_files: Optional[Dict[str, str]] = None
    sent_to: Optional[List[str]] = None
    execution_time_ms: Optional[int] = None
    row_count: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ScheduledReportResponse(ScheduledReportBase):
    """Schema for scheduled report response."""

    id: UUID
    owner_id: UUID
    dashboard_id: Optional[UUID] = None
    saved_query_id: Optional[UUID] = None
    schedule_config: Dict[str, Any]
    recipients: List[str]
    formats: List[str]
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    is_active: bool
    last_run_at: Optional[datetime] = None
    next_run_at: datetime
    created_at: datetime
    updated_at: datetime

    # Optional: Include last execution summary
    last_execution: Optional[ReportExecutionResponse] = None

    class Config:
        from_attributes = True


class ScheduledReportListResponse(BaseModel):
    """Schema for list of scheduled reports."""

    total: int
    reports: List[ScheduledReportResponse]


class ExecutionHistoryResponse(BaseModel):
    """Schema for execution history list."""

    total: int
    executions: List[ReportExecutionResponse]


class ManualRunResponse(BaseModel):
    """Schema for manual run response."""

    task_id: Optional[str] = None
    status: str
    message: str
    scheduled_report_id: UUID


class TestRunResponse(BaseModel):
    """Schema for test run response."""

    status: str
    message: str
    generated_files: Optional[Dict[str, str]] = None
    sent_to: Optional[List[str]] = None
    execution_time_ms: Optional[int] = None
    row_count: Optional[int] = None
    error_message: Optional[str] = None
