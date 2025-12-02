"""
Content management endpoints for CRUD operations.

This module provides:
- List all content (public and user's private)
- Get single content item
- Create new content
- Update existing content
- Delete content
"""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.database import get_db
from app.models import User, Content
from app.schemas import (
    ContentCreate,
    ContentUpdate,
    ContentResponse,
    ContentListResponse
)
from app.dependencies import (
    get_current_user,
    get_optional_user,
    raise_not_found,
    check_ownership,
)


router = APIRouter(
    prefix="/content",
    tags=["Content"],
)


@router.get(
    "",
    response_model=ContentListResponse,
    summary="List Content",
    description="Get paginated list of content items with optional filtering"
)
async def list_content(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    published_only: bool = Query(True, description="Show only published content"),
    search: Optional[str] = Query(None, description="Search in title and body")
) -> ContentListResponse:
    """
    List content items with pagination and filtering.

    Args:
        db: Database session
        current_user: Current user (optional, from auth token)
        page: Page number (1-indexed)
        page_size: Number of items per page
        published_only: Filter to published content only
        search: Search term for title/body

    Returns:
        ContentListResponse: Paginated content list with metadata
    """
    # Build base query
    query = select(Content)

    # Apply authorization filter
    if current_user:
        # Authenticated: show own content + published from others
        query = query.where(
            or_(
                Content.owner_id == current_user.id,
                Content.is_published == True
            )
        )
    else:
        # Not authenticated: only published content regardless of flag
        published_only = True
        query = query.where(Content.is_published == True)

    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Content.title.ilike(search_pattern),
                Content.body.ilike(search_pattern)
            )
        )

    # Count total items (before pagination)
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Order by creation date (newest first)
    query = query.order_by(Content.created_at.desc())

    # Execute query
    result = await db.execute(query)
    items = result.scalars().all()

    # Calculate total pages
    pages = (total + page_size - 1) // page_size

    return ContentListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get(
    "/{content_id}",
    response_model=ContentResponse,
    summary="Get Content",
    description="Get a single content item by ID"
)
async def get_content(
    content_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
) -> Content:
    """
    Get a single content item by ID.

    Args:
        content_id: UUID of content item
        db: Database session
        current_user: Current user (optional)

    Returns:
        ContentResponse: Content item data

    Raises:
        HTTPException 404: Content not found or not authorized
    """
    result = await db.execute(
        select(Content).where(Content.id == content_id)
    )
    content = result.scalar_one_or_none()

    if not content:
        raise_not_found("Content")

    # Check authorization
    if not content.is_published:
        if not current_user or content.owner_id != current_user.id:
            raise_not_found("Content")

    return content


@router.post(
    "",
    response_model=ContentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Content",
    description="Create a new content item (requires authentication)"
)
async def create_content(
    content_data: ContentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Content:
    """
    Create a new content item.

    Args:
        content_data: Content creation data
        current_user: Authenticated user
        db: Database session

    Returns:
        ContentResponse: Created content item
    """
    new_content = Content(
        **content_data.model_dump(),
        owner_id=current_user.id
    )

    db.add(new_content)
    await db.commit()
    await db.refresh(new_content)

    return new_content


@router.put(
    "/{content_id}",
    response_model=ContentResponse,
    summary="Update Content",
    description="Update an existing content item (owner only)"
)
async def update_content(
    content_id: UUID,
    content_data: ContentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Content:
    """
    Update an existing content item.

    Args:
        content_id: UUID of content to update
        content_data: Updated content data
        current_user: Authenticated user
        db: Database session

    Returns:
        ContentResponse: Updated content item

    Raises:
        HTTPException 404: Content not found
        HTTPException 403: Not authorized (not the owner)
    """
    result = await db.execute(
        select(Content).where(Content.id == content_id)
    )
    content = result.scalar_one_or_none()

    if not content:
        raise_not_found("Content")

    # Check ownership
    check_ownership(content, current_user, "update this content")

    # Update fields that were provided
    update_data = content_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(content, field, value)

    await db.commit()
    await db.refresh(content)

    return content


@router.delete(
    "/{content_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Content",
    description="Delete a content item (owner only)"
)
async def delete_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a content item.

    Args:
        content_id: UUID of content to delete
        current_user: Authenticated user
        db: Database session

    Raises:
        HTTPException 404: Content not found
        HTTPException 403: Not authorized (not the owner)
    """
    result = await db.execute(
        select(Content).where(Content.id == content_id)
    )
    content = result.scalar_one_or_none()

    if not content:
        raise_not_found("Content")

    # Check ownership
    check_ownership(content, current_user, "delete this content")

    await db.delete(content)
    await db.commit()
