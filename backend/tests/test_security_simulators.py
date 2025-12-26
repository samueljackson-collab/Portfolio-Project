"""Tests for the security simulation suites (projects 5-10)."""

import pytest


@pytest.mark.asyncio
async def test_red_team_simulation_updates_streak(authenticated_client):
    create_response = await authenticated_client.post(
        "/red-team/operations",
        json={"name": "APT90", "objective": "Exfiltrate data", "stealth_factor": 1},
    )
    assert create_response.status_code == 201
    operation_id = create_response.json()["id"]

    simulate = await authenticated_client.post(
        f"/red-team/operations/{operation_id}/simulate-next-day",
        params={"seed": 1},
    )
    assert simulate.status_code == 200
    assert simulate.json()["day"] == 1

    operations = await authenticated_client.get("/red-team/operations")
    streak = operations.json()[0]["undetected_streak"]
    assert streak >= 0

    # Add a detected event and ensure timeline filtering works
    add_event = await authenticated_client.post(
        f"/red-team/operations/{operation_id}/events",
        json={
            "description": "Noisy port scan",
            "category": "Recon",
            "detected": True,
            "detection_confidence": 0.9,
        },
    )
    assert add_event.status_code == 200

    detected_timeline = await authenticated_client.get(
        f"/red-team/operations/{operation_id}/timeline",
        params={"detected": True},
    )
    assert detected_timeline.status_code == 200
    assert len(detected_timeline.json()) == 1


@pytest.mark.asyncio
async def test_ransomware_simulation_sequence(authenticated_client):
    create_response = await authenticated_client.post(
        "/incidents", json={"name": "Ransomware-1", "severity": "critical"}
    )
    assert create_response.status_code == 201
    incident_id = create_response.json()["id"]

    simulate = await authenticated_client.post(f"/incidents/{incident_id}/simulate")
    assert simulate.status_code == 200
    events = simulate.json()["events"]
    assert len(events) >= 5
    assert [event["sequence"] for event in events] == sorted(event["sequence"] for event in events)


@pytest.mark.asyncio
async def test_malware_analysis_sets_status(authenticated_client):
    sample_resp = await authenticated_client.post(
        "/malware/samples",
        json={"name": "locker", "file_hash": "abc123def456", "sample_type": "elf"},
    )
    assert sample_resp.status_code == 201
    sample_id = sample_resp.json()["id"]

    analyze_resp = await authenticated_client.post(f"/malware/samples/{sample_id}/analyze")
    assert analyze_resp.status_code == 200
    body = analyze_resp.json()
    assert body["sample"]["status"] == "analyzed"
    assert "yara_rule" in body["report"]


@pytest.mark.asyncio
async def test_threat_hunting_promotion_creates_rule(authenticated_client):
    hypothesis = await authenticated_client.post(
        "/threat-hunting/hypotheses",
        json={"title": "Suspicious PowerShell", "description": "Investigate remote sessions"},
    )
    hypothesis_id = hypothesis.json()["id"]
    finding = await authenticated_client.post(
        f"/threat-hunting/hypotheses/{hypothesis_id}/findings",
        json={"severity": "high", "details": "Encoded command seen"},
    )
    finding_id = finding.json()["id"]

    promoted = await authenticated_client.post(f"/threat-hunting/findings/{finding_id}/promote")
    assert promoted.status_code == 200
    assert promoted.json()["source_finding_id"] == finding_id


@pytest.mark.asyncio
async def test_edr_outdated_agent_alert(authenticated_client):
    endpoint_resp = await authenticated_client.post(
        "/edr/endpoints",
        json={
            "hostname": "host-1",
            "operating_system": "linux",
            "agent_version": "1.0.0",
        },
    )
    assert endpoint_resp.status_code == 201

    alerts_resp = await authenticated_client.get("/edr/alerts")
    assert alerts_resp.status_code == 200
    assert len(alerts_resp.json()) >= 1


@pytest.mark.asyncio
async def test_soc_fake_alert_generation(authenticated_client):
    generated = await authenticated_client.post("/soc/alerts/generate")
    assert generated.status_code == 200
    alerts = generated.json()
    assert len(alerts) == 3
    severities = {alert["severity"] for alert in alerts}
    assert "high" in severities
