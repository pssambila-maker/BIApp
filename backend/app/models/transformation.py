"""Transformation pipeline models for data processing."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, ForeignKey, Text, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID, TIMESTAMP

from app.db.base import Base


class TransformationPipeline(Base):
    """Data transformation pipeline model."""

    __tablename__ = "transformation_pipelines"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    owner_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    schedule_config: Mapped[Optional[dict]] = mapped_column(JSONB)  # Cron schedule, manual, etc.
    last_run_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    last_run_status: Mapped[Optional[str]] = mapped_column(String(50))  # 'success', 'failed', 'running'

    # Relationships
    steps: Mapped[list["TransformationStep"]] = relationship(
        "TransformationStep",
        back_populates="pipeline",
        cascade="all, delete-orphan",
        order_by="TransformationStep.step_order"
    )
    runs: Mapped[list["PipelineRun"]] = relationship(
        "PipelineRun",
        back_populates="pipeline",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<TransformationPipeline(name={self.name}, steps={len(self.steps)})>"


class TransformationStep(Base):
    """Individual step in a transformation pipeline."""

    __tablename__ = "transformation_steps"

    pipeline_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("transformation_pipelines.id", ondelete="CASCADE"),
        nullable=False
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)  # Execution order
    step_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'source', 'filter', 'join', 'aggregate', 'select', 'sort'
    step_name: Mapped[str] = mapped_column(String(255), nullable=False)
    configuration: Mapped[dict] = mapped_column(JSONB, nullable=False)  # Step-specific config
    output_alias: Mapped[Optional[str]] = mapped_column(String(255))  # Optional name for intermediate result

    # Relationships
    pipeline: Mapped["TransformationPipeline"] = relationship(
        "TransformationPipeline",
        back_populates="steps"
    )

    def __repr__(self) -> str:
        return f"<TransformationStep(type={self.step_type}, order={self.step_order})>"


class PipelineRun(Base):
    """Execution history of a transformation pipeline."""

    __tablename__ = "pipeline_runs"

    pipeline_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("transformation_pipelines.id", ondelete="CASCADE"),
        nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # 'running', 'success', 'failed'
    started_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    rows_processed: Mapped[Optional[int]] = mapped_column(Integer)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    execution_log: Mapped[Optional[dict]] = mapped_column(JSONB)  # Detailed logs per step

    # Relationships
    pipeline: Mapped["TransformationPipeline"] = relationship(
        "TransformationPipeline",
        back_populates="runs"
    )

    def __repr__(self) -> str:
        return f"<PipelineRun(pipeline_id={self.pipeline_id}, status={self.status})>"
