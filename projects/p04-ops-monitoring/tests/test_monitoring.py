"""Unit tests for monitoring stack configuration."""
from pathlib import Path

import pytest


@pytest.fixture
def project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent


def test_docker_compose_exists(project_root):
    """Verify docker-compose.yml exists."""
    compose_file = project_root / "docker-compose.yml"
    assert compose_file.exists(), f"docker-compose.yml not found: {compose_file}"


def test_prometheus_config_exists(project_root):
    """Verify Prometheus config exists."""
    config_file = project_root / "config" / "prometheus.yml"
    assert config_file.exists(), f"Prometheus config not found: {config_file}"


def test_alerts_config_exists(project_root):
    """Verify alerts config exists."""
    alerts_file = project_root / "config" / "alerts.yml"
    assert alerts_file.exists(), f"Alerts config not found: {alerts_file}"


def test_prometheus_config_valid_yaml(project_root):
    """Verify Prometheus config is valid YAML."""
    import yaml
    config_file = project_root / "config" / "prometheus.yml"
    with open(config_file) as f:
        data = yaml.safe_load(f)
    assert data is not None
    assert "global" in data
    assert "scrape_configs" in data


def test_alerts_has_instance_down_rule(project_root):
    """Verify alerts include InstanceDown rule."""
    import yaml
    alerts_file = project_root / "config" / "alerts.yml"
    with open(alerts_file) as f:
        data = yaml.safe_load(f)

    groups = data.get("groups", [])
    assert len(groups) > 0, "No alert groups defined"

    alerts = []
    for group in groups:
        alerts.extend(group.get("rules", []))

    alert_names = [alert.get("alert") for alert in alerts]
    assert "InstanceDown" in alert_names, "Missing InstanceDown alert"
