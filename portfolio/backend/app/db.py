"""Database configuration and session management."""
from __future__ import annotations

import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./portfolio.db")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    """Base declarative class for SQLAlchemy models."""


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional scope around a series of operations."""
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    """Initialize database tables."""
    from . import models  # noqa: F401  # ensure models are imported

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
