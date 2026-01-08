"""Pydantic schemas for semantic layer."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ==================== Dimension Schemas ====================

class SemanticDimensionBase(BaseModel):
    """Base schema for semantic dimension."""
    name: str = Field(..., min_length=1, max_length=255, description="Dimension name")
    description: Optional[str] = Field(None, description="Dimension description")
    sql_column: str = Field(..., min_length=1, max_length=255, description="Underlying SQL column")
    data_type: str = Field(..., pattern="^(string|integer|date|boolean|decimal)$", description="Data type")
    display_format: Optional[str] = Field(None, max_length=100, description="Display format hint")
    is_hidden: bool = Field(default=False, description="Hide from UI")
    display_order: int = Field(default=0, ge=0, description="Display order in UI")


class SemanticDimensionCreate(SemanticDimensionBase):
    """Schema for creating a dimension."""
    pass


class SemanticDimensionUpdate(BaseModel):
    """Schema for updating a dimension."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    sql_column: Optional[str] = Field(None, min_length=1, max_length=255)
    data_type: Optional[str] = Field(None, pattern="^(string|integer|date|boolean|decimal)$")
    display_format: Optional[str] = Field(None, max_length=100)
    is_hidden: Optional[bool] = None
    display_order: Optional[int] = Field(None, ge=0)


class SemanticDimensionResponse(SemanticDimensionBase):
    """Schema for dimension response."""
    id: UUID
    semantic_entity_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Measure Schemas ====================

class SemanticMeasureBase(BaseModel):
    """Base schema for semantic measure."""
    name: str = Field(..., min_length=1, max_length=255, description="Measure name")
    description: Optional[str] = Field(None, description="Measure description")
    calculation_type: str = Field(default="aggregation", pattern="^aggregation$", description="Calculation type")
    aggregation_function: str = Field(..., pattern="^(SUM|COUNT|AVG|MIN|MAX|MEDIAN|STDDEV)$", description="Aggregation function")
    base_column: str = Field(..., min_length=1, max_length=255, description="Column to aggregate")
    format: Optional[str] = Field(None, pattern="^(currency|percent|integer|decimal)$", description="Display format")
    default_format_pattern: Optional[str] = Field(None, max_length=100, description="Format pattern (e.g., $#,##0.00)")
    is_hidden: bool = Field(default=False, description="Hide from UI")


class SemanticMeasureCreate(SemanticMeasureBase):
    """Schema for creating a measure."""
    pass


class SemanticMeasureUpdate(BaseModel):
    """Schema for updating a measure."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    aggregation_function: Optional[str] = Field(None, pattern="^(SUM|COUNT|AVG|MIN|MAX|MEDIAN|STDDEV)$")
    base_column: Optional[str] = Field(None, min_length=1, max_length=255)
    format: Optional[str] = Field(None, pattern="^(currency|percent|integer|decimal)$")
    default_format_pattern: Optional[str] = Field(None, max_length=100)
    is_hidden: Optional[bool] = None


class SemanticMeasureResponse(SemanticMeasureBase):
    """Schema for measure response."""
    id: UUID
    semantic_entity_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Entity Schemas ====================

class SemanticEntityBase(BaseModel):
    """Base schema for semantic entity."""
    name: str = Field(..., min_length=1, max_length=255, description="Entity name")
    plural_name: Optional[str] = Field(None, max_length=255, description="Plural form of entity name")
    description: Optional[str] = Field(None, description="Entity description")
    primary_table: str = Field(..., min_length=1, max_length=255, description="Primary table or data source")
    sql_definition: Optional[str] = Field(None, description="Optional SQL definition for derived entity")
    is_certified: bool = Field(default=False, description="Whether entity is certified/approved")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Ensure tags are list of strings."""
        if not isinstance(v, list):
            raise ValueError('tags must be a list')
        for tag in v:
            if not isinstance(tag, str):
                raise ValueError('all tags must be strings')
        return v


class SemanticEntityCreate(SemanticEntityBase):
    """Schema for creating an entity."""
    pass


class SemanticEntityUpdate(BaseModel):
    """Schema for updating an entity."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    plural_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    primary_table: Optional[str] = Field(None, min_length=1, max_length=255)
    sql_definition: Optional[str] = None
    is_certified: Optional[bool] = None
    tags: Optional[list[str]] = None

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Ensure tags are list of strings."""
        if v is not None:
            if not isinstance(v, list):
                raise ValueError('tags must be a list')
            for tag in v:
                if not isinstance(tag, str):
                    raise ValueError('all tags must be strings')
        return v


class SemanticEntityResponse(SemanticEntityBase):
    """Schema for full entity response with dimensions and measures."""
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    dimensions: list[SemanticDimensionResponse] = Field(default_factory=list)
    measures: list[SemanticMeasureResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class SemanticEntityListResponse(BaseModel):
    """Schema for lightweight entity list response."""
    id: UUID
    name: str
    plural_name: Optional[str]
    description: Optional[str]
    primary_table: str
    is_certified: bool
    tags: list[str]
    dimension_count: int
    measure_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Catalog Schema ====================

class SemanticCatalogEntity(BaseModel):
    """Entity schema for catalog response."""
    id: UUID
    name: str
    plural_name: Optional[str]
    description: Optional[str]
    primary_table: str
    is_certified: bool
    tags: list[str]
    dimensions: list[SemanticDimensionResponse] = Field(default_factory=list)
    measures: list[SemanticMeasureResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class SemanticCatalogResponse(BaseModel):
    """Complete semantic catalog for frontend discovery."""
    entities: list[SemanticCatalogEntity]
    total_entities: int
    total_dimensions: int
    total_measures: int
