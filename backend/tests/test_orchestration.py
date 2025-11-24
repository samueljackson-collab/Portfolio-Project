import pytest


@pytest.mark.asyncio
async def test_start_and_fetch_run(client):
    payload = {
        "name": "demo-deploy",
        "environment": "staging",
        "target_version": "v1.2.3",
        "kickoff_notes": "rolling out api and console",
    }

    create_response = await client.post("/orchestration/runs", json=payload)
    assert create_response.status_code == 201
    run = create_response.json()

    detail_response = await client.get(f"/orchestration/runs/{run['id']}")
    assert detail_response.status_code == 200
    fetched = detail_response.json()

    assert fetched["environment"] == "staging"
    assert fetched["target_version"] == "v1.2.3"
    assert len(fetched["steps"]) == 1


@pytest.mark.asyncio
async def test_summary_and_status_transitions(client):
    payload = {
        "name": "blue-green-deploy",
        "environment": "production",
        "target_version": "v2.0.0",
    }
    run = (await client.post("/orchestration/runs", json=payload)).json()

    summary = (await client.get("/orchestration/summary")).json()
    assert summary["running"] >= 1

    update = {
        "message": "health checks green",
        "status": "succeeded",
        "level": "info",
    }
    updated_run = (await client.post(f"/orchestration/runs/{run['id']}/events", json=update)).json()

    assert updated_run["status"] == "succeeded"
    assert any(step["message"] == "health checks green" for step in updated_run["steps"])
