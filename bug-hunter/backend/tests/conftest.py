"""Shared pytest fixtures for Bug Hunter backend tests."""
from __future__ import annotations
import asyncio
import os

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Configure test DB before any app imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["API_KEY"] = ""  # disable auth by default

from database import Base, get_db  # noqa: E402
import database as _database       # noqa: E402  — for patching AsyncSessionLocal
from main import app               # noqa: E402

# ── Test-scoped engine with StaticPool so all connections share one in-memory DB
_test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSession = async_sessionmaker(_test_engine, class_=AsyncSession, expire_on_commit=False)

# Patch the module-level session factory so background tasks use the test DB
_database.AsyncSessionLocal = _TestSession


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset in-memory rate limit counters before each test."""
    from limiter import limiter
    limiter._storage.reset()
    yield


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db():
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with _TestSession() as session:
        yield session

    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db):
    async def override_get_db():
        async with _TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ── Code samples used across tests ───────────────────────────────────────────

# Triggers "SQL Injection in Android rawQuery()":
# pattern: rawQuery\s*\(\s*[\"']?.*\+
ANDROID_VULNERABLE = """
import android.database.sqlite.SQLiteDatabase;

public class UserDao {
    public void getUser(String userId) {
        db.rawQuery("SELECT * FROM users WHERE id = " + userId, null);
        setJavaScriptEnabled(true);
    }
}
"""

# Triggers "Sensitive Data Logged in Production Code" (iOS):
# pattern: NSLog\s*\([^)]*(?:password|token|...)
IOS_VULNERABLE = """
NSLog(@"User password: %@", password);
NSLog(@"Auth token: %@", token);
"""

# Triggers "Process Execution with Variable Path" (Windows):
# pattern: Process\.Start\s*\(\s*(?:[a-zA-Z_]\w*)\s*\)
WINDOWS_VULNERABLE = """
string ConnectionString = "Server=myserver;Database=db;User ID=sa;Password=secret123;";
Process.Start(command);
"""

# Triggers "eval() — Arbitrary JavaScript Execution" (Web):
WEB_VULNERABLE = """
const express = require('express');
app.post('/run', (req, res) => {
    eval(req.body.code);
});
"""
