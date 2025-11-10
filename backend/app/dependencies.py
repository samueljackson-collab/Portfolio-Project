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
    Retrieve the currently authenticated User from a Bearer JWT.
    
    Validates the provided Authorization Bearer token, decodes it to extract the subject email, loads the corresponding User from the database, and ensures the account is active.
    
    Returns:
        The User corresponding to the token's subject email.
    
    Raises:
        HTTPException: 401 if the token is missing, invalid, or no matching user is found.
        HTTPException: 403 if the user account exists but is inactive.
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
    Ensure the current user account is active.
    
    Returns:
        The provided User object when active.
    
    Raises:
        HTTPException: 400 if the user's account is not active.
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