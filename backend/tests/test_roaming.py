"""Tests for roaming simulation endpoints."""

from httpx import AsyncClient, ASGITransport
import pytest
import pytest_asyncio

from app.main import app


@pytest_asyncio.fixture
async def roaming_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_initiate_roaming_session(roaming_client):
    payload = {
        "imsi": "310410123456789",
        "home_network": "310-410",
        "visited_network": "208-01",
        "roaming_enabled": True,
    }
    response = await roaming_client.post("/roaming/sessions", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["state"] == "authenticating"
    assert body["visited_network"] == "208-01"


@pytest.mark.asyncio
async def test_reject_roaming_without_agreement(roaming_client):
    payload = {
        "imsi": "310410123456789",
        "home_network": "310-410",
        "visited_network": "999-99",
        "roaming_enabled": True,
    }
    response = await roaming_client.post("/roaming/sessions", json=payload)
    assert response.status_code == 400
    assert "agreement" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_roaming_event_transitions(roaming_client):
    payload = {
        "imsi": "310410123456789",
        "home_network": "310-410",
        "visited_network": "208-01",
        "roaming_enabled": True,
    }
    session = await roaming_client.post("/roaming/sessions", json=payload)
    session_id = session.json()["session_id"]

    for event_type in ["location_update", "activate_roaming", "detach"]:
        response = await roaming_client.post(
            f"/roaming/sessions/{session_id}/events",
            json={"type": event_type, "message": f"{event_type} completed"},
        )
        assert response.status_code == 200

    final_state = response.json()["state"]
    assert final_state == "detached"
    history = response.json()["events"]
    assert any(e["type"] == "activate_roaming" for e in history)

