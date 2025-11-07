"""Test observability configuration."""
import pytest
import yaml
from pathlib import Path

def test_prometheus_config_exists():
    """Test Prometheus config exists."""
    config = Path(__file__).parent.parent / "config" / "prometheus.yml"
    assert config.exists()

def test_prometheus_config_valid():
    """Test Prometheus config is valid YAML."""
    config = Path(__file__).parent.parent / "config" / "prometheus.yml"
    with open(config) as f:
        data = yaml.safe_load(f)
    assert 'scrape_configs' in data
    assert len(data['scrape_configs']) > 0

def test_dashboard_exists():
    """Test at least one dashboard exists."""
    dashboards_dir = Path(__file__).parent.parent / "dashboards"
    dashboards = list(dashboards_dir.glob("*.json"))
    assert len(dashboards) > 0
