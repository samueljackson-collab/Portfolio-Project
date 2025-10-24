from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_user_content_flow(async_client: AsyncClient):
    register = await async_client.post("/auth/register", json={"email": "flow@example.com", "password": "secret"})
    assert register.status_code == 201

    login = await async_client.post("/auth/login", json={"email": "flow@example.com", "password": "secret"})
    tokens = login.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    create = await async_client.post(
        "/content/",
        json={"title": "Integration", "body": "Body"},
        headers=headers,
    )
    assert create.status_code == 201
    content_id = create.json()["id"]

    listing = await async_client.get("/content/", headers=headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1

    delete = await async_client.delete(f"/content/{content_id}", headers=headers)
    assert delete.status_code == 204
