from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.saved_query import SavedQuery
from app.schemas.saved_query import (
    SavedQueryCreate,
    SavedQueryUpdate,
    SavedQueryResponse,
    SavedQueryListResponse,
)

router = APIRouter(prefix="/saved-queries", tags=["Saved Queries"])


@router.post("", response_model=SavedQueryResponse, status_code=status.HTTP_201_CREATED)
async def create_saved_query(
    query_data: SavedQueryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new saved query."""
    saved_query = SavedQuery(
        owner_id=current_user.id,
        name=query_data.name,
        description=query_data.description,
        entity_id=query_data.entity_id,
        query_config=query_data.query_config,
        is_favorite=query_data.is_favorite,
    )

    db.add(saved_query)
    db.commit()
    db.refresh(saved_query)

    return saved_query


@router.get("", response_model=SavedQueryListResponse)
async def list_saved_queries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    favorites_only: bool = False,
):
    """List all saved queries for the current user."""
    query = db.query(SavedQuery).filter(SavedQuery.owner_id == current_user.id)

    if favorites_only:
        query = query.filter(SavedQuery.is_favorite == True)

    queries = query.order_by(desc(SavedQuery.updated_at)).all()

    return SavedQueryListResponse(queries=queries, total=len(queries))


@router.get("/{query_id}", response_model=SavedQueryResponse)
async def get_saved_query(
    query_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific saved query."""
    saved_query = db.query(SavedQuery).filter(
        SavedQuery.id == query_id,
        SavedQuery.owner_id == current_user.id,
    ).first()

    if not saved_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved query not found",
        )

    return saved_query


@router.put("/{query_id}", response_model=SavedQueryResponse)
async def update_saved_query(
    query_id: UUID,
    query_data: SavedQueryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a saved query."""
    saved_query = db.query(SavedQuery).filter(
        SavedQuery.id == query_id,
        SavedQuery.owner_id == current_user.id,
    ).first()

    if not saved_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved query not found",
        )

    # Update fields if provided
    update_data = query_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(saved_query, field, value)

    db.commit()
    db.refresh(saved_query)

    return saved_query


@router.delete("/{query_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_query(
    query_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a saved query."""
    saved_query = db.query(SavedQuery).filter(
        SavedQuery.id == query_id,
        SavedQuery.owner_id == current_user.id,
    ).first()

    if not saved_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved query not found",
        )

    db.delete(saved_query)
    db.commit()

    return None
