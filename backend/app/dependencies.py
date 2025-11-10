"""
FastAPI dependency injection utilities.

Dependencies are reusable components that can be injected into route handlers.
They handle common tasks like:
- Database session management
- User authentication
- Permission checks
"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.auth import decode_access_token
from app.models import User


# Security scheme for Swagger UI
security = HTTPBearer(
    scheme_name="Bearer Token",
    description="JWT access token from login endpoint"
)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    Dependency to get the currently authenticated user.

    This dependency:
    1. Extracts the token from Authorization header
    2. Validates and decodes the JWT token
    3. Looks up the user in the database
    4. Returns the User object or raises 401

    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session (injected by FastAPI)

    Returns:
        User: The authenticated user object

    Raises:
        HTTPException: 401 if token invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Extract token from credentials
        token = credentials.credentials

        # Decode and validate token
        payload = decode_access_token(token)
        email: str = payload.get("sub")

        if email is None:
            raise credentials_exception

    except Exception as e:
        raise credentials_exception from e

    # Look up user in database
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    # Check if user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency that requires an active user.

    Args:
        current_user: User object from get_current_user dependency

    Returns:
        User: The active user object

    Raises:
        HTTPException: 400 if user account is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


# Type alias for cleaner endpoint signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


# Optional security scheme (doesn't raise on missing token)
optional_security = HTTPBearer(
    scheme_name="Bearer Token (Optional)",
    description="JWT access token from login endpoint (optional)",
    auto_error=False
)


async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(optional_security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User | None:
    """
    Dependency to optionally get the currently authenticated user.
    
    Unlike get_current_user, this dependency returns None if no token
    is provided instead of raising a 401 error. This is useful for
    endpoints that behave differently for authenticated vs anonymous users.
    
    Args:
        credentials: HTTP Bearer token from Authorization header (optional)
        db: Database session (injected by FastAPI)
    
    Returns:
        User | None: The authenticated user object or None if not authenticated
    """
    if credentials is None:
        return None
    
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Decode and validate token
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        
        if email is None:
            return None
        
        # Look up user in database
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        # Only return active users
        if user and user.is_active:
            return user
        
        return None
        
    except Exception:
        # If anything goes wrong, just return None (not authenticated)
        return None


# Type alias for optional user
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
