"""Tests for the /health endpoint."""
import pytest


@pytest.mark.asyncio
async def test_health_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert data["db"] == "connected"


@pytest.mark.asyncio
async def test_health_has_no_auth_requirement(client):
    """Health endpoint must be reachable without an API key."""
    response = await client.get("/health", headers={})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_security_headers(client):
    response = await client.get("/health")
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
    assert response.headers.get("referrer-policy") == "strict-origin-when-cross-origin"
