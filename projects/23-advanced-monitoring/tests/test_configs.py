from pathlib import Path

import json
import yaml


def test_dashboard_contains_panels():
    dashboard = json.loads(Path("projects/23-advanced-monitoring/dashboards/portfolio.json").read_text())
    assert dashboard.get("panels") is not None


def test_alerts_yaml_has_rules():
    rules = yaml.safe_load(Path("projects/23-advanced-monitoring/alerts/portfolio_rules.yml").read_text())
    assert any(group.get("rules") for group in rules.get("groups", []))


def test_kustomize_base_declares_resources():
    kustomization = yaml.safe_load(Path("projects/23-advanced-monitoring/manifests/base/kustomization.yaml").read_text())
    assert "resources" in kustomization
