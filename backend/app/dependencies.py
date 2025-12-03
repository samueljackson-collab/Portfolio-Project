"""
FastAPI dependency injection utilities.

Dependencies are reusable components that can be injected into route handlers.
They handle common tasks like:
- Database session management
- User authentication
- Permission checks
"""

from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.auth import decode_access_token
from app.models import User


# =============================================================================
# Exception Helpers - Reduce code duplication across routers
# =============================================================================

def raise_not_found(resource: str = "Resource") -> None:
    """
    Raise a 404 Not Found HTTP exception.

    Args:
        resource: Name of the resource that was not found
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} not found"
    )


def raise_forbidden(action: str = "perform this action") -> None:
    """
    Raise a 403 Forbidden HTTP exception.

    Args:
        action: Description of the forbidden action
    """
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Not authorized to {action}"
    )


def raise_bad_request(message: str) -> None:
    """
    Raise a 400 Bad Request HTTP exception.

    Args:
        message: Error message describing the bad request
    """
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message
    )


def raise_conflict(message: str) -> None:
    """
    Raise a 409 Conflict HTTP exception.

    Args:
        message: Error message describing the conflict
    """
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=message
    )


def raise_server_error(message: str = "An internal error occurred") -> None:
    """
    Raise a 500 Internal Server Error HTTP exception.

    Args:
        message: Error message
    """
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=message
    )


def check_ownership(resource, current_user: User, action: str = "access this resource") -> None:
    """
    Verify that the current user owns the resource.

    Args:
        resource: Database model instance with owner_id attribute
        current_user: The currently authenticated user
        action: Description of the action being attempted

    Raises:
        HTTPException: 403 if user doesn't own the resource
    """
    if resource.owner_id != current_user.id:
        raise_forbidden(action)


# Security scheme for Swagger UI
security = HTTPBearer(
    scheme_name="Bearer Token",
    description="JWT access token from login endpoint"
)


# Optional security scheme that does not raise when missing credentials
optional_security = HTTPBearer(
    scheme_name="Optional Bearer Token",
    description=(
        "JWT access token. Optional for read-only endpoints, required for mutating operations."
    ),
    auto_error=False,
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


# Optional user dependency ---------------------------------------------------
async def get_optional_user(
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials],
        Depends(optional_security)
    ],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Optional[User]:
    """Return the authenticated user if a token is provided, else ``None``."""

    if not credentials:
        return None

    return await get_current_user(credentials, db)


# Type alias for cleaner endpoint signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
