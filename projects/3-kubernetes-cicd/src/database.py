"""
Database connectivity module for Kubernetes CI/CD Demo.

Provides async database operations using SQLAlchemy with connection pooling.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)


# Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "5"))
DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
DATABASE_POOL_TIMEOUT = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))


# Engine singleton
_engine = None
_session_factory = None


def get_engine():
    """Get or create the database engine."""
    global _engine

    if _engine is None:
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable not set")

        # Convert postgres:// to postgresql+asyncpg://
        db_url = DATABASE_URL
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        _engine = create_async_engine(
            db_url,
            pool_size=DATABASE_POOL_SIZE,
            max_overflow=DATABASE_MAX_OVERFLOW,
            pool_timeout=DATABASE_POOL_TIMEOUT,
            pool_pre_ping=True,  # Verify connections before use
            echo=os.getenv("DATABASE_ECHO", "false").lower() == "true"
        )
        logger.info("Database engine created")

    return _engine


def get_session_factory():
    """Get or create the session factory."""
    global _session_factory

    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        logger.info("Session factory created")

    return _session_factory


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def check_connection() -> bool:
    """
    Check database connectivity.

    Returns True if database is accessible, False otherwise.
    Used for Kubernetes readiness probes.
    """
    if not DATABASE_URL:
        logger.debug("No DATABASE_URL configured, skipping connection check")
        return True

    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.warning(f"Database connection check failed: {e}")
        return False


async def init_database():
    """Initialize database (create tables, run migrations, etc.)."""
    if not DATABASE_URL:
        logger.info("No DATABASE_URL configured, skipping database initialization")
        return

    try:
        engine = get_engine()
        async with engine.begin() as conn:
            # Add your table creation logic here
            # await conn.run_sync(Base.metadata.create_all)
            logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def close_database():
    """Close database connections."""
    global _engine, _session_factory

    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database connections closed")


# Example model operations
class DatabaseOperations:
    """Example database operations."""

    @staticmethod
    async def health_check() -> dict:
        """Perform a health check query."""
        try:
            engine = get_engine()
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT version()"))
                version = result.scalar()
                return {
                    "status": "healthy",
                    "database_version": version
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    @staticmethod
    async def get_connection_pool_stats() -> dict:
        """Get connection pool statistics."""
        try:
            engine = get_engine()
            pool = engine.pool
            return {
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalidated()
            }
        except Exception as e:
            return {"error": str(e)}
