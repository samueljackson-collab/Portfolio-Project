"""
Tests for health check endpoints.

This module tests:
- Basic health check endpoint
- Liveness probe endpoint
- Readiness probe endpoint
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test basic health check endpoint."""
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
    assert data["service"] == "Portfolio API"


@pytest.mark.asyncio
async def test_liveness_probe(client: AsyncClient):
    """Test Kubernetes liveness probe endpoint."""
    response = await client.get("/health/liveness")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_readiness_probe(client: AsyncClient):
    """Test Kubernetes readiness probe endpoint."""
    response = await client.get("/health/readiness")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "database" in data
    assert data["database"] == "connected"
