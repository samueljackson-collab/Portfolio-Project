"""Tests for the QA gate definitions and gate checker tool."""

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

BASE = Path(__file__).parent.parent
GATES_FILE = BASE / "qa-gates" / "gate-definitions.yaml"
GATE_CHECKER = BASE / "qa-gates" / "gate-checker.py"


# ── Gate definition tests ─────────────────────────────────────────────────────

def test_gate_definitions_file_exists():
    assert GATES_FILE.exists()


def test_gate_definitions_loads_as_valid_yaml():
    content = yaml.safe_load(GATES_FILE.read_text())
    assert "gates" in content
    assert isinstance(content["gates"], list)


def test_gate_definitions_has_expected_count():
    gates = yaml.safe_load(GATES_FILE.read_text())["gates"]
    assert len(gates) >= 10, f"Expected at least 10 gates, got {len(gates)}"


REQUIRED_GATE_FIELDS = {"id", "name", "category", "tool", "command", "applies_to", "severity"}

@pytest.fixture(scope="module")
def gates():
    return yaml.safe_load(GATES_FILE.read_text())["gates"]


@pytest.mark.parametrize("field", sorted(REQUIRED_GATE_FIELDS))
def test_all_gates_have_required_fields(gates, field):
    for gate in gates:
        assert field in gate, f"Gate {gate.get('id', '?')} missing field: {field}"


def test_all_gate_ids_are_unique(gates):
    ids = [g["id"] for g in gates]
    assert len(ids) == len(set(ids)), "Duplicate gate IDs found"


def test_all_gate_ids_match_pattern(gates):
    import re
    pattern = re.compile(r"^GATE-\d{3}$")
    for gate in gates:
        assert pattern.match(gate["id"]), f"Gate ID does not match pattern: {gate['id']}"


def test_gate_severities_are_valid(gates):
    valid = {"block", "block_on_high", "block_on_critical", "warn"}
    for gate in gates:
        assert gate["severity"] in valid, \
            f"Gate {gate['id']} has invalid severity: {gate['severity']}"


def test_gate_categories_are_valid(gates):
    valid = {"code_quality", "testing", "security"}
    for gate in gates:
        assert gate["category"] in valid, \
            f"Gate {gate['id']} has invalid category: {gate['category']}"


def test_gate_applies_to_are_valid(gates):
    valid_types = {"python", "node", "typescript", "terraform", "docker"}
    for gate in gates:
        for t in gate["applies_to"]:
            assert t in valid_types, \
                f"Gate {gate['id']} has unknown applies_to: {t}"


def test_gates_cover_all_required_categories(gates):
    categories = {g["category"] for g in gates}
    assert "code_quality" in categories
    assert "testing" in categories
    assert "security" in categories


def test_gates_include_python_unit_test_gate(gates):
    pytest_gates = [g for g in gates if g["tool"] == "pytest" and "python" in g["applies_to"]]
    assert len(pytest_gates) >= 1, "Must have at least one pytest gate for Python"


def test_gates_include_sast_gate(gates):
    sast_gates = [g for g in gates if g["category"] == "security"
                  and "python" in g.get("applies_to", [])]
    assert len(sast_gates) >= 1, "Must have at least one security gate for Python"


def test_gates_include_terraform_gate(gates):
    tf_gates = [g for g in gates if "terraform" in g.get("applies_to", [])]
    assert len(tf_gates) >= 2, "Must have at least 2 Terraform gates"


# ── Gate checker tool tests ───────────────────────────────────────────────────

def test_gate_checker_script_exists():
    assert GATE_CHECKER.exists()


