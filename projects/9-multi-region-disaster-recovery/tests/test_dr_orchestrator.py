"""Tests for the Multi-Region Disaster Recovery orchestrator."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from src.main import DROrchestrator, DRStatus, FailoverEvent, RegionStatus


@pytest.fixture
def orchestrator() -> DROrchestrator:
    return DROrchestrator(
        primary_region="us-east-1",
        secondary_region="us-west-2",
        rto_target_seconds=300.0,
        rpo_target_minutes=5.0,
    )


# ---------------------------------------------------------------------------
# RegionStatus
# ---------------------------------------------------------------------------

def test_region_status_availability_full():
    rs = RegionStatus(
        region="us-east-1",
        status=DRStatus.HEALTHY,
        latency_ms=10.0,
        healthy_services=5,
        total_services=5,
    )
    assert rs.availability == 100.0


def test_region_status_availability_partial():
    rs = RegionStatus(
        region="us-east-1",
        status=DRStatus.DEGRADED,
        latency_ms=10.0,
        healthy_services=3,
        total_services=5,
    )
    assert rs.availability == 60.0


def test_region_status_availability_zero_services():
    rs = RegionStatus(
        region="us-east-1",
        status=DRStatus.FAILOVER,
        latency_ms=0.0,
        healthy_services=0,
        total_services=0,
    )
    assert rs.availability == 0.0


# ---------------------------------------------------------------------------
# DRStatus enum
# ---------------------------------------------------------------------------

def test_dr_status_values():
    assert DRStatus.HEALTHY == "healthy"
    assert DRStatus.DEGRADED == "degraded"
    assert DRStatus.FAILOVER == "failover"
    assert DRStatus.RECOVERING == "recovering"


# ---------------------------------------------------------------------------
# check_region_readiness
# ---------------------------------------------------------------------------

def test_check_region_readiness_returns_status(orchestrator: DROrchestrator):
    status = orchestrator.check_region_readiness("us-east-1")
    assert isinstance(status, RegionStatus)
    assert status.region == "us-east-1"
    assert status.total_services > 0
    assert status.last_checked


def test_check_region_readiness_latency_primary_lower(orchestrator: DROrchestrator):
    primary = orchestrator.check_region_readiness("us-east-1")
    secondary = orchestrator.check_region_readiness("us-west-2")
    assert primary.latency_ms < secondary.latency_ms


def test_check_region_readiness_custom_services(orchestrator: DROrchestrator):
    status = orchestrator.check_region_readiness("us-east-1", services=["rds", "ec2"])
    assert status.total_services == 2


# ---------------------------------------------------------------------------
# execute_failover
# ---------------------------------------------------------------------------

def test_execute_failover_returns_event(orchestrator: DROrchestrator):
    event = orchestrator.execute_failover(trigger="test")
    assert isinstance(event, FailoverEvent)
    assert event.event_id.startswith("dr-")
    assert event.trigger == "test"


def test_execute_failover_has_steps(orchestrator: DROrchestrator):
    event = orchestrator.execute_failover()
    assert len(event.steps) > 0
    for step in event.steps:
        assert "step" in step
        assert "passed" in step


def test_execute_failover_records_rto(orchestrator: DROrchestrator):
    event = orchestrator.execute_failover()
    assert event.rto_seconds >= 0.0


def test_execute_failover_success(orchestrator: DROrchestrator):
    event = orchestrator.execute_failover()
    assert event.success is True
    assert event.completed_at


def test_execute_failover_appended_to_log(orchestrator: DROrchestrator):
    orchestrator.execute_failover()
    orchestrator.execute_failover()
    assert len(orchestrator._event_log) == 2


# ---------------------------------------------------------------------------
# generate_report
# ---------------------------------------------------------------------------

def test_generate_report_structure(orchestrator: DROrchestrator):
    report = orchestrator.generate_report()
    assert "generated_at" in report
    assert "configuration" in report
    assert "region_status" in report
    assert "failover_events" in report


def test_generate_report_includes_both_regions(orchestrator: DROrchestrator):
    report = orchestrator.generate_report()
    assert "us-east-1" in report["region_status"]
    assert "us-west-2" in report["region_status"]


def test_generate_report_includes_events(orchestrator: DROrchestrator):
    orchestrator.execute_failover(trigger="scheduled")
    report = orchestrator.generate_report()
    assert len(report["failover_events"]) == 1
    assert report["failover_events"][0]["trigger"] == "scheduled"


def test_generate_report_writes_file(orchestrator: DROrchestrator, tmp_path: Path):
    output = tmp_path / "reports" / "dr-report.json"
    orchestrator.generate_report(output_path=output)
    assert output.exists()
    data = json.loads(output.read_text())
    assert "configuration" in data


def test_generate_report_rto_config(orchestrator: DROrchestrator):
    report = orchestrator.generate_report()
    assert report["configuration"]["rto_target_seconds"] == 300.0
    assert report["configuration"]["rpo_target_minutes"] == 5.0
