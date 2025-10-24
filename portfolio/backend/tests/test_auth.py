import pytest


@pytest.mark.asyncio
async def test_register_and_login(client):
    register_payload = {"email": "user@example.com", "password": "strongpass123"}
    response = await client.post("/api/auth/register", json=register_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == register_payload["email"]

    login_response = await client.post(
        "/api/auth/login",
        data={"username": register_payload["email"], "password": register_payload["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token
