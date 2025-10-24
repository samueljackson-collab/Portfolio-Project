import os
import tempfile

import pytest
from fastapi import status
from httpx import AsyncClient

# Ensure the app uses an isolated SQLite database for test runs.
_fd, _path = tempfile.mkstemp(prefix="portfolio-test-", suffix=".sqlite")
os.close(_fd)
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{_path}")

from app.main import app  # noqa: E402  (import after env setup)


@pytest.mark.asyncio
async def test_complete_user_workflow():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.post(
            "/api/auth/register",
            json={"email": "workflow@example.com", "password": "workflowpass123"},
        )
        assert r.status_code == status.HTTP_201_CREATED
        r = await client.post(
            "/api/auth/login",
            data={"username": "workflow@example.com", "password": "workflowpass123"},
        )
        assert r.status_code == status.HTTP_200_OK
        token = r.json()["access_token"]
        assert isinstance(token, str) and token
