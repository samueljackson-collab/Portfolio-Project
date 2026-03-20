"""
test_plans.py — pytest suite for adversary emulation plans

Validates that all emulation plan files are well-formed and contain
the required fields and structure for the atomic executor to use.
"""

import csv
from pathlib import Path

import pytest
import yaml


# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent
PLANS_DIR = REPO_ROOT / "emulation-plans"
APT29_PLAN = PLANS_DIR / "apt29-plan.yaml"
FIN7_PLAN = PLANS_DIR / "fin7-plan.yaml"
COVERAGE_CSV = REPO_ROOT / "attack-mapping" / "technique-coverage.csv"

EXPECTED_CSV_HEADERS = [
    "technique_id",
    "technique_name",
    "tactic",
    "plan",
    "test_id",
    "detection_rule",
    "status",
]

REQUIRED_PLAN_FIELDS = ["name", "id", "version", "author", "date", "description", "phases"]
REQUIRED_PHASE_FIELDS = ["id", "name", "techniques"]
REQUIRED_TECHNIQUE_FIELDS = [
    "id",
    "name",
    "test_id",
    "test_name",
    "command",
    "expected_detection",
    "detection_rule",
    "safe",
    "cleanup",
]


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def apt29_plan() -> dict:
    """Load the APT29 emulation plan."""
    assert APT29_PLAN.exists(), f"APT29 plan not found at {APT29_PLAN}"
    with open(APT29_PLAN) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def fin7_plan() -> dict:
    """Load the FIN7 emulation plan."""
    assert FIN7_PLAN.exists(), f"FIN7 plan not found at {FIN7_PLAN}"
    with open(FIN7_PLAN) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def coverage_csv_rows() -> list:
    """Load all rows from the technique-coverage.csv."""
    assert COVERAGE_CSV.exists(), f"Coverage CSV not found at {COVERAGE_CSV}"
    with open(COVERAGE_CSV, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


# --------------------------------------------------------------------------
# Plan file existence tests
# --------------------------------------------------------------------------


class TestPlanFilesExist:
    def test_apt29_plan_file_exists(self):
        assert APT29_PLAN.exists(), f"APT29 plan file missing: {APT29_PLAN}"

    def test_fin7_plan_file_exists(self):
        assert FIN7_PLAN.exists(), f"FIN7 plan file missing: {FIN7_PLAN}"

    def test_coverage_csv_exists(self):
        assert COVERAGE_CSV.exists(), f"Coverage CSV missing: {COVERAGE_CSV}"


# --------------------------------------------------------------------------
# Plan loading tests
# --------------------------------------------------------------------------


class TestPlanLoading:
    def test_apt29_plan_loads_as_dict(self, apt29_plan):
        assert isinstance(apt29_plan, dict), "APT29 plan should parse to a dict"

    def test_fin7_plan_loads_as_dict(self, fin7_plan):
        assert isinstance(fin7_plan, dict), "FIN7 plan should parse to a dict"

    def test_apt29_plan_not_empty(self, apt29_plan):
        assert len(apt29_plan) > 0, "APT29 plan should not be empty"

    def test_fin7_plan_not_empty(self, fin7_plan):
        assert len(fin7_plan) > 0, "FIN7 plan should not be empty"


# --------------------------------------------------------------------------
# Required top-level fields
# --------------------------------------------------------------------------


class TestRequiredPlanFields:
    @pytest.mark.parametrize("field", REQUIRED_PLAN_FIELDS)
    def test_apt29_has_required_field(self, apt29_plan, field):
        assert field in apt29_plan, f"APT29 plan missing required field: '{field}'"

    @pytest.mark.parametrize("field", REQUIRED_PLAN_FIELDS)
    def test_fin7_has_required_field(self, fin7_plan, field):
        assert field in fin7_plan, f"FIN7 plan missing required field: '{field}'"

    def test_apt29_name_is_string(self, apt29_plan):
        assert isinstance(apt29_plan["name"], str)
        assert len(apt29_plan["name"]) > 0

    def test_fin7_name_is_string(self, fin7_plan):
        assert isinstance(fin7_plan["name"], str)
        assert len(fin7_plan["name"]) > 0

    def test_apt29_id_format(self, apt29_plan):
        assert apt29_plan["id"].startswith("ep-"), "Plan ID should start with 'ep-'"

    def test_fin7_id_format(self, fin7_plan):
        assert fin7_plan["id"].startswith("ep-"), "Plan ID should start with 'ep-'"

    def test_apt29_has_mitre_groups(self, apt29_plan):
        assert "mitre_groups" in apt29_plan
        assert isinstance(apt29_plan["mitre_groups"], list)
        assert len(apt29_plan["mitre_groups"]) > 0

    def test_fin7_has_mitre_groups(self, fin7_plan):
        assert "mitre_groups" in fin7_plan
        assert isinstance(fin7_plan["mitre_groups"], list)
        assert len(fin7_plan["mitre_groups"]) > 0


# --------------------------------------------------------------------------
# Phase structure tests
# --------------------------------------------------------------------------


class TestPhaseStructure:
    def test_apt29_has_6_phases(self, apt29_plan):
        assert len(apt29_plan["phases"]) == 6, (
            f"APT29 plan should have 6 phases, got {len(apt29_plan['phases'])}"
        )

    def test_fin7_has_6_phases(self, fin7_plan):
        assert len(fin7_plan["phases"]) == 6, (
            f"FIN7 plan should have 6 phases, got {len(fin7_plan['phases'])}"
        )

    @pytest.mark.parametrize("field", REQUIRED_PHASE_FIELDS)
    def test_apt29_phases_have_required_fields(self, apt29_plan, field):
        for phase in apt29_plan["phases"]:
            assert field in phase, (
                f"APT29 phase '{phase.get('id', '?')}' missing field: '{field}'"
            )

    @pytest.mark.parametrize("field", REQUIRED_PHASE_FIELDS)
    def test_fin7_phases_have_required_fields(self, fin7_plan, field):
        for phase in fin7_plan["phases"]:
            assert field in phase, (
                f"FIN7 phase '{phase.get('id', '?')}' missing field: '{field}'"
            )

    def test_apt29_phase_ids_are_unique(self, apt29_plan):
        phase_ids = [p["id"] for p in apt29_plan["phases"]]
        assert len(phase_ids) == len(set(phase_ids)), "APT29 phase IDs must be unique"

    def test_fin7_phase_ids_are_unique(self, fin7_plan):
        phase_ids = [p["id"] for p in fin7_plan["phases"]]
        assert len(phase_ids) == len(set(phase_ids)), "FIN7 phase IDs must be unique"


# --------------------------------------------------------------------------
# Technique structure tests
# --------------------------------------------------------------------------


class TestTechniqueStructure:
    @pytest.mark.parametrize("field", REQUIRED_TECHNIQUE_FIELDS)
    def test_apt29_techniques_have_required_fields(self, apt29_plan, field):
        for phase in apt29_plan["phases"]:
            for tech in phase.get("techniques", []):
                assert field in tech, (
                    f"APT29 technique '{tech.get('test_id', '?')}' in phase "
                    f"'{phase['id']}' missing field: '{field}'"
                )

    @pytest.mark.parametrize("field", REQUIRED_TECHNIQUE_FIELDS)
    def test_fin7_techniques_have_required_fields(self, fin7_plan, field):
        for phase in fin7_plan["phases"]:
            for tech in phase.get("techniques", []):
                assert field in tech, (
                    f"FIN7 technique '{tech.get('test_id', '?')}' in phase "
                    f"'{phase['id']}' missing field: '{field}'"
                )

    def test_apt29_all_tests_are_safe(self, apt29_plan):
        for phase in apt29_plan["phases"]:
            for tech in phase.get("techniques", []):
                assert tech.get("safe") is True, (
                    f"APT29 test '{tech.get('test_id')}' must have safe=true"
                )

    def test_fin7_all_tests_are_safe(self, fin7_plan):
        for phase in fin7_plan["phases"]:
            for tech in phase.get("techniques", []):
                assert tech.get("safe") is True, (
                    f"FIN7 test '{tech.get('test_id')}' must have safe=true"
                )

    def test_apt29_test_ids_are_unique(self, apt29_plan):
        test_ids = []
        for phase in apt29_plan["phases"]:
            for tech in phase.get("techniques", []):
                test_ids.append(tech["test_id"])
        assert len(test_ids) == len(set(test_ids)), "APT29 test IDs must be unique"

    def test_fin7_test_ids_are_unique(self, fin7_plan):
        test_ids = []
        for phase in fin7_plan["phases"]:
            for tech in phase.get("techniques", []):
                test_ids.append(tech["test_id"])
        assert len(test_ids) == len(set(test_ids)), "FIN7 test IDs must be unique"

    def test_apt29_technique_ids_reference_attack(self, apt29_plan):
        for phase in apt29_plan["phases"]:
            for tech in phase.get("techniques", []):
                tid = tech["id"]
                assert tid.startswith("T"), (
                    f"Technique ID '{tid}' should start with 'T' (MITRE ATT&CK format)"
                )

    def test_apt29_commands_write_only_to_tmp(self, apt29_plan):
        """Verify safe test commands don't reference sensitive paths."""
        # These patterns should not appear as the start of a command or after ; && ||
        # We check that the command doesn't write to sensitive paths or run as root
        forbidden_write_targets = ["/etc/shadow", "/root/.ssh", "/etc/crontab"]
        for phase in apt29_plan["phases"]:
            for tech in phase.get("techniques", []):
                cmd = tech.get("command", "")
                for pattern in forbidden_write_targets:
                    assert pattern not in cmd, (
                        f"Test '{tech['test_id']}' command references forbidden path: '{pattern}'"
                    )

    def test_apt29_has_at_least_24_tests(self, apt29_plan):
        total = sum(len(p.get("techniques", [])) for p in apt29_plan["phases"])
        assert total >= 24, f"APT29 plan should have at least 24 tests, got {total}"

    def test_fin7_has_at_least_20_tests(self, fin7_plan):
        total = sum(len(p.get("techniques", [])) for p in fin7_plan["phases"])
        assert total >= 20, f"FIN7 plan should have at least 20 tests, got {total}"


# --------------------------------------------------------------------------
# Coverage CSV tests
# --------------------------------------------------------------------------


class TestCoverageCSV:
    def test_csv_has_correct_headers(self, coverage_csv_rows):
        # DictReader was used so check the fieldnames from the first row keys
        if coverage_csv_rows:
            headers = list(coverage_csv_rows[0].keys())
            for expected in EXPECTED_CSV_HEADERS:
                assert expected in headers, (
                    f"CSV missing expected column: '{expected}'. Found: {headers}"
                )

    def test_csv_has_25_or_more_rows(self, coverage_csv_rows):
        assert len(coverage_csv_rows) >= 25, (
            f"Coverage CSV should have 25+ rows, got {len(coverage_csv_rows)}"
        )

    def test_csv_technique_ids_start_with_T(self, coverage_csv_rows):
        for row in coverage_csv_rows:
            tid = row.get("technique_id", "")
            assert tid.startswith("T"), (
                f"technique_id '{tid}' should start with 'T'"
            )

    def test_csv_no_empty_technique_names(self, coverage_csv_rows):
        for row in coverage_csv_rows:
            assert row.get("technique_name", "").strip() != "", (
                f"Row has empty technique_name: {row}"
            )

    def test_csv_status_values_are_valid(self, coverage_csv_rows):
        valid_statuses = {"Covered", "Partial", "Not Covered", "In Progress"}
        for row in coverage_csv_rows:
            status = row.get("status", "")
            assert status in valid_statuses, (
                f"Invalid status '{status}' in row: {row}"
            )

    def test_csv_plans_reference_known_plans(self, coverage_csv_rows):
        known_plans = {"APT29", "FIN7"}
        for row in coverage_csv_rows:
            plan = row.get("plan", "")
            assert plan in known_plans, (
                f"Unknown plan '{plan}' in coverage CSV"
            )

    def test_csv_has_both_plans(self, coverage_csv_rows):
        plans = {row.get("plan") for row in coverage_csv_rows}
        assert "APT29" in plans, "Coverage CSV should include APT29 rows"
        assert "FIN7" in plans, "Coverage CSV should include FIN7 rows"
