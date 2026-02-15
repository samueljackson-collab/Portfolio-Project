import pytest


async def authenticate(client) -> str:
    await client.post(
        "/api/auth/register",
        json={"email": "content@example.com", "password": "supersecret"},
    )
    response = await client.post(
        "/api/auth/login",
        data={"username": "content@example.com", "password": "supersecret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_content_crud_flow(client):
    token = await authenticate(client)
    headers = {"Authorization": f"Bearer {token}"}

    create_response = await client.post(
        "/api/content/",
        json={"title": "First", "body": "Hello"},
        headers=headers,
    )
    assert create_response.status_code == 201
    created = create_response.json()

    list_response = await client.get("/api/content/", headers=headers)
    assert list_response.status_code == 200
    items = list_response.json()
    assert len(items) == 1

    content_id = created["id"]
    detail_response = await client.get(f"/api/content/{content_id}", headers=headers)
    assert detail_response.status_code == 200

    update_response = await client.put(
        f"/api/content/{content_id}",
        json={"body": "Updated"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["body"] == "Updated"

    delete_response = await client.delete(f"/api/content/{content_id}", headers=headers)
    assert delete_response.status_code == 204

    missing_response = await client.get(f"/api/content/{content_id}", headers=headers)
    assert missing_response.status_code == 404
