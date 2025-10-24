from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _auth_headers(client: AsyncClient) -> dict[str, str]:
    await client.post("/auth/register", json={"email": "content@example.com", "password": "secret"})
    token_response = await client.post("/auth/login", json={"email": "content@example.com", "password": "secret"})
    token = token_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_and_list_content(async_client: AsyncClient):
    headers = await _auth_headers(async_client)
    create_response = await async_client.post(
        "/content/",
        json={"title": "First", "body": "Hello", "is_published": True},
        headers=headers,
    )
    assert create_response.status_code == 201
    list_response = await async_client.get("/content/", headers=headers)
    assert list_response.status_code == 200
    items = list_response.json()
    assert len(items) == 1
    assert items[0]["title"] == "First"


@pytest.mark.asyncio
async def test_update_content(async_client: AsyncClient):
    headers = await _auth_headers(async_client)
    create_response = await async_client.post(
        "/content/",
        json={"title": "First", "body": "Hello", "is_published": False},
        headers=headers,
    )
    content_id = create_response.json()["id"]
    update_response = await async_client.put(
        f"/content/{content_id}",
        json={"title": "Updated", "is_published": True},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated"


@pytest.mark.asyncio
async def test_delete_content(async_client: AsyncClient):
    headers = await _auth_headers(async_client)
    create_response = await async_client.post(
        "/content/",
        json={"title": "To Delete", "body": "Delete me"},
        headers=headers,
    )
    content_id = create_response.json()["id"]
    delete_response = await async_client.delete(f"/content/{content_id}", headers=headers)
    assert delete_response.status_code == 204
    list_response = await async_client.get("/content/", headers=headers)
    assert list_response.json() == []
