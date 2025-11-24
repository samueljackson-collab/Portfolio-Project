import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_deployment(authenticated_client: AsyncClient):
    payload = {
        "service_name": "portfolio-api",
        "region": "us-east-1",
        "cluster": "use1-portfolio",
        "version": "2025.11.15",
        "status": "Healthy",
        "git_commit": "abcd1234",
        "desired_replicas": 3,
        "available_replicas": 3,
    }

    create_response = await authenticated_client.post("/deployments", json=payload)
    assert create_response.status_code == 201
    body = create_response.json()
    assert body["service_name"] == payload["service_name"]
    assert body["available_replicas"] == payload["available_replicas"]

    list_response = await authenticated_client.get("/deployments")
    assert list_response.status_code == 200
    deployments = list_response.json()
    assert len(deployments) == 1
    assert deployments[0]["region"] == payload["region"]


@pytest.mark.asyncio
async def test_dashboard_rollup(authenticated_client: AsyncClient):
    first = {
        "service_name": "portfolio-api",
        "region": "us-east-1",
        "cluster": "use1-portfolio",
        "version": "2025.11.15",
        "status": "Healthy",
        "desired_replicas": 3,
        "available_replicas": 3,
    }
    second = {**first, "region": "eu-west-1", "cluster": "euw1-portfolio", "available_replicas": 2}

    for payload in (first, second):
        resp = await authenticated_client.post("/deployments", json=payload)
        assert resp.status_code == 201

    dashboard = await authenticated_client.get("/deployments/dashboard")
    assert dashboard.status_code == 200
    data = dashboard.json()
    assert {entry["region"] for entry in data["regions"]} == {"us-east-1", "eu-west-1"}
    assert len(data["latest_releases"]) == 2
