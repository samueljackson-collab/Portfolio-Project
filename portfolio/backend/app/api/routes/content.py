
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ... import schemas
from ...crud import create_content, delete_content, list_content, update_content
from ...models import Content
from ..deps import get_current_user_id, get_db_session, get_owned_content

router = APIRouter(prefix="/api/content", tags=["content"])


@router.post("", response_model=schemas.ContentRead, status_code=status.HTTP_201_CREATED)
async def create_content_item(
    payload: schemas.ContentCreate,
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> schemas.ContentRead:
    content = await create_content(
        session,
        owner_id=current_user_id,
        title=payload.title,
        slug=payload.slug,
        body=payload.body,
    )
    return schemas.ContentRead.model_validate(content)


@router.get("", response_model=list[schemas.ContentRead])
async def list_content_items(
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> list[schemas.ContentRead]:
    contents = await list_content(session, owner_id=current_user_id)
    return [schemas.ContentRead.model_validate(item) for item in contents]


@router.put("/{content_id}", response_model=schemas.ContentRead)
async def update_content_item(
    content_update: schemas.ContentUpdate,
    content: Content = Depends(get_owned_content),
    session: AsyncSession = Depends(get_db_session),
) -> schemas.ContentRead:
    updated = await update_content(
        session,
        db_obj=content,
        title=content_update.title,
        slug=content_update.slug,
        body=content_update.body,
    )
    return schemas.ContentRead.model_validate(updated)


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content_item(
    content: Content = Depends(get_owned_content),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    await delete_content(session, content)
