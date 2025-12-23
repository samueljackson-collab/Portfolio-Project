import pytest


@pytest.mark.asyncio
async def test_register_and_login_flow(client):
    register_response = await client.post(
        "/api/auth/register",
        json={"email": "user@example.com", "password": "supersecret"},
    )
    assert register_response.status_code == 201
    data = register_response.json()
    assert data["email"] == "user@example.com"

    login_response = await client.post(
        "/api/auth/login",
        data={"username": "user@example.com", "password": "supersecret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token

    # Duplicate registration should fail
    duplicate_response = await client.post(
        "/api/auth/register",
        json={"email": "user@example.com", "password": "anotherpass"},
    )
    assert duplicate_response.status_code == 400
