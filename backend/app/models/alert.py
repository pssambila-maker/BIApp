"""Alert models for automated data condition monitoring."""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Alert(Base):
    """Alert model for monitoring data conditions."""

    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Source query
    saved_query_id = Column(UUID(as_uuid=True), ForeignKey("saved_queries.id", ondelete="CASCADE"), nullable=False, index=True)

    # Alert type: 'threshold', 'change', 'anomaly', 'data_quality'
    alert_type = Column(String(50), nullable=False)

    # Condition configuration (JSONB) - structure depends on alert_type
    # Threshold: {measure_id: UUID, operator: '>', '<', '>=', '<=', '==', value: number}
    # Change: {measure_id: UUID, change_percent: number, comparison_period: 'previous', lookback_days: number}
    # Anomaly: {measure_id: UUID, method: 'zscore', threshold: number (e.g., 3.0)}
    # Data Quality: {check_type: 'nulls', 'duplicates', 'range', column: string, threshold: number}
    condition_config = Column(JSONB, nullable=False)

    # Check frequency (JSONB)
    # Structure: {
    #   type: 'interval' | 'scheduled',
    #   interval_minutes: number (for interval type),
    #   time: 'HH:MM' (for scheduled type),
    #   day_of_week: 0-6 (optional, for scheduled type)
    # }
    check_frequency = Column(JSONB, nullable=False)

    # Recipients (JSONB array)
    recipients = Column(JSONB, nullable=False)

    # Notification message template
    notification_message = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_checked_at = Column(DateTime(timezone=True), nullable=True)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="alerts")
    saved_query = relationship("SavedQuery", backref="alerts")
    executions = relationship(
        "AlertExecution",
        back_populates="alert",
        cascade="all, delete-orphan",
        order_by="AlertExecution.created_at.desc()"
    )

    def __repr__(self):
        return f"<Alert(id={self.id}, name={self.name}, type={self.alert_type}, is_active={self.is_active})>"


class AlertExecution(Base):
    """Alert execution audit trail."""

    __tablename__ = "alert_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(
        UUID(as_uuid=True),
        ForeignKey("alerts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Execution result
    condition_met = Column(Boolean, nullable=False)
    condition_value = Column(JSONB, nullable=True)  # Actual value that was checked

    # Notification
    notification_sent = Column(Boolean, default=False, nullable=False)
    notified_recipients = Column(JSONB, nullable=True)  # Array of emails

    # Error tracking
    error_message = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    alert = relationship("Alert", back_populates="executions")

    def __repr__(self):
        return f"<AlertExecution(id={self.id}, condition_met={self.condition_met}, notification_sent={self.notification_sent})>"
