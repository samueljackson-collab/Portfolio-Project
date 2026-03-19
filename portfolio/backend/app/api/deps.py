from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import decode_token
from ..crud import get_content
from ..db import get_db
from ..models import Content

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = decode_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return int(sub)


async def get_db_session() -> AsyncSession:
    async for session in get_db():
        yield session


async def get_owned_content(
    content_id: int,
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> Content:
    content = await get_content(session, content_id=content_id, owner_id=current_user_id)
    if content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    return content
