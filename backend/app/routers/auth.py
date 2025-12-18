"""
Authentication endpoints for user registration and login.

This module handles:
- User registration with validation
- User authentication (login)
- JWT token generation
- Password hashing
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, UserLogin, Token
from app.auth import hash_password, verify_password, create_access_token
from app.config import settings
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Create a new user account with email and password"
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Register a new user account.

    Args:
        user_data: User registration data (email, password)
        db: Database session

    Returns:
        UserResponse: Created user data

    Raises:
        HTTPException 400: If email already registered
    """
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password before storing
    hashed_password = hash_password(user_data.password)

    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user and receive JWT token"
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Token:
    """
    Authenticate user and generate JWT token.

    Args:
        credentials: Login credentials (email, password)
        db: Database session

    Returns:
        Token: JWT access token with expiration

    Raises:
        HTTPException 401: If credentials are invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Look up user
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    # User not found or password incorrect
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise credentials_exception

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Create JWT token
    access_token_expires = timedelta(
        minutes=settings.access_token_expire_minutes
    )
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds())
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User",
    description="Get the currently authenticated user's information"
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get information about the currently authenticated user.

    Args:
        current_user: Authenticated user (injected by dependency)

    Returns:
        UserResponse: Current user's data
    """
    return current_user
