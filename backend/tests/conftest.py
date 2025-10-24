from __future__ import annotations

import os

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Provide defaults so tests can spin up without additional configuration.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret")

from app.main import app
from app.auth import get_password_hash
from app.database import get_session
from app.models import Base, User

TEST_DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_async_engine(TEST_DATABASE_URL, future=True)
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Create a temporary SQLite database for each test function."""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session: AsyncSession = TestingSessionLocal()
    try:
        yield session
    finally:
        await session.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
def override_session(db_session: AsyncSession):
    """Inject the test session into the FastAPI dependency graph."""

    async def _get_session_override():
        async with db_session.begin():
            yield db_session

    app.dependency_overrides[get_session] = _get_session_override
    yield
    app.dependency_overrides.pop(get_session, None)


@pytest_asyncio.fixture
async def async_client(override_session):
    """HTTPX async client that exercises the FastAPI app in tests."""

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def user_factory(db_session: AsyncSession):
    """Helper that inserts users directly into the test database."""

    created_users: list[User] = []

    async def _factory(email: str, password: str) -> User:
        user = User(email=email, hashed_password=get_password_hash(password))
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        created_users.append(user)
        return user

    yield _factory

    for user in created_users:
        await db_session.delete(user)
    await db_session.commit()
