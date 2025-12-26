import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db, Base


def override_get_db():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    test_url = f"sqlite:///{path}"
    engine = create_engine(test_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        os.remove(path)


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in {"ok", "error"}


def test_auth_and_target_flow():
    register = client.post(
        "/auth/register", json={"username": "analyst", "password": "password123", "role": "admin"}
    )
    assert register.status_code == 200

    token_resp = client.post(
        "/auth/login",
        data={"username": "analyst", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert token_resp.status_code == 200
    token = token_resp.json()["access_token"]

    target_resp = client.post(
        "/targets",
        json={"name": "API", "description": "Test", "url": "https://example.com", "environment": "dev"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert target_resp.status_code == 200
    target_id = target_resp.json()["id"]

    finding_resp = client.post(
        "/findings",
        json={"title": "SQLi", "description": "Possible injection", "severity": "high", "target_id": target_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert finding_resp.status_code == 200

    scan_resp = client.post(
        "/scan", json={"target_id": target_id}, headers={"Authorization": f"Bearer {token}"}
    )
    assert scan_resp.status_code == 200
    assert scan_resp.json()["findings"]
