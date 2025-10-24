"""Content management API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, get_optional_current_user
from app.models import Content, User
from app.schemas import ContentCreate, ContentListResponse, ContentResponse, ContentUpdate

router = APIRouter(prefix="/content", tags=["Content"])


@router.get(
    "",
    response_model=ContentListResponse,
    summary="List content items",
    description="Return a paginated list of content items with optional filters.",
)
async def list_content(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    published_only: bool = Query(True, description="Return only published content"),
    search: Optional[str] = Query(None, description="Search string for title/body"),
) -> ContentListResponse:
    """Return content items visible to the requester."""

    # Start with a base select statement; filters below tailor visibility.
    base_query = select(Content)

    if current_user is not None:
        base_query = base_query.where(
            or_(Content.owner_id == current_user.id, Content.is_published.is_(True))
        )
    elif published_only:
        base_query = base_query.where(Content.is_published.is_(True))

    if search:
        pattern = f"%{search}%"
        base_query = base_query.where(
            or_(Content.title.ilike(pattern), Content.body.ilike(pattern))
        )

    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    offset = (page - 1) * page_size
    items_result = await db.execute(
        base_query.order_by(Content.created_at.desc()).offset(offset).limit(page_size)
    )
    items = items_result.scalars().all()

    pages = (total + page_size - 1) // page_size if total else 0

    return ContentListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/{content_id}",
    response_model=ContentResponse,
    summary="Retrieve a content item",
)
async def get_content(
    content_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> Content:
    """Retrieve a single content item respecting publication status."""
    result = await db.execute(select(Content).where(Content.id == content_id))
    content = result.scalar_one_or_none()

    if content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")

    if not content.is_published and (current_user is None or current_user.id != content.owner_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")

    return content


@router.post(
    "",
    response_model=ContentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create content",
)
async def create_content(
    content_data: ContentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Content:
    """Create a new content item owned by the authenticated user."""
    new_content = Content(**content_data.model_dump(), owner_id=current_user.id)
    db.add(new_content)
    await db.commit()
    await db.refresh(new_content)

    return new_content


@router.put(
    "/{content_id}",
    response_model=ContentResponse,
    summary="Update content",
)
async def update_content(
    content_id: UUID,
    content_data: ContentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Content:
    """Update an existing content item if the requester is the owner."""
    result = await db.execute(select(Content).where(Content.id == content_id))
    content = result.scalar_one_or_none()

    if content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")

    if content.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this content",
        )

    update_fields = content_data.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(content, key, value)

    await db.commit()
    await db.refresh(content)

    return content


@router.delete(
    "/{content_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete content",
)
async def delete_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a content item if the requester is the owner."""
    result = await db.execute(select(Content).where(Content.id == content_id))
    content = result.scalar_one_or_none()

    if content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")

    if content.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this content",
        )

    await db.delete(content)
    await db.commit()
