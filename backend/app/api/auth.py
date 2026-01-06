"""Authentication API endpoints."""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User, UserSession
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_token_hash
)
from app.api.deps import get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Created user object

    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username exists
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=get_password_hash(user_data.password),
        is_active=True,
        is_superuser=False
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Login with username and password.

    Args:
        credentials: Login credentials (username and password)
        db: Database session

    Returns:
        Access token and user data

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by username
    result = await db.execute(
        select(User).where(User.username == credentials.username)
    )
    user = result.scalar_one_or_none()

    # Verify user and password
    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Create access token
    access_token = create_access_token(user.id)
    token_hash = get_token_hash(access_token)

    # Create session
    expires_at = datetime.utcnow() + timedelta(hours=settings.access_token_expire_hours)
    session = UserSession(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
        last_activity_at=datetime.utcnow()
    )

    db.add(session)
    await db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Logout current user (invalidate session).

    Args:
        current_user: Current authenticated user
        db: Database session
    """
    # Delete all active sessions for the user
    result = await db.execute(
        select(UserSession)
        .where(UserSession.user_id == current_user.id)
        .where(UserSession.expires_at > datetime.utcnow())
    )
    sessions = result.scalars().all()

    for session in sessions:
        await db.delete(session)

    await db.commit()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user object
    """
    return current_user
