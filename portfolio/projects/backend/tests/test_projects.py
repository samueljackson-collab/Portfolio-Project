from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_list_projects_returns_seed_data() -> None:
    response = client.get("/api/projects")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload, "Expected at least one project in the seed data"
    project = payload[0]
    assert {"id", "name", "description", "tags", "url"}.issubset(project)
