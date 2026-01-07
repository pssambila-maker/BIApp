"""Data source models for connecting to external data."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Boolean, ForeignKey, Text, Integer, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID, TIMESTAMP

from app.db.base import Base


class DataSource(Base):
    """Data source model for external connections."""

    __tablename__ = "data_sources"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'csv', 'excel', 'postgresql', 'mysql', 'api'
    description: Mapped[Optional[str]] = mapped_column(Text)
    connection_config: Mapped[dict] = mapped_column(JSONB, nullable=False)  # Encrypted credentials
    schema_metadata: Mapped[Optional[dict]] = mapped_column(JSONB)  # Cached schema information
    owner_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    is_certified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    last_refreshed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))

    # Relationships
    tables: Mapped[list["DataSourceTable"]] = relationship(
        "DataSourceTable",
        back_populates="data_source",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<DataSource(name={self.name}, type={self.type})>"


class DataSourceTable(Base):
    """Table/sheet within a data source."""

    __tablename__ = "data_source_tables"

    data_source_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("data_sources.id", ondelete="CASCADE"),
        nullable=False
    )
    table_name: Mapped[str] = mapped_column(String(255), nullable=False)
    schema_name: Mapped[Optional[str]] = mapped_column(String(255))  # For databases with schemas
    column_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False)  # [{name, type, nullable, sample_values}]
    row_count: Mapped[Optional[int]] = mapped_column(BigInteger)
    size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)

    # Relationships
    data_source: Mapped["DataSource"] = relationship("DataSource", back_populates="tables")

    def __repr__(self) -> str:
        return f"<DataSourceTable(table_name={self.table_name}, schema={self.schema_name})>"
