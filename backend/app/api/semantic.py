"""API endpoints for semantic layer."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.semantic import SemanticEntity, SemanticDimension, SemanticMeasure
from app.schemas.semantic import (
    SemanticEntityCreate,
    SemanticEntityUpdate,
    SemanticEntityResponse,
    SemanticEntityListResponse,
    SemanticDimensionCreate,
    SemanticDimensionUpdate,
    SemanticDimensionResponse,
    SemanticMeasureCreate,
    SemanticMeasureUpdate,
    SemanticMeasureResponse,
    SemanticCatalogResponse,
    SemanticCatalogEntity,
)

router = APIRouter(prefix="/semantic", tags=["semantic"])


# ==================== Entity CRUD ====================

@router.post("/entities", response_model=SemanticEntityResponse, status_code=status.HTTP_201_CREATED)
async def create_entity(
    entity_data: SemanticEntityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SemanticEntity:
    """
    Create a new semantic entity.

    Args:
        entity_data: Entity creation data
        current_user: Authenticated user
        db: Database session

    Returns:
        Created semantic entity
    """
    entity = SemanticEntity(
        **entity_data.model_dump(),
        owner_id=current_user.id
    )
    db.add(entity)
    await db.commit()
    await db.refresh(entity)

    # Load relationships
    result = await db.execute(
        select(SemanticEntity)
        .where(SemanticEntity.id == entity.id)
        .options(
            selectinload(SemanticEntity.dimensions),
            selectinload(SemanticEntity.measures)
        )
    )
    return result.scalar_one()


@router.get("/entities", response_model=List[SemanticEntityListResponse])
async def list_entities(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[dict]:
    """
    List all semantic entities with dimension/measure counts.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Authenticated user
        db: Database session

    Returns:
        List of semantic entities with counts
    """
    # Query with dimension and measure counts
    query = (
        select(
            SemanticEntity,
            func.count(SemanticDimension.id.distinct()).label("dimension_count"),
            func.count(SemanticMeasure.id.distinct()).label("measure_count")
        )
        .outerjoin(SemanticDimension, SemanticEntity.id == SemanticDimension.semantic_entity_id)
        .outerjoin(SemanticMeasure, SemanticEntity.id == SemanticMeasure.semantic_entity_id)
        .where(SemanticEntity.owner_id == current_user.id)
        .group_by(SemanticEntity.id)
        .order_by(SemanticEntity.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    rows = result.all()

    # Build response
    entities_list = []
    for entity, dim_count, meas_count in rows:
        entities_list.append({
            "id": entity.id,
            "name": entity.name,
            "plural_name": entity.plural_name,
            "description": entity.description,
            "primary_table": entity.primary_table,
            "is_certified": entity.is_certified,
            "tags": entity.tags,
            "dimension_count": dim_count,
            "measure_count": meas_count,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at
        })

    return entities_list


@router.get("/entities/{entity_id}", response_model=SemanticEntityResponse)
async def get_entity(
    entity_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SemanticEntity:
    """
    Get a specific semantic entity with dimensions and measures.

    Args:
        entity_id: Entity ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Semantic entity with dimensions and measures

    Raises:
        HTTPException: 404 if entity not found
    """
    result = await db.execute(
        select(SemanticEntity)
        .where(
            SemanticEntity.id == entity_id,
            SemanticEntity.owner_id == current_user.id
        )
        .options(
            selectinload(SemanticEntity.dimensions),
            selectinload(SemanticEntity.measures)
        )
    )
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )

    return entity


@router.put("/entities/{entity_id}", response_model=SemanticEntityResponse)
async def update_entity(
    entity_id: UUID,
    entity_data: SemanticEntityUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SemanticEntity:
    """
    Update a semantic entity.

    Args:
        entity_id: Entity ID
        entity_data: Entity update data
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated semantic entity

    Raises:
        HTTPException: 404 if entity not found
    """
    result = await db.execute(
        select(SemanticEntity)
        .where(
            SemanticEntity.id == entity_id,
            SemanticEntity.owner_id == current_user.id
        )
        .options(
            selectinload(SemanticEntity.dimensions),
            selectinload(SemanticEntity.measures)
        )
    )
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )

    # Update fields
    update_data = entity_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entity, field, value)

    await db.commit()
    await db.refresh(entity)
    return entity


@router.delete("/entities/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entity(
    entity_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a semantic entity (cascades to dimensions and measures).

    Args:
        entity_id: Entity ID
        current_user: Authenticated user
        db: Database session

    Raises:
        HTTPException: 404 if entity not found
    """
    result = await db.execute(
        select(SemanticEntity).where(
            SemanticEntity.id == entity_id,
            SemanticEntity.owner_id == current_user.id
        )
    )
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )

    await db.delete(entity)
    await db.commit()


