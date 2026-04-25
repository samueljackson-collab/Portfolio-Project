"""Tests for the scan CRUD API endpoints."""
from __future__ import annotations
import pytest
from tests.conftest import ANDROID_VULNERABLE, WEB_VULNERABLE


# ── Create scan ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_scan_returns_201(client):
    payload = {
        "platform": "android",
        "filename": "UserDao.java",
        "code_content": ANDROID_VULNERABLE,
    }
    response = await client.post("/api/scans", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["platform"] == "android"
    assert data["filename"] == "UserDao.java"
    assert data["status"] in ("pending", "running", "complete")
    assert "id" in data


@pytest.mark.asyncio
async def test_create_scan_invalid_platform(client):
    payload = {"platform": "cobol", "filename": "test.cbl", "code_content": "DISPLAY 'HELLO'"}
    response = await client.post("/api/scans", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_scan_empty_code(client):
    payload = {"platform": "web", "filename": "app.js", "code_content": "   "}
    response = await client.post("/api/scans", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_scan_oversized_code(client):
    big_code = "x" * (1024 * 1024 + 1)  # 1 MB + 1 byte
    payload = {"platform": "web", "filename": "big.js", "code_content": big_code}
    response = await client.post("/api/scans", json=payload)
    assert response.status_code == 413


# ── List scans ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_scans_empty(client):
    response = await client.get("/api/scans")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_scans_after_create(client):
    payload = {"platform": "web", "filename": "app.js", "code_content": WEB_VULNERABLE}
    create_resp = await client.post("/api/scans", json=payload)
    assert create_resp.status_code == 201, create_resp.text

    response = await client.get("/api/scans")
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_list_scans_platform_filter(client):
    await client.post("/api/scans", json={
        "platform": "android", "filename": "a.java", "code_content": ANDROID_VULNERABLE
    })
    await client.post("/api/scans", json={
        "platform": "web", "filename": "b.js", "code_content": WEB_VULNERABLE
    })

    resp_android = await client.get("/api/scans", params={"platform": "android"})
    assert resp_android.status_code == 200
    assert all(s["platform"] == "android" for s in resp_android.json())

    resp_web = await client.get("/api/scans", params={"platform": "web"})
    assert resp_web.status_code == 200
    assert all(s["platform"] == "web" for s in resp_web.json())


# ── Get scan by ID ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_scan_not_found(client):
    response = await client.get("/api/scans/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_scan_by_id(client):
    create_resp = await client.post("/api/scans", json={
        "platform": "web", "filename": "app.js", "code_content": WEB_VULNERABLE
    })
    assert create_resp.status_code == 201, create_resp.text
    scan_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/scans/{scan_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == scan_id


# ── API key auth ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_api_key_rejected_when_set(client, monkeypatch):
    import config as cfg
    monkeypatch.setattr(cfg, "API_KEY", "secret-test-key")

    response = await client.post("/api/scans", json={
        "platform": "web", "filename": "a.js", "code_content": "console.log('hi')"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_api_key_accepted_when_correct(client, monkeypatch):
    import config as cfg
    monkeypatch.setattr(cfg, "API_KEY", "secret-test-key")

    response = await client.post(
        "/api/scans",
        json={"platform": "web", "filename": "a.js", "code_content": "console.log('hi')"},
        headers={"X-API-Key": "secret-test-key"},
    )
    assert response.status_code == 201, response.text
