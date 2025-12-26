"""
Pytest configuration and shared fixtures for backend tests.

This module provides:
- Test database configuration
- Test client fixtures
- User authentication fixtures
- Database session fixtures
"""

import asyncio
import os
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.database import Base, get_db
from app.config import settings
from app.models import User, Content
from app.auth import get_password_hash


# Use test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    # Default to SQLite for faster, dependency-free test execution. A Postgres
    # URL can still be provided via TEST_DATABASE_URL when running in CI.
    "sqlite+aiosqlite:///./test.db"
)


# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the entire test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database for each test.

    This fixture:
    1. Creates all tables
    2. Yields a database session
    3. Rolls back all changes after the test
    4. Drops all tables
    """
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_override(test_db: AsyncSession):
    """Shared dependency override to keep a single session per test."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client(test_db: AsyncSession, db_override) -> AsyncGenerator[AsyncClient, None]:
    """Create an unauthenticated test client."""

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user(test_db: AsyncSession) -> User:
    """
    Create a test user in the database.

    Returns:
        User: Created test user
    """
    user = User(
        email="testuser@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_token(client: AsyncClient, test_user: User) -> str:
    """
    Get authentication token for test user.

    Args:
        client: Test HTTP client
        test_user: Test user instance

    Returns:
        str: JWT access token
    """
    response = await client.post(
        "/auth/login",
        data={
            "username": test_user.email,
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def authenticated_client(
    test_db: AsyncSession,
    test_user_token: str,
    db_override,
) -> AsyncClient:
    """Create a dedicated authenticated client without mutating the base client."""

    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {test_user_token}"}
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as ac:
        yield ac


@pytest_asyncio.fixture
async def test_content(
    test_db: AsyncSession,
    test_user: User
) -> Content:
    """
    Create test content item.

    Args:
        test_db: Test database session
        test_user: Test user instance

    Returns:
        Content: Created test content
    """
    content = Content(
        title="Test Content",
        body="This is test content body",
        owner_id=test_user.id,
        is_published=True
    )
    test_db.add(content)
    await test_db.commit()
    await test_db.refresh(content)
    return content


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user registration data."""
    return {
        "email": "newuser@example.com",
        "password": "securepassword123"
    }


@pytest.fixture
def sample_content_data() -> dict:
    """Sample content creation data."""
    return {
        "title": "New Content Item",
        "body": "This is the body of the new content",
        "is_published": False
    }
