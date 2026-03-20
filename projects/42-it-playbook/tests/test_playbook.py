"""Tests for IT Playbook completeness and content quality."""

import subprocess
import sys
from pathlib import Path

import pytest

BASE = Path(__file__).parent.parent
PLAYBOOK_DIR = BASE / "playbook"
EXAMPLES_DIR = BASE / "examples"

PHASE_FILES = [
    "01-project-intake.md",
    "02-design-architecture.md",
    "03-development.md",
    "04-testing-qa.md",
    "05-deployment-release.md",
    "06-operations-monitoring.md",
    "07-maintenance.md",
    "08-decommission.md",
]


@pytest.mark.parametrize("filename", PHASE_FILES)
def test_phase_file_exists(filename):
    assert (PLAYBOOK_DIR / filename).exists(), f"Phase file missing: {filename}"


@pytest.mark.parametrize("filename", PHASE_FILES)
def test_phase_file_has_purpose_section(filename):
    text = (PLAYBOOK_DIR / filename).read_text().lower()
    assert "purpose" in text, f"{filename}: missing Purpose section"


@pytest.mark.parametrize("filename", PHASE_FILES)
def test_phase_file_has_version(filename):
    text = (PLAYBOOK_DIR / filename).read_text()
    assert "Version" in text or "version" in text


@pytest.mark.parametrize("filename", PHASE_FILES)
def test_phase_file_has_checklist_or_steps(filename):
    text = (PLAYBOOK_DIR / filename).read_text()
    has_checklist = "- [ ]" in text or "Checklist" in text
    has_numbered_steps = any(f"{i}." in text for i in range(1, 6))
    assert has_checklist or has_numbered_steps, \
        f"{filename}: must have a checklist or numbered steps"


def test_all_8_phases_present():
    existing = {f.name for f in PLAYBOOK_DIR.glob("*.md")}
    missing = set(PHASE_FILES) - existing
    assert not missing, f"Missing phase files: {missing}"


# ── phase-specific content tests ──────────────────────────────────────────────

def test_intake_phase_has_scope():
    text = (PLAYBOOK_DIR / "01-project-intake.md").read_text()
    assert "In Scope" in text or "scope" in text.lower()


def test_design_phase_has_adr():
    text = (PLAYBOOK_DIR / "02-design-architecture.md").read_text()
    assert "ADR" in text or "Architecture Decision" in text


def test_development_phase_has_git_workflow():
    text = (PLAYBOOK_DIR / "03-development.md").read_text()
    assert "git" in text.lower() or "branch" in text.lower()


def test_testing_phase_has_coverage_requirement():
    text = (PLAYBOOK_DIR / "04-testing-qa.md").read_text()
    assert "coverage" in text.lower() or "%" in text


def test_deployment_phase_has_rollback():
    text = (PLAYBOOK_DIR / "05-deployment-release.md").read_text()
    assert "rollback" in text.lower()


def test_operations_phase_has_slo():
    text = (PLAYBOOK_DIR / "06-operations-monitoring.md").read_text()
    assert "SLO" in text or "SLI" in text


def test_maintenance_phase_has_patch_sla():
    text = (PLAYBOOK_DIR / "07-maintenance.md").read_text()
    assert "Critical" in text and ("24 hour" in text or "CVSS" in text)


def test_decommission_phase_has_data_handling():
    text = (PLAYBOOK_DIR / "08-decommission.md").read_text()
    assert "data" in text.lower() and ("archive" in text.lower() or "delete" in text.lower())


# ── example artifacts tests ───────────────────────────────────────────────────

def test_project_charter_example_exists():
    assert (EXAMPLES_DIR / "sample-project-charter.md").exists()


def test_project_charter_has_success_criteria():
    text = (EXAMPLES_DIR / "sample-project-charter.md").read_text()
    assert "Success Criteria" in text or "success criteria" in text.lower()


def test_project_charter_has_risk_table():
    text = (EXAMPLES_DIR / "sample-project-charter.md").read_text()
    assert "Risk" in text


def test_adr_example_exists():
    assert (EXAMPLES_DIR / "sample-adr-001.md").exists()


def test_adr_has_decision_section():
    text = (EXAMPLES_DIR / "sample-adr-001.md").read_text()
    assert "## Decision" in text


def test_adr_has_consequences():
    text = (EXAMPLES_DIR / "sample-adr-001.md").read_text()
    assert "Consequences" in text or "consequences" in text.lower()


# ── validator tests ───────────────────────────────────────────────────────────

def test_validator_script_exists():
    assert (BASE / "scripts" / "playbook_validator.py").exists()


def test_validator_passes_all_checks():
    result = subprocess.run(
        [sys.executable, str(BASE / "scripts" / "playbook_validator.py")],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"Validator failed:\n{result.stdout}"
    assert "10/10 checks passed" in result.stdout


def test_demo_output_exists():
    assert (BASE / "demo_output" / "validation_results.txt").exists()


def test_demo_output_shows_all_pass():
    text = (BASE / "demo_output" / "validation_results.txt").read_text()
    assert "10/10 checks passed" in text
    assert "All checks passed" in text
