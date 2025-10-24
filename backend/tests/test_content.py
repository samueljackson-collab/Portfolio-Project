from __future__ import annotations

from fastapi.testclient import TestClient


def authenticate(client: TestClient) -> dict[str, str]:
    payload = {"email": "writer@example.com", "password": "password123"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/login", json=payload)
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def test_create_and_list_content(client: TestClient) -> None:
    headers = authenticate(client)
    create_resp = client.post(
        "/content/",
        json={"title": "My Article", "body": "Hello", "is_published": True},
        headers=headers,
    )
    assert create_resp.status_code == 201

    list_resp = client.get("/content/", headers=headers)
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert items[0]["title"] == "My Article"


def test_update_and_delete_content(client: TestClient) -> None:
    headers = authenticate(client)
    created = client.post(
        "/content/",
        json={"title": "Draft", "body": "text"},
        headers=headers,
    ).json()

    updated = client.put(
        f"/content/{created['id']}",
        json={"title": "Updated"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated"

    deleted = client.delete(f"/content/{created['id']}", headers=headers)
    assert deleted.status_code == 204
    remaining = client.get("/content/", headers=headers)
    assert remaining.json() == []
