"""
Content CRUD routes with ownership and authorization checks.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from app.database import get_db
from app.models import User, Content as ContentModel
from app.schemas import Content, ContentCreate, ContentUpdate
from app.dependencies import get_current_user


router = APIRouter()


@router.post("/", response_model=Content, status_code=status.HTTP_201_CREATED)
async def create_content(
    content: ContentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new content owned by the current user."""
    db_content = ContentModel(**content.model_dump(), owner_id=current_user.id)
    db.add(db_content)
    await db.commit()
    await db.refresh(db_content)
    return db_content


@router.get("/", response_model=List[Content])
async def list_content(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all content owned by the current user."""
    result = await db.execute(
        select(ContentModel)
        .where(ContentModel.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{content_id}", response_model=Content)
async def get_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific content item by ID."""
    result = await db.execute(
        select(ContentModel).where(ContentModel.id == content_id)
    )
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if content.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return content


@router.put("/{content_id}", response_model=Content)
async def update_content(
    content_id: UUID,
    content_update: ContentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a content item owned by the current user."""
    result = await db.execute(
        select(ContentModel).where(ContentModel.id == content_id)
    )
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if content.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = content_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(content, field, value)

    await db.commit()
    await db.refresh(content)
    return content


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a content item owned by the current user."""
    result = await db.execute(
        select(ContentModel).where(ContentModel.id == content_id)
    )
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if content.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(content)
    await db.commit()
    return None
