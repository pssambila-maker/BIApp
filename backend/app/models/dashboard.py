"""Dashboard models for storing dashboard configurations and widgets."""
from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class Dashboard(Base):
    """Dashboard model for storing dashboard configurations."""

    __tablename__ = "dashboards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Layout configuration (grid settings, etc.)
    layout_config = Column(JSON, nullable=False, default=dict)

    # Global filters that apply to all widgets
    global_filters = Column(JSON, nullable=False, default=list)

    # Dashboard metadata
    is_public = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    tags = Column(JSON, default=list)

    # Relationships
    owner = relationship("User", back_populates="dashboards")
    widgets = relationship(
        "DashboardWidget",
        back_populates="dashboard",
        cascade="all, delete-orphan",
        order_by="DashboardWidget.position_order"
    )

    def __repr__(self):
        return f"<Dashboard(id={self.id}, name={self.name})>"


class DashboardWidget(Base):
    """Widget model for storing individual chart configurations on a dashboard."""

    __tablename__ = "dashboard_widgets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dashboard_id = Column(UUID(as_uuid=True), ForeignKey("dashboards.id"), nullable=False)

    # Widget identification
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Query configuration (entity, dimensions, measures, filters)
    query_config = Column(JSON, nullable=False)

    # Chart configuration (type, axes, colors, sorting)
    chart_config = Column(JSON, nullable=False)

    # Position and size in grid layout
    # Grid uses 12-column layout
    grid_position = Column(JSON, nullable=False)  # {x, y, w, h}
    position_order = Column(Integer, default=0)  # For ordering widgets

    # Widget settings
    refresh_interval = Column(Integer, nullable=True)  # Auto-refresh in seconds

    # Relationships
    dashboard = relationship("Dashboard", back_populates="widgets")

    def __repr__(self):
        return f"<DashboardWidget(id={self.id}, title={self.title})>"
