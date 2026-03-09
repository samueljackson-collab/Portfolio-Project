from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def get_token() -> str:
    response = client.post("/login", json={"username": "admin", "password": "password"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_page_and_finding_flow():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    endpoint_resp = client.post(
        "/endpoints",
        headers=headers,
        json={"name": "App", "path": "/app", "description": "Main app"},
    )
    assert endpoint_resp.status_code == 201
    endpoint_id = endpoint_resp.json()["id"]

    scan_resp = client.post(
        "/scan-page",
        headers=headers,
        json={"endpoint_id": endpoint_id, "url": "http://example.com/app?id=1"},
    )
    assert scan_resp.status_code == 200
    body = scan_resp.json()

    assert body["page"]["endpoint_id"] == endpoint_id
    assert body["findings"]
    assert all(finding["page_id"] == body["page"]["id"] for finding in body["findings"])


def test_create_page_validation():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/pages",
        headers=headers,
        json={"endpoint_id": 999, "url": "https://example.com"},
    )
    assert response.status_code == 404
