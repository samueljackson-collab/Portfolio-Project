"""Authentication routes."""
from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import auth, models, schemas
from ..dependencies import get_db

router = APIRouter()


@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_in: schemas.UserCreate, session: AsyncSession = Depends(get_db)) -> models.User:
    existing = await session.execute(select(models.User).where(models.User.email == user_in.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = models.User(email=user_in.email, hashed_password=auth.hash_password(user_in.password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/login", response_model=schemas.TokenPair)
async def login(user_in: schemas.UserCreate, session: AsyncSession = Depends(get_db)) -> schemas.TokenPair:
    result = await session.execute(select(models.User).where(models.User.email == user_in.email))
    user = result.scalar_one_or_none()
    if not user or not auth.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return schemas.TokenPair(
        access_token=auth.create_access_token(user.id),
        refresh_token=auth.create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=schemas.TokenPair)
async def refresh(token_pair: schemas.TokenPair) -> schemas.TokenPair:
    user_id = auth.decode_token(token_pair.refresh_token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return schemas.TokenPair(
        access_token=auth.create_access_token(user_id),
        refresh_token=auth.create_refresh_token(user_id),
    )
