"""Tests for item-related endpoints."""
from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient


def _auth_headers(client: TestClient) -> dict[str, str]:
    """Register a throwaway user and return authorization headers."""
    username = f"user-{uuid4().hex[:6]}"
    payload = {
        "username": username,
        "password": "supersecret",
        "email": f"{username}@example.com",
    }
    client.post("/users/", json=payload)
    token_response = client.post(
        "/auth/token",
        data={"username": username, "password": "supersecret"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    token_response.raise_for_status()
    token = token_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_and_list_items(client: TestClient) -> None:
    """Authenticated users should be able to create and fetch their items."""
    headers = _auth_headers(client)

    create_response = client.post(
        "/items/",
        json={"title": "First item", "description": "Documented in tests"},
        headers=headers,
    )
    assert create_response.status_code == 201

    list_response = client.get("/items/", headers=headers)
    assert list_response.status_code == 200
    items = list_response.json()
    assert len(items) == 1
    assert items[0]["title"] == "First item"


def test_get_item_requires_ownership(client: TestClient) -> None:
    """Users should not see items that do not belong to them."""
    owner_headers = _auth_headers(client)
    other_headers = _auth_headers(client)

    create_response = client.post(
        "/items/",
        json={"title": "Secret", "description": "Only owner can see"},
        headers=owner_headers,
    )
    item_id = create_response.json()["id"]

    missing_response = client.get(f"/items/{item_id}", headers=other_headers)
    assert missing_response.status_code == 404
