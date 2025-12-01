"""Roaming endpoint contract tests."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_roaming_flow(client: AsyncClient):
    create_resp = await client.post(
        "/roaming/sessions",
        json={
            "imsi": "310410999999999",
            "home_network": "310-410",
            "visited_network": "208-01",
        },
    )
    assert create_resp.status_code == 201
    session_id = create_resp.json()["session_id"]

    auth_resp = await client.post(f"/roaming/sessions/{session_id}/authenticate")
    assert auth_resp.status_code == 200
    assert auth_resp.json()["state"] == "authenticated"

    activate_resp = await client.post(f"/roaming/sessions/{session_id}/activate")
    assert activate_resp.status_code == 200
    assert activate_resp.json()["state"] == "active"

    list_resp = await client.get("/roaming/sessions")
    assert list_resp.status_code == 200
    payload = list_resp.json()
    assert payload["total"] == 1
    assert payload["sessions"][0]["state"] == "active"


@pytest.mark.asyncio
async def test_roaming_denied_without_agreement(client: AsyncClient):
    create_resp = await client.post(
        "/roaming/sessions",
        json={
            "imsi": "310410123456789",
            "home_network": "310-410",
            "visited_network": "999-99",
        },
    )
    session_id = create_resp.json()["session_id"]

    auth_resp = await client.post(f"/roaming/sessions/{session_id}/authenticate")
    assert auth_resp.status_code == 403
    assert "No roaming agreement" in auth_resp.json()["detail"]

    list_resp = await client.get("/roaming/sessions")
    assert list_resp.status_code == 200
    assert list_resp.json()["sessions"][0]["state"] == "detached"
