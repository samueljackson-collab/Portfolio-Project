"""Database session utilities."""
from __future__ import annotations

from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import get_settings

_settings = get_settings()
_engine = create_async_engine(_settings.database_url, echo=False, future=True)
AsyncSessionLocal = sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)


@asynccontextmanager
async def get_session() -> AsyncSession:
    session: AsyncSession = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
