"""
Database configuration and session management.

This module provides:
- Async SQLAlchemy engine
- Session factory with connection pooling
- Base class for ORM models
- Database session dependency for FastAPI
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

from app.config import settings


# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL in debug mode
    future=True,  # Use SQLAlchemy 2.0 API
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,  # Number of connections to maintain
    max_overflow=10,  # Additional connections when pool is exhausted
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for ORM models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a per-request database session for FastAPI dependency injection.
    
    Yields a session that will be committed if the caller completes successfully, rolled back if an exception is raised, and always closed after use.
    
    Returns:
        AsyncSession: A session bound to the configured engine; committed on normal completion, rolled back on exception, and closed when the dependency context exits.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.

    This creates all tables defined in models.
    In production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close and dispose the module-level database engine, releasing all pooled connections.
    
    This ensures the engine is disposed and its connection pool is closed; call during application shutdown to free database resources.
    """
    await engine.dispose()