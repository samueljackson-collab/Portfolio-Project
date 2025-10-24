from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.auth import create_access_token

@pytest.mark.asyncio
async def test_register_and_login(async_client: AsyncClient):
    response = await async_client.post("/auth/register", json={"email": "test@example.com", "password": "secret"})
    assert response.status_code == 201
    token_response = await async_client.post("/auth/login", json={"email": "test@example.com", "password": "secret"})
    assert token_response.status_code == 200
    data = token_response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_duplicate_registration_fails(async_client: AsyncClient):
    payload = {"email": "dup@example.com", "password": "secret"}
    await async_client.post("/auth/register", json=payload)
    response = await async_client.post("/auth/register", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client: AsyncClient):
    response = await async_client.post("/auth/login", json={"email": "nobody@example.com", "password": "bad"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_token_payload_is_rejected(async_client: AsyncClient):
    token = create_access_token("not-a-uuid")
    response = await async_client.get("/content/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
