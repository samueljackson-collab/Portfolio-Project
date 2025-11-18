import pytest
from sqlalchemy import select

from app import models
from app.auth import get_password_hash
from app.database import SessionLocal


async def create_admin_user():
    async with SessionLocal() as session:
        existing = await session.execute(select(models.User).where(models.User.username == "admin"))
        if not existing.scalar_one_or_none():
            session.add(
                models.User(
                    email="admin@example.com",
                    username="admin",
                    hashed_password=get_password_hash("admin1234"),
                    is_admin=True,
                )
            )
            await session.commit()


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_admin_can_create_project(client):
    await create_admin_user()
    login_resp = await client.post(
        "/auth/login", data={"username": "admin", "password": "admin1234"}
    )
    token = login_resp.json()["access_token"]

    project_payload = {
        "title": "Test Project",
        "slug": "test-project",
        "description": "A project created in tests",
        "category": "Testing",
        "tags": ["pytest", "fastapi"],
        "featured": False,
    }

    create_resp = await client.post("/projects/", json=project_payload, headers=auth_headers(token))
    assert create_resp.status_code == 200
    data = create_resp.json()
    assert data["slug"] == project_payload["slug"]

    list_resp = await client.get("/projects/")
    assert list_resp.status_code == 200
    assert any(item["slug"] == project_payload["slug"] for item in list_resp.json())


@pytest.mark.asyncio
async def test_non_admin_cannot_create_project(client):
    await client.post(
        "/auth/register",
        json={"email": "user@example.com", "username": "user", "password": "password123"},
    )
    login_resp = await client.post(
        "/auth/login", data={"username": "user", "password": "password123"}
    )
    token = login_resp.json()["access_token"]

    payload = {
        "title": "Unauthorized",
        "slug": "unauth",
        "description": "Should fail",
        "category": "Testing",
        "tags": [],
    }

    resp = await client.post("/projects/", json=payload, headers=auth_headers(token))
    assert resp.status_code == 403
