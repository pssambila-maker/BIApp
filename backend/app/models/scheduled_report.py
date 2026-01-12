"""Scheduled report models for automated report generation and delivery."""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class ScheduledReport(Base):
    """Scheduled report model for automated report generation."""

    __tablename__ = "scheduled_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Source: EXACTLY ONE of dashboard_id or saved_query_id must be set
    dashboard_id = Column(UUID(as_uuid=True), ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=True, index=True)
    saved_query_id = Column(UUID(as_uuid=True), ForeignKey("saved_queries.id", ondelete="CASCADE"), nullable=True, index=True)

    # Schedule configuration (JSONB)
    # Structure: {
    #   type: 'daily' | 'weekly' | 'monthly',
    #   time: 'HH:MM',
    #   day_of_week: 0-6 (for weekly, 0=Monday),
    #   day_of_month: 1-31 (for monthly)
    # }
    schedule_config = Column(JSONB, nullable=False)

    # Recipients (JSONB array of email addresses)
    # Example: ["user1@example.com", "user2@example.com"]
    recipients = Column(JSONB, nullable=False)

    # Formats to generate (JSONB array)
    # Example: ["excel", "csv", "pdf", "html"]
    formats = Column(JSONB, nullable=False)

    # Email template
    email_subject = Column(String(255), nullable=True)
    email_body = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="scheduled_reports")
    dashboard = relationship("Dashboard", backref="scheduled_reports")
    saved_query = relationship("SavedQuery", backref="scheduled_reports")
    executions = relationship(
        "ReportExecution",
        back_populates="scheduled_report",
        cascade="all, delete-orphan",
        order_by="ReportExecution.created_at.desc()"
    )

    def __repr__(self):
        return f"<ScheduledReport(id={self.id}, name={self.name}, is_active={self.is_active})>"


class ReportExecution(Base):
    """Report execution audit trail."""

    __tablename__ = "report_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scheduled_report_id = Column(
        UUID(as_uuid=True),
        ForeignKey("scheduled_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Execution metadata
    status = Column(String(50), nullable=False)  # 'success', 'failed', 'partial'
    triggered_by = Column(String(50), nullable=False)  # 'schedule', 'manual', 'test'

    # Generated files (JSONB)
    # Structure: {
    #   excel: "/path/to/file.xlsx",
    #   csv: "/path/to/file.csv",
    #   pdf: "/path/to/file.pdf"
    # }
    generated_files = Column(JSONB, nullable=True)

    # Email delivery
    sent_to = Column(JSONB, nullable=True)  # Array of email addresses

    # Execution stats
    execution_time_ms = Column(Integer, nullable=True)
    row_count = Column(Integer, nullable=True)

    # Error tracking
    error_message = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    scheduled_report = relationship("ScheduledReport", back_populates="executions")

    def __repr__(self):
        return f"<ReportExecution(id={self.id}, status={self.status}, triggered_by={self.triggered_by})>"
