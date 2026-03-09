"""Test web application."""

import pytest


def test_health_endpoint():
    """Test health endpoint structure."""
    response = {"status": "healthy", "hostname": "test"}
    assert "status" in response
    assert response["status"] == "healthy"


def test_ready_endpoint():
    """Test ready endpoint structure."""
    response = {"status": "ready", "hostname": "test"}
    assert "status" in response
    assert response["status"] == "ready"
