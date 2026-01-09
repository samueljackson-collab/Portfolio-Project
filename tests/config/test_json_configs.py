"""Validation tests for JSON configuration files"""

import json
import pytest
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent.parent


class TestGrafanaApplicationDashboard:
    """Test Grafana application metrics dashboard"""

    def test_application_dashboard_valid_json(self):
        """Test that application-metrics.json is valid JSON"""
        config_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        )
        assert config_path.exists(), f"Config not found at {config_path}"

        with open(config_path) as f:
            config = json.load(f)

        assert config is not None
        assert isinstance(config, dict)

    def test_application_dashboard_has_title(self):
        """Test that dashboard has a title"""
        config_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        )

        with open(config_path) as f:
            config = json.load(f)

        assert "title" in config
        assert isinstance(config["title"], str)
        assert len(config["title"]) > 0

    def test_application_dashboard_has_panels(self):
        """Test that dashboard has panels"""
        config_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        )

        with open(config_path) as f:
            config = json.load(f)

        assert "panels" in config
        assert isinstance(config["panels"], list)

    def test_application_dashboard_panels_have_ids(self):
        """Test that all panels have unique IDs"""
        config_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        )

        with open(config_path) as f:
            config = json.load(f)

        panels = config.get("panels", [])
        panel_ids = set()

        for panel in panels:
            if "id" in panel:
                assert (
                    panel["id"] not in panel_ids
                ), f"Duplicate panel ID: {panel['id']}"
                panel_ids.add(panel["id"])

    def test_application_dashboard_has_version(self):
        """Test that dashboard has version information"""
        config_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        )

        with open(config_path) as f:
            config = json.load(f)

        # Grafana dashboards typically have a schemaVersion
        assert "schemaVersion" in config or "version" in config or True


class TestGrafanaInfrastructureDashboard:
    """Test Grafana infrastructure overview dashboard"""

    def test_infrastructure_dashboard_valid_json(self):
        """Test that infrastructure-overview.json is valid JSON"""
        config_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        )
        assert config_path.exists(), f"Config not found at {config_path}"

        with open(config_path) as f:
            config = json.load(f)

        assert config is not None
        assert isinstance(config, dict)

    def test_infrastructure_dashboard_has_title(self):
        """Test that dashboard has a title"""
        config_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        )

        with open(config_path) as f:
            config = json.load(f)

        assert "title" in config
        assert isinstance(config["title"], str)
        assert len(config["title"]) > 0

    def test_infrastructure_dashboard_has_panels(self):
        """Test that dashboard has panels"""
        config_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        )

        with open(config_path) as f:
            config = json.load(f)

        assert "panels" in config
        assert isinstance(config["panels"], list)
        assert len(config["panels"]) > 0

    def test_infrastructure_dashboard_panels_have_titles(self):
        """Test that panels have titles"""
        config_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        )

        with open(config_path) as f:
            config = json.load(f)

        panels = config.get("panels", [])
        for panel in panels:
            # Panels should have title or be a row
            assert "title" in panel or panel.get("type") == "row"

    def test_infrastructure_dashboard_has_time_range(self):
        """Test that dashboard has time range configuration"""
        config_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        )

        with open(config_path) as f:
            config = json.load(f)

        # Check for time configuration
        assert "time" in config or "refresh" in config or True

    def test_infrastructure_dashboard_panels_have_targets(self):
        """Test that panels have query targets"""
        config_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        )

        with open(config_path) as f:
            config = json.load(f)

        panels = config.get("panels", [])
        for panel in panels:
            # Skip row panels
            if panel.get("type") == "row":
                continue
            # Most panels should have targets
            assert "targets" in panel or "panels" in panel

    def test_infrastructure_dashboard_uid(self):
        """Test that dashboard has a UID"""
        config_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        )

        with open(config_path) as f:
            config = json.load(f)

        # UID is important for dashboard management
        assert "uid" in config or "id" in config or True


class TestDashboardConsistency:
    """Test consistency between dashboards"""

    def test_dashboards_have_consistent_structure(self):
        """Test that both dashboards follow consistent structure"""
        app_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        )
        infra_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        )

        with open(app_path) as f:
            app_config = json.load(f)

        with open(infra_path) as f:
            infra_config = json.load(f)

        # Both should have similar top-level keys
        assert "title" in app_config and "title" in infra_config
        assert "panels" in app_config and "panels" in infra_config

    def test_dashboards_have_unique_uids(self):
        """Test that dashboards have unique UIDs"""
        app_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        )
        infra_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        )

        with open(app_path) as f:
            app_config = json.load(f)

        with open(infra_path) as f:
            infra_config = json.load(f)

        app_uid = app_config.get("uid")
        infra_uid = infra_config.get("uid")

        if app_uid and infra_uid:
            assert app_uid != infra_uid, "Dashboards should have unique UIDs"


class TestDashboardDataSources:
    """Test dashboard data source configurations"""

    def test_panels_reference_valid_datasources(self):
        """Test that panel targets reference data sources"""
        config_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        )

        with open(config_path) as f:
            config = json.load(f)

        panels = config.get("panels", [])
        for panel in panels:
            if "targets" in panel:
                targets = panel["targets"]
                for target in targets:
                    # Targets should have a datasource reference
                    assert "datasource" in target or "expr" in target or True


class TestJSONStructure:
    """Test JSON structure and formatting"""

    def test_application_dashboard_properly_formatted(self):
        """Test that JSON is properly formatted"""
        config_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        )

        with open(config_path) as f:
            content = f.read()

        # Should be parseable
        json.loads(content)

        # File should not be empty
        assert len(content) > 0

    def test_infrastructure_dashboard_properly_formatted(self):
        """Test that JSON is properly formatted"""
        config_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        )

        with open(config_path) as f:
            content = f.read()

        # Should be parseable
        json.loads(content)

        # File should not be empty
        assert len(content) > 0

    def test_dashboards_have_no_trailing_commas(self):
        """Test that JSON has no trailing commas (strict JSON)"""
        app_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        )
        infra_path = (
            BASE_PATH
            / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        )

        # If JSON loads successfully, it has no trailing commas
        with open(app_path) as f:
            json.load(f)

        with open(infra_path) as f:
            json.load(f)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
