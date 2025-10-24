from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app import models
from app.dependencies import get_db

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(DATABASE_URL, future=True)
AsyncSessionLocal = sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope="function")
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
