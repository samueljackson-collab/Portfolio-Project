import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_complete_user_workflow(client: AsyncClient):
    # 1. Register
    r = await client.post("/api/auth/register", json={"email": "workflow@example.com", "password": "workflowpass123"})
    assert r.status_code == 201
    user_id = r.json()["id"]

    # 2. Login
    r = await client.post("/api/auth/login", data={"username": "workflow@example.com", "password": "workflowpass123"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create
    r = await client.post("/api/content/", json={"title": "Integration Test", "body": "Full workflow test"}, headers=headers)
    assert r.status_code == 201
    cid = r.json()["id"]

    # 4. Read
    r = await client.get(f"/api/content/{cid}", headers=headers)
    assert r.status_code == 200
    assert r.json()["title"] == "Integration Test"

    # 5. Update
    r = await client.put(f"/api/content/{cid}", json={"title": "Updated Title"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["title"] == "Updated Title"

    # 6. Delete
    r = await client.delete(f"/api/content/{cid}", headers=headers)
    assert r.status_code == 204
