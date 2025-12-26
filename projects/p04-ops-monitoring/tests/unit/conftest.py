"""
Pytest configuration and shared fixtures for P04 unit tests.
"""

import os
import pytest


@pytest.fixture(scope="session")
def project_root():
    """Return the absolute path to the project root directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


@pytest.fixture(scope="session")
def config_dir(project_root):
    """Return the path to the config directory."""
    return os.path.join(project_root, "config")


@pytest.fixture(scope="session")
def dashboards_dir(config_dir):
    """Return the path to the dashboards directory."""
    return os.path.join(config_dir, "dashboards")


@pytest.fixture(scope="session")
def prometheus_config_file(config_dir):
    """Return the path to prometheus.yml."""
    return os.path.join(config_dir, "prometheus.yml")


@pytest.fixture(scope="session")
def alerts_config_file(config_dir):
    """Return the path to alerts.yml."""
    return os.path.join(config_dir, "alerts.yml")


@pytest.fixture(scope="session")
def alertmanager_config_file(config_dir):
    """Return the path to alertmanager.yml."""
    return os.path.join(config_dir, "alertmanager.yml")


@pytest.fixture(scope="session")
def grafana_datasources_file(config_dir):
    """Return the path to grafana-datasources.yml."""
    return os.path.join(config_dir, "grafana-datasources.yml")
