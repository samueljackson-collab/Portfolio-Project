from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..auth import create_access_token, create_refresh_token, get_password_hash, verify_password, decode_token
from ..database import get_session

router = APIRouter()


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(payload: schemas.UserCreate, session: AsyncSession = Depends(get_session)):
    """Create a user record and hash the password before persisting it."""

    result = await session.execute(select(models.User).where(models.User.email == payload.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = models.User(email=payload.email, hashed_password=get_password_hash(payload.password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/login", response_model=schemas.Token)
async def login(payload: schemas.UserLogin, session: AsyncSession = Depends(get_session)):
    """Authenticate a user and issue access/refresh tokens."""

    result = await session.execute(select(models.User).where(models.User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    return schemas.Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(data: schemas.Token, session: AsyncSession = Depends(get_session)):
    """Exchange a refresh token for a new access/refresh pair."""

    payload = decode_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user_id = payload.get("sub")
    result = await session.execute(select(models.User).where(models.User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    return schemas.Token(access_token=access_token, refresh_token=refresh_token)
