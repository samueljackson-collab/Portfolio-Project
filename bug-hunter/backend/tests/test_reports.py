"""Tests for the reports API and report generation service."""
from __future__ import annotations
import asyncio
import pytest
from tests.conftest import WEB_VULNERABLE, ANDROID_VULNERABLE


async def _wait_for_scan(client, scan_id: str, max_seconds: int = 15) -> dict:
    """Poll until a scan reaches terminal status."""
    for _ in range(max_seconds * 2):
        resp = await client.get(f"/api/scans/{scan_id}")
        assert resp.status_code == 200
        data = resp.json()
        if data["status"] in ("complete", "failed"):
            return data
        await asyncio.sleep(0.5)
    raise TimeoutError(f"Scan {scan_id} did not complete within {max_seconds}s")


async def _create_and_complete_scan(client, code: str = WEB_VULNERABLE, platform: str = "web") -> str:
    resp = await client.post("/api/scans", json={
        "platform": platform,
        "filename": "test.js",
        "code_content": code,
    })
    assert resp.status_code == 201, resp.text
    scan_id = resp.json()["id"]
    await _wait_for_scan(client, scan_id)
    return scan_id


# ── Report listing ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_reports_empty(client):
    resp = await client.get("/api/reports")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_reports_after_scan(client):
    await _create_and_complete_scan(client)
    resp = await client.get("/api/reports")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


# ── Report retrieval ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_report_not_found(client):
    resp = await client.get("/api/reports/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_report_by_id(client):
    scan_id = await _create_and_complete_scan(client)

    reports_resp = await client.get("/api/reports")
    assert reports_resp.status_code == 200
    reports = [r for r in reports_resp.json() if r["session_id"] == scan_id]
    assert reports, "Expected a report for the completed scan"

    report_id = reports[0]["id"]
    get_resp = await client.get(f"/api/reports/{report_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == report_id
    assert data["session_id"] == scan_id
    assert isinstance(data["html_content"], str)
    assert len(data["html_content"]) > 0
    assert "pending" not in data["id"]


@pytest.mark.asyncio
async def test_report_id_not_in_html_as_pending(client):
    """Verify the fragile 'pending' placeholder replacement was fully eliminated."""
    scan_id = await _create_and_complete_scan(client)

    reports_resp = await client.get("/api/reports")
    reports = [r for r in reports_resp.json() if r["session_id"] == scan_id]
    assert reports

    report_id = reports[0]["id"]
    get_resp = await client.get(f"/api/reports/{report_id}")
    html = get_resp.json()["html_content"]
    # The real report ID should appear in the rendered HTML
    assert report_id in html


@pytest.mark.asyncio
async def test_report_executive_summary_populated(client):
    scan_id = await _create_and_complete_scan(client, code=WEB_VULNERABLE)

    reports_resp = await client.get("/api/reports")
    reports = [r for r in reports_resp.json() if r["session_id"] == scan_id]
    assert reports
    summary = reports[0]["executive_summary"]
    assert len(summary) > 50


# ── HTML export ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_html_export(client):
    scan_id = await _create_and_complete_scan(client)
    reports_resp = await client.get("/api/reports")
    reports = [r for r in reports_resp.json() if r["session_id"] == scan_id]
    assert reports

    report_id = reports[0]["id"]
    html_resp = await client.get(f"/api/reports/{report_id}/html")
    assert html_resp.status_code == 200
    assert "text/html" in html_resp.headers["content-type"]
    cd = html_resp.headers.get("content-disposition", "")
    assert "attachment" in cd
    # Filename must not contain raw newlines (header injection guard)
    assert "\r" not in cd and "\n" not in cd


@pytest.mark.asyncio
async def test_html_export_not_found(client):
    resp = await client.get("/api/reports/nonexistent/html")
    assert resp.status_code == 404


# ── Input validation (new checks) ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_scans_invalid_platform_rejected(client):
    resp = await client.get("/api/scans", params={"platform": "cobol"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_scans_invalid_status_rejected(client):
    resp = await client.get("/api/scans", params={"status": "exploded"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_scans_negative_offset_rejected(client):
    resp = await client.get("/api/scans", params={"offset": -1})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_scan_filename_too_long(client):
    long_name = "a" * 256
    resp = await client.post("/api/scans", json={
        "platform": "web",
        "filename": long_name,
        "code_content": "console.log('hi')",
    })
    assert resp.status_code == 422


# ── Unicode code content ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_unicode_code_content(client):
    """Multi-byte unicode must not crash the scan pipeline."""
    unicode_code = "// 日本語コメント\nconst x = eval(req.body.cmd);\n// emoji 🔥"
    resp = await client.post("/api/scans", json={
        "platform": "web",
        "filename": "unicode.js",
        "code_content": unicode_code,
    })
    assert resp.status_code == 201, resp.text
    scan_id = resp.json()["id"]
    final = await _wait_for_scan(client, scan_id)
    assert final["status"] == "complete"


# ── Single commit / no duplicate commits ──────────────────────────────────────

@pytest.mark.asyncio
async def test_scan_completes_with_findings_in_single_pass(client):
    """Scan with multiple findings should still complete and produce a single report."""
    scan_id = await _create_and_complete_scan(client, code=ANDROID_VULNERABLE, platform="android")

    get_resp = await client.get(f"/api/scans/{scan_id}")
    assert get_resp.status_code == 200
    scan = get_resp.json()
    assert scan["status"] == "complete"
    total = scan["critical_count"] + scan["high_count"] + scan["medium_count"] + scan["low_count"]
    assert total > 0, "Expected at least one finding for vulnerable Android code"

    reports_resp = await client.get("/api/reports")
    reports = [r for r in reports_resp.json() if r["session_id"] == scan_id]
    assert len(reports) == 1, "Expected exactly one report per scan"
