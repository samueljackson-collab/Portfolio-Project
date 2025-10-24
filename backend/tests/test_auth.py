from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app import auth


def test_register_and_login(client: TestClient) -> None:
    payload = {"email": "user@example.com", "password": "password123"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    user_id = response.json()["id"]

    login = client.post("/auth/login", json=payload)
    assert login.status_code == 200
    data = login.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    refreshed = client.post("/auth/refresh", json=data)
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"] != data["access_token"]


def test_hash_and_verify_password() -> None:
    hashed = auth.hash_password("secret")
    assert auth.verify_password("secret", hashed)
    assert not auth.verify_password("wrong", hashed)