# ==================== Dimension CRUD ====================

@router.post("/entities/{entity_id}/dimensions", response_model=SemanticDimensionResponse, status_code=status.HTTP_201_CREATED)
async def add_dimension(
    entity_id: UUID,
    dimension_data: SemanticDimensionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SemanticDimension:
    """
    Add a dimension to an entity.

    Args:
        entity_id: Entity ID
        dimension_data: Dimension creation data
        current_user: Authenticated user
        db: Database session

    Returns:
        Created dimension

    Raises:
        HTTPException: 404 if entity not found
    """
    # Verify entity ownership
    result = await db.execute(
        select(SemanticEntity).where(
            SemanticEntity.id == entity_id,
            SemanticEntity.owner_id == current_user.id
        )
    )
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )

    # Create dimension
    dimension = SemanticDimension(
        **dimension_data.model_dump(),
        semantic_entity_id=entity_id
    )
    db.add(dimension)
    await db.commit()
    await db.refresh(dimension)
    return dimension


@router.get("/entities/{entity_id}/dimensions", response_model=List[SemanticDimensionResponse])
async def list_dimensions(
    entity_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[SemanticDimension]:
    """
    List all dimensions for an entity.

    Args:
        entity_id: Entity ID
        current_user: Authenticated user
        db: Database session

    Returns:
        List of dimensions

    Raises:
        HTTPException: 404 if entity not found
    """
    # Verify entity ownership
    result = await db.execute(
        select(SemanticEntity).where(
            SemanticEntity.id == entity_id,
            SemanticEntity.owner_id == current_user.id
        )
    )
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )

    # Get dimensions
    result = await db.execute(
        select(SemanticDimension)
        .where(SemanticDimension.semantic_entity_id == entity_id)
        .order_by(SemanticDimension.display_order, SemanticDimension.name)
    )
    return result.scalars().all()


@router.put("/dimensions/{dimension_id}", response_model=SemanticDimensionResponse)
async def update_dimension(
    dimension_id: UUID,
    dimension_data: SemanticDimensionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SemanticDimension:
    """
    Update a dimension.

    Args:
        dimension_id: Dimension ID
        dimension_data: Dimension update data
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated dimension

    Raises:
        HTTPException: 404 if dimension not found or not owned
    """
    # Get dimension with entity for ownership check
    result = await db.execute(
        select(SemanticDimension)
        .join(SemanticEntity)
        .where(
            SemanticDimension.id == dimension_id,
            SemanticEntity.owner_id == current_user.id
        )
    )
    dimension = result.scalar_one_or_none()

    if not dimension:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dimension not found"
        )

    # Update fields
    update_data = dimension_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dimension, field, value)

    await db.commit()
    await db.refresh(dimension)
    return dimension


