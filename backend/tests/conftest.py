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
from httpx import AsyncClient
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
    "postgresql+asyncpg://portfolio_user:securepassword@localhost:5432/portfolio_test_db"
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
    """
    Provide a dedicated asyncio event loop for the entire test session.
    
    Yields:
        asyncio.AbstractEventLoop: The event loop created for tests; it is closed after the session completes.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a fresh database session backed by a newly created test database for each test.
    
    Creates all tables before yielding a session, rolls back any changes after the test, and drops all tables once the test completes.
    
    Returns:
        An AsyncSession bound to the test database; tables are created before yielding, changes are rolled back after use, and tables are dropped after the test.
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


@pytest_asyncio.fixture(scope="function")
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an AsyncClient for tests while overriding the app's database dependency to use the given test session.
    
    Parameters:
        test_db (AsyncSession): Async database session to be injected into the application's `get_db` dependency.
    
    Yields:
        AsyncClient: HTTP client bound to the FastAPI app that uses `test_db` for database operations.
    """
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        """
        Provide the test database session for FastAPI dependency injection during tests.
        
        Returns:
            AsyncSession: The active AsyncSession bound to the test database.
        """
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(test_db: AsyncSession) -> User:
    """
    Create and persist a test user with predefined credentials.
    
    Returns:
        User: The persisted User instance (refreshed with DB-generated fields).
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
    Retrieve a JWT access token for the provided test user.
    
    Parameters:
        client (AsyncClient): Test HTTP client used to make the login request.
        test_user (User): The test user whose credentials will be used to authenticate.
    
    Returns:
        str: JWT access token.
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
    client: AsyncClient,
    test_user_token: str
) -> AsyncClient:
    """
    Attach a Bearer Authorization header with the provided token to the given client and return it.
    
    Returns:
        AsyncClient: The same client instance with the `Authorization: Bearer <token>` header set.
    """
    client.headers.update({"Authorization": f"Bearer {test_user_token}"})
    return client


@pytest_asyncio.fixture
async def test_content(
    test_db: AsyncSession,
    test_user: User
) -> Content:
    """
    Create and persist a Content record owned by the provided test user.
    
    Parameters:
        test_db (AsyncSession): Async database session used to persist the content.
        test_user (User): Owner of the created content.
    
    Returns:
        Content: The persisted Content instance with refreshed state (including id).
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
    """
    Return a sample user registration payload for tests.
    
    Returns:
        dict: Dictionary containing `email` (str) and `password` (str) for creating a new user.
    """
    return {
        "email": "newuser@example.com",
        "password": "securepassword123"
    }


@pytest.fixture
def sample_content_data() -> dict:
    """
    Return a sample payload for creating new content.
    
    Returns:
        dict: Example content data with keys 'title' (string), 'body' (string), and 'is_published' (bool).
    """
    return {
        "title": "New Content Item",
        "body": "This is the body of the new content",
        "is_published": False
    }