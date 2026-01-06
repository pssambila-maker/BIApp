"""Security utilities for password hashing and token generation."""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(user_id: UUID, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.

    Args:
        user_id: User ID to encode in the token
        expires_delta: Token expiration time (default: from settings)

    Returns:
        Encoded JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.access_token_expire_hours)

    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[UUID]:
    """
    Decode and verify JWT access token.

    Args:
        token: JWT token string

    Returns:
        User ID if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return UUID(user_id)
    except JWTError:
        return None


def get_token_hash(token: str) -> str:
    """
    Get hash of token for storage in database.

    Args:
        token: JWT token string

    Returns:
        SHA-256 hash of the token
    """
    import hashlib
    return hashlib.sha256(token.encode()).hexdigest()
