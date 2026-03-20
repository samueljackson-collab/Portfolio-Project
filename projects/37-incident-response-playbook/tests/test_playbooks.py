"""Tests for incident response playbooks and timeline generator."""

import subprocess
import sys
from pathlib import Path

import pytest

BASE = Path(__file__).parent.parent

# ── playbook content tests ────────────────────────────────────────────────────

RANSOMWARE_PLAYBOOK = BASE / "playbooks" / "ransomware-ir.md"
PHISHING_PLAYBOOK = BASE / "playbooks" / "phishing-ir.md"
DATABREACH_PLAYBOOK = BASE / "playbooks" / "data-breach-ir.md"

REQUIRED_PHASES = [
    "Preparation",
    "Identification",
    "Containment",
    "Eradication",
    "Recovery",
]


@pytest.mark.parametrize("playbook", [RANSOMWARE_PLAYBOOK, PHISHING_PLAYBOOK, DATABREACH_PLAYBOOK],
                         ids=["ransomware", "phishing", "data-breach"])
def test_playbook_exists(playbook):
    assert playbook.exists(), f"Playbook not found: {playbook}"


@pytest.mark.parametrize("playbook", [RANSOMWARE_PLAYBOOK, PHISHING_PLAYBOOK, DATABREACH_PLAYBOOK],
                         ids=["ransomware", "phishing", "data-breach"])
def test_playbook_has_title(playbook):
    text = playbook.read_text()
    assert text.startswith("# "), f"{playbook.name}: must start with a H1 title"


@pytest.mark.parametrize("phase", REQUIRED_PHASES)
def test_ransomware_playbook_has_all_picerl_phases(phase):
    text = RANSOMWARE_PLAYBOOK.read_text()
    assert f"Phase" in text and phase in text, \
        f"Ransomware playbook missing Phase: {phase}"


def test_ransomware_playbook_has_playbook_id():
    text = RANSOMWARE_PLAYBOOK.read_text()
    assert "IRP-001" in text


def test_ransomware_playbook_has_containment_checklist():
    text = RANSOMWARE_PLAYBOOK.read_text()
    assert "Containment Checklist" in text


def test_ransomware_playbook_has_ioc_template():
    text = RANSOMWARE_PLAYBOOK.read_text()
    assert "incident_id" in text and "c2_ips" in text


def test_ransomware_playbook_has_recovery_tiers():
    text = RANSOMWARE_PLAYBOOK.read_text()
    assert "RTO" in text


def test_phishing_playbook_has_triage_questions():
    text = PHISHING_PLAYBOOK.read_text()
    assert "Triage Questions" in text


def test_phishing_playbook_has_metrics():
    text = PHISHING_PLAYBOOK.read_text()
    assert "Metrics" in text and "MTTD" in text.upper() or "Time to" in text


def test_databreach_playbook_has_regulatory_table():
    text = DATABREACH_PLAYBOOK.read_text()
    assert "GDPR" in text and "HIPAA" in text and "72 hours" in text


def test_databreach_playbook_has_notification_workflow():
    text = DATABREACH_PLAYBOOK.read_text()
    assert "Notification" in text


# ── escalation matrix tests ───────────────────────────────────────────────────

ESCALATION_MATRIX = BASE / "escalation" / "escalation-matrix.md"


def test_escalation_matrix_exists():
    assert ESCALATION_MATRIX.exists()


def test_escalation_matrix_has_severity_levels():
    text = ESCALATION_MATRIX.read_text()
    for level in ["P1", "P2", "P3", "P4"]:
        assert level in text, f"Escalation matrix missing severity level {level}"


def test_escalation_matrix_has_sla_table():
    text = ESCALATION_MATRIX.read_text()
    assert "SLA" in text or "Acknowledgement" in text


def test_communication_templates_exist():
    assert (BASE / "escalation" / "communication-templates.md").exists()


def test_communication_templates_has_customer_notification():
    text = (BASE / "escalation" / "communication-templates.md").read_text()
    assert "Customer Notification" in text or "Dear" in text


# ── template tests ────────────────────────────────────────────────────────────

def test_incident_ticket_template_exists():
    assert (BASE / "templates" / "incident-ticket.md").exists()


def test_pir_template_exists():
    assert (BASE / "templates" / "post-incident-report.md").exists()


def test_pir_template_has_timeline():
    text = (BASE / "templates" / "post-incident-report.md").read_text()
    assert "Timeline" in text


def test_pir_template_has_metrics():
    text = (BASE / "templates" / "post-incident-report.md").read_text()
    assert "MTTD" in text and "MTTC" in text and "MTTR" in text


def test_pir_template_has_root_cause():
    text = (BASE / "templates" / "post-incident-report.md").read_text()
    assert "Root Cause" in text


# ── timeline generator tests ──────────────────────────────────────────────────

def test_timeline_generator_exists():
    assert (BASE / "scripts" / "ir_timeline_generator.py").exists()


def test_timeline_generator_runs_demo():
    result = subprocess.run(
        [sys.executable, str(BASE / "scripts" / "ir_timeline_generator.py"), "--demo"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    assert "INC-2026-0042" in result.stdout
    assert "MTTD" in result.stdout


def test_timeline_generator_calculates_mttd():
    result = subprocess.run(
        [sys.executable, str(BASE / "scripts" / "ir_timeline_generator.py"), "--demo"],
        capture_output=True, text=True
    )
    assert "22 min" in result.stdout, "MTTD should be 22 minutes for demo incident"


def test_timeline_generator_calculates_mttc():
    result = subprocess.run(
        [sys.executable, str(BASE / "scripts" / "ir_timeline_generator.py"), "--demo"],
        capture_output=True, text=True
    )
    assert "15 min" in result.stdout, "MTTC should be 15 minutes for demo incident"


def test_demo_output_file_exists():
    assert (BASE / "demo_output" / "sample_ir_timeline.txt").exists()


def test_demo_output_has_real_content():
    text = (BASE / "demo_output" / "sample_ir_timeline.txt").read_text()
    assert "LockBit" in text and "MTTD" in text and "Containment" in text
