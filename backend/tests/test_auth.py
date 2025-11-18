import pytest


@pytest.mark.asyncio
async def test_register_and_login(client):
    payload = {"email": "test@example.com", "username": "tester", "password": "password123"}
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == payload["email"]

    login_resp = await client.post(
        "/auth/login", data={"username": payload["username"], "password": payload["password"]}
    )
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()


@pytest.mark.asyncio
async def test_invalid_login(client):
    resp = await client.post("/auth/login", data={"username": "missing", "password": "bad"})
    assert resp.status_code == 401
