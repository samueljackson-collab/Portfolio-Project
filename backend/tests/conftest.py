"""Shared pytest fixtures for FastAPI integration tests."""

from __future__ import annotations

import os
import sys
from collections.abc import AsyncGenerator, Callable
from pathlib import Path
from typing import Awaitable
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Ensure the backend package is importable when running tests from repository root.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Provide default environment configuration for tests before importing settings.
os.environ.setdefault("TESTING", "true")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "0123456789abcdefghijklmnopqrstuv")

from app.auth import create_access_token, hash_password  # noqa: E402
from app.config import settings  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.main import create_application  # noqa: E402
from app.models import Content, User  # noqa: E402

settings.testing = True


@pytest_asyncio.fixture()
async def engine() -> AsyncGenerator:
    """Provide a SQLite engine backed by an in-memory database."""
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture()
def session_factory(engine) -> async_sessionmaker[AsyncSession]:
    """Return an async session factory bound to the temporary engine."""
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture()
async def client(session_factory: async_sessionmaker[AsyncSession]):
    """Return an HTTP client bound to a FastAPI test application."""

    app = create_application()

    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:  # pragma: no cover - defensive rollback
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = _get_test_db

    async with AsyncClient(app=app, base_url="http://testserver") as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def create_user(session_factory: async_sessionmaker[AsyncSession]):
    """Factory fixture for creating persisted users."""

    async def _create_user(
        *,
        email: str | None = None,
        password: str = "ValidPass123!",
        is_active: bool = True,
    ) -> tuple[User, str]:
        actual_email = email or f"user-{uuid4().hex}@example.com"
        async with session_factory() as session:
            user = User(
                email=actual_email,
                hashed_password=hash_password(password),
                is_active=is_active,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user, password

    return _create_user


@pytest_asyncio.fixture()
async def create_content(
    session_factory: async_sessionmaker[AsyncSession],
) -> Callable[..., Awaitable[Content]]:
    """Factory fixture for creating content rows tied to users."""

    async def _create_content(
        *,
        owner: User,
        title: str = "Sample Title",
        body: str | None = "Sample body",
        is_published: bool = True,
    ) -> Content:
        async with session_factory() as session:
            content = Content(
                title=title,
                body=body,
                owner_id=owner.id,
                is_published=is_published,
            )
            session.add(content)
            await session.commit()
            await session.refresh(content)
        return content

    return _create_content


@pytest_asyncio.fixture()
async def auth_headers(create_user):
    """Return an authorization header for a newly created active user."""

    user, _ = await create_user()
    token = create_access_token({"sub": user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture()
async def authenticated_user(create_user):
    """Return a tuple of a user and bearer token headers for that user."""

    user, _ = await create_user()
    token = create_access_token({"sub": user.email})
    return user, {"Authorization": f"Bearer {token}"}