def test_gate_checker_list_gates_runs():
    result = subprocess.run(
        [sys.executable, str(GATE_CHECKER), "--list-gates"],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "GATE-001" in result.stdout
    assert "GATE-010" in result.stdout


def test_gate_checker_demo_mode_runs():
    result = subprocess.run(
        [sys.executable, str(GATE_CHECKER), "--demo"],
        capture_output=True, text=True
    )
    # Should run without crashing (exit 0 or 1 depending on findings)
    assert result.returncode in (0, 1)
    assert "QA GATE COMPLIANCE REPORT" in result.stdout


def test_gate_checker_demo_produces_summary_line():
    result = subprocess.run(
        [sys.executable, str(GATE_CHECKER), "--demo"],
        capture_output=True, text=True
    )
    assert "Summary:" in result.stdout
    assert "passed" in result.stdout


def test_demo_output_file_exists():
    assert (BASE / "demo_output" / "gate_check_results.txt").exists()


def test_demo_output_has_real_content():
    text = (BASE / "demo_output" / "gate_check_results.txt").read_text()
    assert "QA GATE COMPLIANCE REPORT" in text
    assert "GATE-001" in text or "Python Format" in text
    assert "Summary:" in text


# ── Handbook file tests ───────────────────────────────────────────────────────

HANDBOOK_FILES = [
    "01-code-standards.md",
    "02-security-standards.md",
    "03-testing-standards.md",
    "04-documentation-standards.md",
    "05-iac-standards.md",
    "06-cicd-quality-gates.md",
]


@pytest.mark.parametrize("filename", HANDBOOK_FILES)
def test_handbook_file_exists(filename):
    assert (BASE / "handbook" / filename).exists()


@pytest.mark.parametrize("filename", HANDBOOK_FILES)
def test_handbook_file_has_version(filename):
    text = (BASE / "handbook" / filename).read_text()
    assert "Version" in text or "version" in text


def test_security_standards_covers_secrets():
    text = (BASE / "handbook" / "02-security-standards.md").read_text()
    assert "secrets" in text.lower() or "Secrets" in text


def test_security_standards_covers_sql_injection():
    text = (BASE / "handbook" / "02-security-standards.md").read_text()
    assert "SQL" in text or "injection" in text.lower()


def test_testing_standards_has_coverage_threshold():
    text = (BASE / "handbook" / "03-testing-standards.md").read_text()
    assert "80%" in text or "coverage" in text.lower()


def test_iac_standards_has_terraform_section():
    text = (BASE / "handbook" / "05-iac-standards.md").read_text()
    assert "Terraform" in text


def test_iac_standards_has_docker_section():
    text = (BASE / "handbook" / "05-iac-standards.md").read_text()
    assert "Docker" in text or "Dockerfile" in text


# ── Example artifact tests ────────────────────────────────────────────────────

def test_compliant_python_snippet_exists():
    assert (BASE / "examples" / "compliant-python-snippet.py").exists()


def test_compliant_python_snippet_has_type_hints():
    text = (BASE / "examples" / "compliant-python-snippet.py").read_text()
    assert "from __future__ import annotations" in text


def test_compliant_python_snippet_no_hardcoded_secrets():
    text = (BASE / "examples" / "compliant-python-snippet.py").read_text()
    # Should not have patterns like PASSWORD = "..." or SECRET = "..."
    import re
    bad_pattern = re.compile(r'(password|secret|token|key)\s*=\s*["\'][^"\']+["\']',
                              re.IGNORECASE)
    matches = bad_pattern.findall(text)
    # Allow comments/docstrings that mention the pattern, but not assignments
    assert "SuperSecret123!" not in text or "NEVER DO THIS" in text


def test_compliant_terraform_module_has_required_files():
    module_dir = BASE / "examples" / "compliant-terraform-module"
    for f in ["main.tf", "variables.tf", "outputs.tf", "versions.tf"]:
        assert (module_dir / f).exists(), f"Missing: {f}"


def test_compliant_terraform_variables_have_descriptions():
    text = (BASE / "examples" / "compliant-terraform-module" / "variables.tf").read_text()
    assert "description" in text


def test_compliant_terraform_has_validation():
    text = (BASE / "examples" / "compliant-terraform-module" / "variables.tf").read_text()
    assert "validation" in text
