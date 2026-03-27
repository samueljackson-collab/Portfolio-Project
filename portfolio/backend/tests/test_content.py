import pytest
from httpx import AsyncClient


async def _auth_headers(client: AsyncClient) -> dict[str, str]:
    register_payload = {"email": "content@example.com", "password": "contentpass123"}
    await client.post("/api/auth/register", json=register_payload)
    login_response = await client.post(
        "/api/auth/login",
        data={"username": register_payload["email"], "password": register_payload["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_content_crud_flow(client: AsyncClient) -> None:
    headers = await _auth_headers(client)

    create_payload = {"title": "First", "slug": "first", "body": "hello"}
    create_resp = await client.post("/api/content", json=create_payload, headers=headers)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["title"] == "First"

    list_resp = await client.get("/api/content", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    content_id = created["id"]
    update_resp = await client.put(
        f"/api/content/{content_id}",
        json={"title": "Updated"},
        headers=headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Updated"

    delete_resp = await client.delete(f"/api/content/{content_id}", headers=headers)
    assert delete_resp.status_code == 204

    final_list = await client.get("/api/content", headers=headers)
    assert final_list.status_code == 200
    assert final_list.json() == []
