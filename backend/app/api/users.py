"""User management API endpoints (Admin only)."""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.api.deps import get_current_user, get_current_superuser
from app.models.user import User
from app.schemas.user import (
    UserResponse,
    UserListResponse,
    UserUpdate,
    PasswordReset,
)
from app.utils.security import get_password_hash

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("", response_model=UserListResponse)
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    is_superuser: Optional[bool] = None,
) -> dict:
    """
    List all users (Superuser only).

    Args:
        db: Database session
        current_user: Current superuser
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_active: Filter by active status
        is_superuser: Filter by superuser status

    Returns:
        List of users and total count
    """
    query = select(User)

    # Apply filters
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    if is_superuser is not None:
        query = query.where(User.is_superuser == is_superuser)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated users
    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = result.scalars().all()

    return {
        "users": users,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> User:
    """
    Get a specific user by ID (Superuser only).

    Args:
        user_id: User ID
        db: Database session
        current_user: Current superuser

    Returns:
        User object

    Raises:
        HTTPException: If user not found
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> User:
    """
    Update a user (Superuser only).

    Args:
        user_id: User ID
        user_data: User update data
        db: Database session
        current_user: Current superuser

    Returns:
        Updated user object

    Raises:
        HTTPException: If user not found or validation fails
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if username is being changed and already exists
    if user_data.username and user_data.username != user.username:
        existing = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    # Check if email is being changed and already exists
    if user_data.email and user_data.email != user.email:
        existing = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already taken"
            )

    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    user.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)

    return user


@router.post("/{user_id}/reset-password", response_model=UserResponse)
async def reset_user_password(
    user_id: UUID,
    password_data: PasswordReset,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> User:
    """
    Reset a user's password (Superuser only).

    Args:
        user_id: User ID
        password_data: New password
        db: Database session
        current_user: Current superuser

    Returns:
        Updated user object

    Raises:
        HTTPException: If user not found
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update password
    user.password_hash = get_password_hash(password_data.new_password)
    user.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)

    return user


@router.post("/{user_id}/promote-superuser", response_model=UserResponse)
async def promote_to_superuser(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> User:
    """
    Promote a user to superuser (Superuser only).

    Args:
        user_id: User ID
        db: Database session
        current_user: Current superuser

    Returns:
        Updated user object

    Raises:
        HTTPException: If user not found
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_superuser = True
    user.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)

    return user


@router.post("/{user_id}/demote-superuser", response_model=UserResponse)
async def demote_from_superuser(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> User:
    """
    Demote a superuser to regular user (Superuser only).

    Args:
        user_id: User ID
        db: Database session
        current_user: Current superuser

    Returns:
        Updated user object

    Raises:
        HTTPException: If user not found or trying to demote self
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot demote yourself"
        )

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_superuser = False
    user.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)

    return user


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> User:
    """
    Activate a user account (Superuser only).

    Args:
        user_id: User ID
        db: Database session
        current_user: Current superuser

    Returns:
        Updated user object

    Raises:
        HTTPException: If user not found
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = True
    user.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)

    return user


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> User:
    """
    Deactivate a user account (Superuser only).

    Args:
        user_id: User ID
        db: Database session
        current_user: Current superuser

    Returns:
        Updated user object

    Raises:
        HTTPException: If user not found or trying to deactivate self
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself"
        )

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = False
    user.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> None:
    """
    Delete a user (Superuser only).

    Args:
        user_id: User ID
        db: Database session
        current_user: Current superuser

    Raises:
        HTTPException: If user not found or trying to delete self
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await db.delete(user)
    await db.commit()
