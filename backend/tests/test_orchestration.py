import pytest
from datetime import datetime, timezone
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.main import app
from app.routers.orchestration import DeploymentStatus, _baseline_plan


@pytest.fixture
async def orchestration_client():
    async def noop_db():
        yield None

    app.dependency_overrides[get_db] = noop_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_list_environments(orchestration_client):
    response = await orchestration_client.get("/orchestration/environments")
    assert response.status_code == 200
    payload = response.json()
    assert any(env["environment"] == "staging" for env in payload)
    assert any(env["plan"]["terraform_plan"].endswith("staging") for env in payload)


@pytest.mark.asyncio
async def test_trigger_deploy_updates_state(orchestration_client):
    response = await orchestration_client.post(
        "/orchestration/deploy",
        json={"environment": "staging", "artifact_version": "build-123", "dry_run": True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["artifact_version"] == "build-123"
    assert payload["status"] == "planned"


@pytest.mark.asyncio
async def test_unknown_environment_returns_404(orchestration_client):
    response = await orchestration_client.post(
        "/orchestration/deploy",
        json={"environment": "qa", "artifact_version": "v1"},
    )
    assert response.status_code == 404


def test_deployment_status_notes_are_isolated():
    plan = _baseline_plan("staging")
    first = DeploymentStatus(
        environment="staging",
        status="planned",
        last_deploy=datetime.now(timezone.utc),
        artifact_version="a",
        plan=plan,
    )
    first.notes.append("first note")

    second = DeploymentStatus(
        environment="staging",
        status="planned",
        last_deploy=datetime.now(timezone.utc),
        artifact_version="b",
        plan=plan,
    )

    assert "first note" not in second.notes