@router.delete("/dimensions/{dimension_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dimension(
    dimension_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a dimension.

    Args:
        dimension_id: Dimension ID
        current_user: Authenticated user
        db: Database session

    Raises:
        HTTPException: 404 if dimension not found or not owned
    """
    # Get dimension with entity for ownership check
    result = await db.execute(
        select(SemanticDimension)
        .join(SemanticEntity)
        .where(
            SemanticDimension.id == dimension_id,
            SemanticEntity.owner_id == current_user.id
        )
    )
    dimension = result.scalar_one_or_none()

    if not dimension:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dimension not found"
        )

    await db.delete(dimension)
    await db.commit()


# ==================== Measure CRUD ====================

@router.post("/entities/{entity_id}/measures", response_model=SemanticMeasureResponse, status_code=status.HTTP_201_CREATED)
async def add_measure(
    entity_id: UUID,
    measure_data: SemanticMeasureCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SemanticMeasure:
    """
    Add a measure to an entity.

    Args:
        entity_id: Entity ID
        measure_data: Measure creation data
        current_user: Authenticated user
        db: Database session

    Returns:
        Created measure

    Raises:
        HTTPException: 404 if entity not found
    """
    # Verify entity ownership
    result = await db.execute(
        select(SemanticEntity).where(
            SemanticEntity.id == entity_id,
            SemanticEntity.owner_id == current_user.id
        )
    )
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )

    # Create measure
    measure = SemanticMeasure(
        **measure_data.model_dump(),
        semantic_entity_id=entity_id
    )
    db.add(measure)
    await db.commit()
    await db.refresh(measure)
    return measure


@router.get("/entities/{entity_id}/measures", response_model=List[SemanticMeasureResponse])
async def list_measures(
    entity_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[SemanticMeasure]:
    """
    List all measures for an entity.

    Args:
        entity_id: Entity ID
        current_user: Authenticated user
        db: Database session

    Returns:
        List of measures

    Raises:
        HTTPException: 404 if entity not found
    """
    # Verify entity ownership
    result = await db.execute(
        select(SemanticEntity).where(
            SemanticEntity.id == entity_id,
            SemanticEntity.owner_id == current_user.id
        )
    )
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )

    # Get measures
    result = await db.execute(
        select(SemanticMeasure)
        .where(SemanticMeasure.semantic_entity_id == entity_id)
        .order_by(SemanticMeasure.name)
    )
    return result.scalars().all()


@router.put("/measures/{measure_id}", response_model=SemanticMeasureResponse)
async def update_measure(
    measure_id: UUID,
    measure_data: SemanticMeasureUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SemanticMeasure:
    """
    Update a measure.

    Args:
        measure_id: Measure ID
        measure_data: Measure update data
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated measure

    Raises:
        HTTPException: 404 if measure not found or not owned
    """
    # Get measure with entity for ownership check
    result = await db.execute(
        select(SemanticMeasure)
        .join(SemanticEntity)
        .where(
            SemanticMeasure.id == measure_id,
            SemanticEntity.owner_id == current_user.id
        )
    )
    measure = result.scalar_one_or_none()

    if not measure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Measure not found"
        )

    # Update fields
    update_data = measure_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(measure, field, value)

    await db.commit()
    await db.refresh(measure)
    return measure


@router.delete("/measures/{measure_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_measure(
    measure_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a measure.

    Args:
        measure_id: Measure ID
        current_user: Authenticated user
        db: Database session

    Raises:
        HTTPException: 404 if measure not found or not owned
    """
    # Get measure with entity for ownership check
    result = await db.execute(
        select(SemanticMeasure)
        .join(SemanticEntity)
        .where(
            SemanticMeasure.id == measure_id,
            SemanticEntity.owner_id == current_user.id
        )
    )
    measure = result.scalar_one_or_none()

    if not measure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Measure not found"
        )

    await db.delete(measure)
    await db.commit()


# ==================== Catalog Endpoint ====================

@router.get("/catalog", response_model=SemanticCatalogResponse)
async def get_semantic_catalog(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SemanticCatalogResponse:
    """
    Get complete semantic catalog for frontend discovery.

    Returns all entities with their dimensions and measures,
    providing a comprehensive view of the semantic layer.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        Complete semantic catalog with totals
    """
    # Fetch all entities with dimensions and measures in one query
    result = await db.execute(
        select(SemanticEntity)
        .where(SemanticEntity.owner_id == current_user.id)
        .options(
            selectinload(SemanticEntity.dimensions),
            selectinload(SemanticEntity.measures)
        )
        .order_by(SemanticEntity.name)
    )
    entities = result.scalars().all()

    # Build catalog response
    catalog_entities = []
    total_dimensions = 0
    total_measures = 0

    for entity in entities:
        total_dimensions += len(entity.dimensions)
        total_measures += len(entity.measures)

        catalog_entities.append(SemanticCatalogEntity(
            id=entity.id,
            name=entity.name,
            plural_name=entity.plural_name,
            description=entity.description,
            primary_table=entity.primary_table,
            is_certified=entity.is_certified,
            tags=entity.tags,
            dimensions=[
                SemanticDimensionResponse.model_validate(dim)
                for dim in entity.dimensions
            ],
            measures=[
                SemanticMeasureResponse.model_validate(meas)
                for meas in entity.measures
            ]
        ))

    return SemanticCatalogResponse(
        entities=catalog_entities,
        total_entities=len(entities),
        total_dimensions=total_dimensions,
        total_measures=total_measures
    )
