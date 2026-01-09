"""API endpoint tests."""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_check():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness_check():
    """Test readiness endpoint."""
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_create_item():
    """Test creating an item."""
    response = client.post(
        "/api/items",
        json={"name": "Test Item", "description": "Test Description", "price": 19.99},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["price"] == 19.99
    assert "id" in data


def test_list_items():
    """Test listing items."""
    response = client.get("/api/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_item():
    """Test getting a specific item."""
    # Create item first
    create_response = client.post(
        "/api/items", json={"name": "Get Test", "description": "Desc", "price": 9.99}
    )
    item_id = create_response.json()["id"]

    # Get the item
    response = client.get(f"/api/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Get Test"


def test_get_nonexistent_item():
    """Test getting a nonexistent item returns 404."""
    response = client.get("/api/items/99999")
    assert response.status_code == 404


def test_update_item():
    """Test updating an item."""
    # Create item first
    create_response = client.post(
        "/api/items", json={"name": "Original", "description": "Desc", "price": 9.99}
    )
    item_id = create_response.json()["id"]

    # Update the item
    response = client.put(
        f"/api/items/{item_id}",
        json={"name": "Updated", "description": "New Desc", "price": 14.99},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated"
    assert response.json()["price"] == 14.99


def test_delete_item():
    """Test deleting an item."""
    # Create item first
    create_response = client.post(
        "/api/items", json={"name": "To Delete", "description": "Desc", "price": 9.99}
    )
    item_id = create_response.json()["id"]

    # Delete the item
    response = client.delete(f"/api/items/{item_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"/api/items/{item_id}")
    assert get_response.status_code == 404
