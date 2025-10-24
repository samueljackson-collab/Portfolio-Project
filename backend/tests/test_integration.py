from __future__ import annotations

from fastapi.testclient import TestClient


def test_user_journey(client: TestClient) -> None:
    register_payload = {"email": "journey@example.com", "password": "password123"}
    assert client.post("/auth/register", json=register_payload).status_code == 201

    login = client.post("/auth/login", json=register_payload).json()
    headers = {"Authorization": f"Bearer {login['access_token']}"}

    created = client.post("/content/", json={"title": "Journey", "body": "story"}, headers=headers)
    assert created.status_code == 201
    content_id = created.json()["id"]

    items = client.get("/content/", headers=headers).json()
    assert any(item["id"] == content_id for item in items)
