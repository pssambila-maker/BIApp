"""Semantic layer models for business-friendly data abstractions."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, ForeignKey, Text, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID

from app.db.base import Base


class SemanticEntity(Base):
    """
    Semantic entity representing a business object (e.g., Customer, Product).

    Entities serve as the foundation of the semantic layer, mapping to
    underlying data sources while providing business-friendly terminology.
    """

    __tablename__ = "semantic_entities"

    # Ownership
    owner_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # Entity metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    plural_name: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Data source mapping
    primary_table: Mapped[str] = mapped_column(String(255), nullable=False)
    sql_definition: Mapped[Optional[str]] = mapped_column(Text)

    # Governance
    is_certified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", index=True)
    tags: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")

    # Relationships
    dimensions: Mapped[list["SemanticDimension"]] = relationship(
        "SemanticDimension",
        back_populates="semantic_entity",
        cascade="all, delete-orphan",
        order_by="SemanticDimension.display_order"
    )
    measures: Mapped[list["SemanticMeasure"]] = relationship(
        "SemanticMeasure",
        back_populates="semantic_entity",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SemanticEntity(name={self.name}, dimensions={len(self.dimensions)}, measures={len(self.measures)})>"


class SemanticDimension(Base):
    """
    Dimension representing an attribute for grouping, filtering, or labeling.

    Examples: Customer Name, Region, Product Category, Order Date
    """

    __tablename__ = "semantic_dimensions"

    # Entity relationship
    semantic_entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("semantic_entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Dimension metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Data mapping
    sql_column: Mapped[str] = mapped_column(String(255), nullable=False)
    data_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Display configuration
    display_format: Mapped[Optional[str]] = mapped_column(String(100))
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    display_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # Relationships
    semantic_entity: Mapped["SemanticEntity"] = relationship(
        "SemanticEntity",
        back_populates="dimensions"
    )

    def __repr__(self) -> str:
        return f"<SemanticDimension(name={self.name}, type={self.data_type})>"


class SemanticMeasure(Base):
    """
    Measure representing a numeric metric that can be aggregated.

    Examples: Total Revenue, Customer Count, Average Order Value
    """

    __tablename__ = "semantic_measures"

    # Entity relationship
    semantic_entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("semantic_entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Measure metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Calculation configuration
    calculation_type: Mapped[str] = mapped_column(String(50), default="aggregation", server_default="aggregation")
    aggregation_function: Mapped[str] = mapped_column(String(20), nullable=False)
    base_column: Mapped[str] = mapped_column(String(255), nullable=False)

    # Display configuration
    format: Mapped[Optional[str]] = mapped_column(String(100))
    default_format_pattern: Mapped[Optional[str]] = mapped_column(String(100))
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # Relationships
    semantic_entity: Mapped["SemanticEntity"] = relationship(
        "SemanticEntity",
        back_populates="measures"
    )

    def __repr__(self) -> str:
        return f"<SemanticMeasure(name={self.name}, function={self.aggregation_function})>"
