"""Tests for the DevSecOps pipeline orchestrator."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from src.main import DevSecOpsPipeline, PipelineReport, ScanResult


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a minimal project structure in a temp directory."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("# main")
    (tmp_path / "pipelines").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "README.md").write_text("# Test Project")
    (tmp_path / "requirements.txt").write_text("pytest>=7.4.0\npytest-cov>=4.1.0\n")
    (tmp_path / "reports").mkdir()
    return tmp_path


@pytest.fixture
def pipeline(tmp_project: Path) -> DevSecOpsPipeline:
    return DevSecOpsPipeline(project_root=tmp_project)


# ---------------------------------------------------------------------------
# SBOM generation
# ---------------------------------------------------------------------------

def test_sbom_generation_creates_file(pipeline: DevSecOpsPipeline, tmp_project: Path):
    result = pipeline.generate_sbom()
    assert result.passed
    sbom_path = tmp_project / "reports" / "sbom.json"
    assert sbom_path.exists()
    sbom = json.loads(sbom_path.read_text())
    assert sbom["bomFormat"] == "CycloneDX"
    assert len(sbom["components"]) >= 2  # pytest + pytest-cov


def test_sbom_stage_name(pipeline: DevSecOpsPipeline):
    result = pipeline.generate_sbom()
    assert result.stage == "sbom_generation"


# ---------------------------------------------------------------------------
# Dependency scan
# ---------------------------------------------------------------------------

def test_dependency_scan_after_sbom(pipeline: DevSecOpsPipeline):
    pipeline.generate_sbom()
    result = pipeline.scan_dependencies()
    assert isinstance(result.passed, bool)
    assert result.stage == "dependency_scan"


def test_dependency_scan_creates_report(pipeline: DevSecOpsPipeline, tmp_project: Path):
    pipeline.generate_sbom()
    pipeline.scan_dependencies()
    report_path = tmp_project / "reports" / "dependency-scan.json"
    assert report_path.exists()
    data = json.loads(report_path.read_text())
    assert "findings" in data
    assert "summary" in data


# ---------------------------------------------------------------------------
# Policy validation
# ---------------------------------------------------------------------------

def test_policy_validation_no_policies(pipeline: DevSecOpsPipeline):
    result = pipeline.validate_policies()
    assert result.passed  # no policies means no violations


def test_policy_validation_with_rego(pipeline: DevSecOpsPipeline, tmp_project: Path):
    policies_dir = tmp_project / "policies"
    policies_dir.mkdir()
    (policies_dir / "allow_all.rego").write_text('package main\ndefault allow = true\n')
    result = pipeline.validate_policies()
    assert result.stage == "policy_validation"
    assert result.passed


# ---------------------------------------------------------------------------
# Full pipeline run
# ---------------------------------------------------------------------------

def test_pipeline_run_returns_report(pipeline: DevSecOpsPipeline):
    report = pipeline.run()
    assert isinstance(report, PipelineReport)
    assert report.run_id
    assert report.overall_status in ("passed", "failed")
    assert len(report.stages) > 0


def test_pipeline_run_writes_report_file(pipeline: DevSecOpsPipeline, tmp_project: Path):
    pipeline.run()
    reports = list((tmp_project / "reports").glob("pipeline-*.json"))
    assert len(reports) == 1
    data = json.loads(reports[0].read_text())
    assert "run_id" in data
    assert "stages" in data


def test_pipeline_to_dict(pipeline: DevSecOpsPipeline):
    report = pipeline.run()
    d = report.to_dict()
    assert isinstance(d["stages"], list)
    assert "overall_status" in d
