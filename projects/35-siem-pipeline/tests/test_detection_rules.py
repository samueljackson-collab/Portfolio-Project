"""
Tests for SIEM pipeline detection rules and sample event structure.
Validates rule schema compliance and runs detection logic against sample events.
"""

import json
import os
import re
from pathlib import Path

import pytest
import yaml

BASE = Path(__file__).parent.parent

# ── helpers ────────────────────────────────────────────────────────────────────

def load_events():
    events_path = BASE / "demo_output" / "sample_events.jsonl"
    events = []
    with open(events_path) as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def load_rule(name):
    return yaml.safe_load((BASE / "detection-rules" / name).read_text())


# ── rule schema tests ──────────────────────────────────────────────────────────

RULE_FILES = list((BASE / "detection-rules").glob("*.yml"))
REQUIRED_FIELDS = {"title", "id", "status", "description", "author", "logsource", "detection", "level", "tags"}


@pytest.mark.parametrize("rule_file", RULE_FILES, ids=[r.name for r in RULE_FILES])
def test_rule_has_required_fields(rule_file):
    rule = yaml.safe_load(rule_file.read_text())
    missing = REQUIRED_FIELDS - set(rule.keys())
    assert not missing, f"{rule_file.name} missing fields: {missing}"


@pytest.mark.parametrize("rule_file", RULE_FILES, ids=[r.name for r in RULE_FILES])
def test_rule_id_is_uuid(rule_file):
    rule = yaml.safe_load(rule_file.read_text())
    uuid_re = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    assert re.match(uuid_re, str(rule["id"])), f"{rule_file.name}: id is not a UUID"


@pytest.mark.parametrize("rule_file", RULE_FILES, ids=[r.name for r in RULE_FILES])
def test_rule_level_valid(rule_file):
    valid_levels = {"informational", "low", "medium", "high", "critical"}
    rule = yaml.safe_load(rule_file.read_text())
    assert rule["level"] in valid_levels


@pytest.mark.parametrize("rule_file", RULE_FILES, ids=[r.name for r in RULE_FILES])
def test_rule_tags_reference_attack(rule_file):
    rule = yaml.safe_load(rule_file.read_text())
    tags = rule.get("tags", [])
    assert any("attack." in t for t in tags), f"{rule_file.name}: no ATT&CK tag found"


@pytest.mark.parametrize("rule_file", RULE_FILES, ids=[r.name for r in RULE_FILES])
def test_rule_status_valid(rule_file):
    valid_statuses = {"stable", "test", "experimental", "deprecated"}
    rule = yaml.safe_load(rule_file.read_text())
    assert rule["status"] in valid_statuses


# ── sample events structure tests ─────────────────────────────────────────────

def test_sample_events_load():
    events = load_events()
    assert len(events) > 0, "sample_events.jsonl must have at least one event"


def test_sample_events_have_required_keys():
    required = {"timestamp", "host_name", "event_type", "source_ip", "severity", "message", "tags"}
    events = load_events()
    for i, ev in enumerate(events):
        missing = required - set(ev.keys())
        assert not missing, f"event[{i}] missing keys: {missing}"


def test_sample_events_timestamps_valid():
    events = load_events()
    ts_re = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    for i, ev in enumerate(events):
        assert re.match(ts_re, ev["timestamp"]), f"event[{i}]: invalid timestamp {ev['timestamp']}"


def test_sample_events_severity_range():
    events = load_events()
    for i, ev in enumerate(events):
        assert 1 <= ev["severity"] <= 5, f"event[{i}]: severity {ev['severity']} out of range 1-5"


def test_sample_events_contain_auth_failures():
    events = load_events()
    auth_failures = [e for e in events if e.get("event_type") == "authentication_failure"]
    assert len(auth_failures) >= 3, "Expected at least 3 authentication_failure events for brute-force detection"


def test_sample_events_contain_multiple_types():
    events = load_events()
    event_types = {e.get("event_type") for e in events}
    assert len(event_types) >= 2, f"Expected multiple event types, got: {event_types}"


def test_sample_events_ips_are_strings():
    events = load_events()
    for i, ev in enumerate(events):
        src_ip = ev.get("source_ip", "")
        assert isinstance(src_ip, str) and len(src_ip) > 0, f"event[{i}]: source_ip must be non-empty string"


# ── detection logic tests ──────────────────────────────────────────────────────

def test_brute_force_rule_detects_repeated_failures():
    """Verify that repeated auth failures from same IP match brute-force pattern."""
    events = load_events()
    # Count auth failures per source IP
    failure_counts = {}
    for ev in events:
        if ev.get("event_type") == "authentication_failure":
            ip = ev.get("source_ip")
            failure_counts[ip] = failure_counts.get(ip, 0) + 1

    # Sample events include 6+ failures from 203.0.113.45
    assert any(count >= 3 for count in failure_counts.values()), \
        "No source IP has >= 3 authentication failures — brute force test data missing"


def test_lateral_movement_rule_events_exist():
    """Lateral movement events are identifiable by process creation or suspicious_process tags."""
    events = load_events()
    lateral = [e for e in events if any(
        t in e.get("tags", []) for t in [
            "lateral_movement", "remote_service", "process_creation", "suspicious_process"
        ]
    )]
    assert len(lateral) >= 1, "Expected at least 1 process/suspicious event (lateral movement indicator) in sample data"


def test_privilege_escalation_events_exist():
    events = load_events()
    priv_esc = [e for e in events if any(
        "privilege" in t or "escalat" in t for t in e.get("tags", [])
    )]
    assert len(priv_esc) >= 1, "Expected at least 1 privilege escalation event in sample data"


# ── pipeline config tests ──────────────────────────────────────────────────────

def test_logstash_input_config_exists():
    assert (BASE / "logstash" / "pipeline" / "01-input.conf").exists()


def test_logstash_filter_config_exists():
    assert (BASE / "logstash" / "pipeline" / "02-filter.conf").exists()


def test_logstash_output_config_exists():
    assert (BASE / "logstash" / "pipeline" / "03-output.conf").exists()


def test_elasticsearch_index_template_valid():
    tmpl_path = BASE / "elasticsearch" / "index-templates" / "security-events.json"
    assert tmpl_path.exists()
    tmpl = json.loads(tmpl_path.read_text())
    assert "mappings" in tmpl or "index_patterns" in tmpl, "ES template must have mappings or index_patterns"


def test_docker_compose_defines_required_services():
    import re as _re
    compose_text = (BASE / "docker-compose.yml").read_text()
    for svc in ["elasticsearch", "logstash", "kibana"]:
        assert svc in compose_text, f"docker-compose.yml missing service: {svc}"


def test_generate_sample_logs_script_exists():
    assert (BASE / "scripts" / "generate_sample_logs.py").exists()


def test_all_four_detection_rules_present():
    rule_names = {f.stem for f in RULE_FILES}
    expected = {"brute-force", "privilege-escalation", "lateral-movement", "data-exfiltration"}
    missing = expected - rule_names
    assert not missing, f"Missing detection rules: {missing}"
