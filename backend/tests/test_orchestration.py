import pytest


@pytest.mark.asyncio
async def test_list_plans(authenticated_client):
    response = await authenticated_client.get("/orchestration/plans")
    assert response.status_code == 200

    plans = response.json()
    assert isinstance(plans, list)
    assert any(plan["environment"] == "dev" for plan in plans)


@pytest.mark.asyncio
async def test_start_run(authenticated_client):
    plans_response = await authenticated_client.get("/orchestration/plans")
    plan_id = plans_response.json()[0]["id"]

    run_response = await authenticated_client.post(
        "/orchestration/runs",
        json={"plan_id": plan_id, "parameters": {"change_ticket": "CHG-12345"}},
    )

    assert run_response.status_code == 201

    run_data = run_response.json()
    assert run_data["plan_id"] == plan_id
    assert run_data["status"] == "succeeded"
    assert run_data["artifacts"]["runbook"].endswith("orchestration-runbook.md")

    detail_response = await authenticated_client.get(f"/orchestration/runs/{run_data['id']}")
    assert detail_response.status_code == 200
    assert len(detail_response.json()["logs"]) >= 1
