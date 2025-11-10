from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_current_user
from ..database import get_session
from ..models import Content, User
from ..schemas import ContentCreate, ContentRead, ContentUpdate

router = APIRouter(prefix="/api/content", tags=["content"])


@router.get("/", response_model=List[ContentRead])
async def list_content(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> List[Content]:
    result = await session.execute(select(Content).where(Content.owner_id == current_user.id))
    return result.scalars().all()


@router.post("/", response_model=ContentRead, status_code=status.HTTP_201_CREATED)
async def create_content(
    payload: ContentCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Content:
    content = Content(title=payload.title, body=payload.body, owner_id=current_user.id)
    session.add(content)
    await session.commit()
    await session.refresh(content)
    return content


@router.get("/{content_id}", response_model=ContentRead)
async def get_content(
    content_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Content:
    content = await session.get(Content, content_id)
    if content is None or content.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    return content


@router.put("/{content_id}", response_model=ContentRead)
async def update_content(
    content_id: int,
    payload: ContentUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Content:
    content = await session.get(Content, content_id)
    if content is None or content.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")

    if payload.title is not None:
        content.title = payload.title
    if payload.body is not None:
        content.body = payload.body

    await session.commit()
    await session.refresh(content)
    return content


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    content = await session.get(Content, content_id)
    if content is None or content.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")

    await session.delete(content)
    await session.commit()
    return None
