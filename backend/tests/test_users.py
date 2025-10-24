"""Tests for user-related endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient


def test_create_user_success(client: TestClient) -> None:
    """Creating a user should return the new user without the password."""
    payload = {"username": "alice", "password": "supersecret", "email": "alice@example.com"}
    response = client.post("/users/", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "alice"
    assert body["email"] == "alice@example.com"
    assert "password" not in body


def test_duplicate_user_returns_bad_request(client: TestClient) -> None:
    """Creating a user with an existing username should fail."""
    payload = {"username": "alice", "password": "supersecret", "email": "alice@example.com"}
    first = client.post("/users/", json=payload)
    assert first.status_code == 201

    second = client.post("/users/", json=payload)
    assert second.status_code == 400
    assert second.json()["detail"] == "Username or email already exists"
