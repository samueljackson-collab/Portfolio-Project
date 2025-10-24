from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..dependencies import get_current_user
from ..database import get_session

router = APIRouter()


@router.get("/", response_model=list[schemas.ContentOut])
async def list_content(
    session: AsyncSession = Depends(get_session),
    current_user: models.User = Depends(get_current_user),
):
    """Return all content owned by the authenticated user sorted by recency."""

    result = await session.execute(
        select(models.Content).where(models.Content.owner_id == current_user.id).order_by(models.Content.created_at.desc())
    )
    return list(result.scalars())


@router.post("/", response_model=schemas.ContentOut, status_code=status.HTTP_201_CREATED)
async def create_content(
    payload: schemas.ContentCreate,
    session: AsyncSession = Depends(get_session),
    current_user: models.User = Depends(get_current_user),
):
    """Insert a new content record tied to the requesting user."""

    content = models.Content(**payload.model_dump(), owner_id=current_user.id)
    session.add(content)
    await session.commit()
    await session.refresh(content)
    return content


@router.put("/{content_id}", response_model=schemas.ContentOut)
async def update_content(
    content_id: uuid.UUID,
    payload: schemas.ContentUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: models.User = Depends(get_current_user),
):
    """Patch mutable fields on a content record after verifying ownership."""

    result = await session.execute(
        select(models.Content).where(models.Content.id == content_id, models.Content.owner_id == current_user.id)
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(content, key, value)
    await session.commit()
    await session.refresh(content)
    return content


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: models.User = Depends(get_current_user),
):
    """Remove a content record owned by the authenticated user."""

    result = await session.execute(
        select(models.Content).where(models.Content.id == content_id, models.Content.owner_id == current_user.id)
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    await session.delete(content)
    await session.commit()
