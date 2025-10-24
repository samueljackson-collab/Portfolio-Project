"""Health endpoint tests."""

from __future__ import annotations

import pytest


@pytest.mark.health
async def test_health_check_returns_service_status(client) -> None:
    """The primary health endpoint should report service status and version."""
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert "version" in body
    assert "database" in body


@pytest.mark.health
async def test_liveness_endpoint_returns_alive(client) -> None:
    """Liveness probe should always return an alive status."""
    response = await client.get("/health/liveness")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


@pytest.mark.health
async def test_readiness_endpoint_returns_ready(client) -> None:
    """Readiness endpoint should indicate readiness when database calls succeed."""
    response = await client.get("/health/readiness")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
