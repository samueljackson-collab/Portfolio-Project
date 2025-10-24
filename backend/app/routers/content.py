"""Content CRUD routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..dependencies import get_current_user, get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.ContentRead])
async def list_content(
    session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> list[models.Content]:
    query = select(models.Content).where(models.Content.owner_id == current_user.id)
    result = await session.execute(query)
    return list(result.scalars())


@router.post("/", response_model=schemas.ContentRead, status_code=status.HTTP_201_CREATED)
async def create_content(
    content_in: schemas.ContentCreate,
    session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> models.Content:
    content = models.Content(**content_in.model_dump(), owner_id=current_user.id)
    session.add(content)
    await session.commit()
    await session.refresh(content)
    return content


@router.put("/{content_id}", response_model=schemas.ContentRead)
async def update_content(
    content_id: str,
    content_in: schemas.ContentUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> models.Content:
    result = await session.execute(
        select(models.Content).where(
            models.Content.id == content_id,
            models.Content.owner_id == current_user.id,
        )
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    for key, value in content_in.model_dump(exclude_unset=True).items():
        setattr(content, key, value)
    await session.commit()
    await session.refresh(content)
    return content


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: str,
    session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> None:
    result = await session.execute(
        select(models.Content).where(
            models.Content.id == content_id,
            models.Content.owner_id == current_user.id,
        )
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    await session.delete(content)
    await session.commit()
