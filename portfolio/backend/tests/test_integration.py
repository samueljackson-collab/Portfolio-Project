import os

import pytest
from httpx import AsyncClient

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("DEFAULT_ADMIN_USERNAME", "admin")
os.environ.setdefault("DEFAULT_ADMIN_PASSWORD", "adminpass")

from app.main import app  # noqa: E402  pylint: disable=wrong-import-position
from app.db import init_db  # noqa: E402


@pytest.fixture(autouse=True, scope="module")
async def setup_db():
    await init_db()
    yield


@pytest.mark.anyio
async def test_auth_and_project_crud():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/auth/token",
            data={"username": "admin", "password": "adminpass"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        token = response.json()["access_token"]

        create_resp = await client.post(
            "/projects",
            json={"title": "Test Project", "description": "Integration"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert create_resp.status_code == 201
        project_id = create_resp.json()["id"]

        list_resp = await client.get(
            "/projects",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert list_resp.status_code == 200
        assert any(item["id"] == project_id for item in list_resp.json())

        detail_resp = await client.get(
            f"/projects/{project_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert detail_resp.status_code == 200
        assert detail_resp.json()["title"] == "Test Project"
