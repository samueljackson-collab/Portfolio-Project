"""
Unit tests for Grafana dashboard validation.

Tests verify:
- Dashboard JSON is valid
- Required panels are present
- Data sources are properly configured
- Dashboard structure is correct
"""

import json
import os
import pytest


class TestDashboardFiles:
    """Test dashboard file existence and validity."""

    @pytest.fixture
    def dashboards_dir(self):
        """Return path to dashboards directory."""
        return os.path.join(
            os.path.dirname(__file__),
            "../../config/dashboards"
        )

    @pytest.fixture
    def required_dashboards(self):
        """Return list of required dashboard files."""
        return [
            "infrastructure-metrics.json",
            "application-metrics.json",
            "business-metrics.json"
        ]

    def test_dashboards_directory_exists(self, dashboards_dir):
        """Test that dashboards directory exists."""
        assert os.path.isdir(dashboards_dir), \
            f"Dashboards directory not found: {dashboards_dir}"

    def test_required_dashboards_exist(self, dashboards_dir, required_dashboards):
        """Test that all required dashboard files exist."""
        for dashboard in required_dashboards:
            path = os.path.join(dashboards_dir, dashboard)
            assert os.path.exists(path), \
                f"Required dashboard not found: {dashboard}"

    def test_dashboard_files_are_json(self, dashboards_dir, required_dashboards):
        """Test that dashboard files have .json extension."""
        for dashboard in required_dashboards:
            assert dashboard.endswith(".json"), \
                f"Dashboard '{dashboard}' does not have .json extension"


class TestDashboardJSON:
    """Test dashboard JSON structure and content."""

    @pytest.fixture
    def infrastructure_dashboard(self):
        """Load infrastructure metrics dashboard."""
        path = os.path.join(
            os.path.dirname(__file__),
            "../../config/dashboards/infrastructure-metrics.json"
        )
        with open(path, "r") as f:
            return json.load(f)

    @pytest.fixture
    def application_dashboard(self):
        """Load application metrics dashboard."""
        path = os.path.join(
            os.path.dirname(__file__),
            "../../config/dashboards/application-metrics.json"
        )
        with open(path, "r") as f:
            return json.load(f)

    @pytest.fixture
    def business_dashboard(self):
        """Load business metrics dashboard."""
        path = os.path.join(
            os.path.dirname(__file__),
            "../../config/dashboards/business-metrics.json"
        )
        with open(path, "r") as f:
            return json.load(f)

    def test_infrastructure_dashboard_valid_json(self):
        """Test that infrastructure dashboard is valid JSON."""
        path = os.path.join(
            os.path.dirname(__file__),
            "../../config/dashboards/infrastructure-metrics.json"
        )
        try:
            with open(path, "r") as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in infrastructure dashboard: {e}")

    def test_application_dashboard_valid_json(self):
        """Test that application dashboard is valid JSON."""
        path = os.path.join(
            os.path.dirname(__file__),
            "../../config/dashboards/application-metrics.json"
        )
        try:
            with open(path, "r") as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in application dashboard: {e}")

    def test_business_dashboard_valid_json(self):
        """Test that business dashboard is valid JSON."""
        path = os.path.join(
            os.path.dirname(__file__),
            "../../config/dashboards/business-metrics.json"
        )
        try:
            with open(path, "r") as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in business dashboard: {e}")

    def test_dashboard_has_required_fields(self, infrastructure_dashboard):
        """Test that dashboard has required fields."""
        required_fields = ["title", "panels", "schemaVersion"]

        for field in required_fields:
            assert field in infrastructure_dashboard, \
                f"Dashboard missing required field: {field}"

    def test_dashboard_has_title(self, infrastructure_dashboard, application_dashboard,
                                  business_dashboard):
        """Test that all dashboards have titles."""
        dashboards = {
            "Infrastructure": infrastructure_dashboard,
            "Application": application_dashboard,
            "Business": business_dashboard
        }

        for name, dashboard in dashboards.items():
            assert "title" in dashboard and len(dashboard.get("title", "")) > 0, \
                f"{name} dashboard missing or empty title"

    def test_dashboard_has_panels(self, infrastructure_dashboard):
        """Test that dashboard has panels."""
        assert "panels" in infrastructure_dashboard, \
            "Dashboard missing 'panels' field"
        assert isinstance(infrastructure_dashboard["panels"], list), \
            "Dashboard 'panels' must be a list"
        assert len(infrastructure_dashboard["panels"]) > 0, \
            "Dashboard has no panels"

    def test_panels_have_required_fields(self, infrastructure_dashboard):
        """Test that all panels have required fields."""
        required_fields = ["id", "type", "title"]

        for panel in infrastructure_dashboard.get("panels", []):
            for field in required_fields:
                assert field in panel, \
                    f"Panel '{panel.get('title', 'unknown')}' missing field: {field}"

    def test_panels_have_datasource(self, infrastructure_dashboard):
        """Test that panels have datasource configuration."""
        for panel in infrastructure_dashboard.get("panels", []):
            panel_type = panel.get("type")
            # Skip text panels and other non-data panels
            if panel_type not in ["text", "stat"]:
                assert "datasource" in panel or "targets" in panel, \
                    f"Panel '{panel.get('title')}' missing datasource or targets"

    def test_dashboard_has_annotations(self, infrastructure_dashboard):
        """Test that dashboard has annotations configuration."""
        assert "annotations" in infrastructure_dashboard, \
            "Dashboard missing 'annotations' field"

    def test_infrastructure_dashboard_panels_count(self, infrastructure_dashboard):
        """Test that infrastructure dashboard has expected panels."""
        panels = infrastructure_dashboard.get("panels", [])
        # Should have CPU, Memory, Disk, Network panels
        assert len(panels) >= 4, \
            f"Infrastructure dashboard should have at least 4 panels, found {len(panels)}"

    def test_application_dashboard_panels_count(self, application_dashboard):
        """Test that application dashboard has expected panels."""
        panels = application_dashboard.get("panels", [])
        # Should have request rate, latency, error rate, availability panels
        assert len(panels) >= 4, \
            f"Application dashboard should have at least 4 panels, found {len(panels)}"

    def test_business_dashboard_panels_count(self, business_dashboard):
        """Test that business dashboard has expected panels."""
        panels = business_dashboard.get("panels", [])
        # Should have request rate, error rate, latency, uptime, connection pool panels
        assert len(panels) >= 5, \
            f"Business dashboard should have at least 5 panels, found {len(panels)}"

    def test_infrastructure_dashboard_has_cpu_panel(self, infrastructure_dashboard):
        """Test that infrastructure dashboard has CPU usage panel."""
        titles = [p.get("title") for p in infrastructure_dashboard.get("panels", [])]
        assert any("CPU" in title for title in titles), \
            "Infrastructure dashboard missing CPU usage panel"

    def test_infrastructure_dashboard_has_memory_panel(self, infrastructure_dashboard):
        """Test that infrastructure dashboard has memory usage panel."""
        titles = [p.get("title") for p in infrastructure_dashboard.get("panels", [])]
        assert any("Memory" in title for title in titles), \
            "Infrastructure dashboard missing Memory usage panel"

    def test_infrastructure_dashboard_has_disk_panel(self, infrastructure_dashboard):
        """Test that infrastructure dashboard has disk usage panel."""
        titles = [p.get("title") for p in infrastructure_dashboard.get("panels", [])]
        assert any("Disk" in title for title in titles), \
            "Infrastructure dashboard missing Disk usage panel"

    def test_application_dashboard_has_request_rate_panel(self, application_dashboard):
        """Test that application dashboard has request rate panel."""
        titles = [p.get("title") for p in application_dashboard.get("panels", [])]
        assert any("Request" in title or "Rate" in title for title in titles), \
            "Application dashboard missing Request Rate panel"

    def test_application_dashboard_has_error_rate_panel(self, application_dashboard):
        """Test that application dashboard has error rate panel."""
        titles = [p.get("title") for p in application_dashboard.get("panels", [])]
        assert any("Error" in title for title in titles), \
            "Application dashboard missing Error Rate panel"

    def test_application_dashboard_has_latency_panel(self, application_dashboard):
        """Test that application dashboard has latency/response time panel."""
        titles = [p.get("title") for p in application_dashboard.get("panels", [])]
        assert any("Response" in title or "Latency" in title or "Duration" in title for title in titles), \
            "Application dashboard missing Response/Latency panel"

    def test_business_dashboard_has_error_rate_panel(self, business_dashboard):
        """Test that business dashboard has error rate panel."""
        titles = [p.get("title") for p in business_dashboard.get("panels", [])]
        assert any("Error" in title for title in titles), \
            "Business dashboard missing Error Rate panel"

    def test_business_dashboard_has_request_rate_panel(self, business_dashboard):
        """Test that business dashboard has request rate panel."""
        titles = [p.get("title") for p in business_dashboard.get("panels", [])]
        assert any("Request" in title for title in titles), \
            "Business dashboard missing Request Rate panel"

    def test_business_dashboard_has_latency_panel(self, business_dashboard):
        """Test that business dashboard has latency panel."""
        titles = [p.get("title") for p in business_dashboard.get("panels", [])]
        assert any("Latency" in title or "Response" in title for title in titles), \
            "Business dashboard missing Latency panel"

    def test_business_dashboard_has_connection_panel(self, business_dashboard):
        """Test that business dashboard has database connection panel."""
        titles = [p.get("title") for p in business_dashboard.get("panels", [])]
        assert any("Connection" in title or "Database" in title for title in titles), \
            "Business dashboard missing Database Connection panel"

    def test_dashboard_refresh_rate_configured(self, infrastructure_dashboard):
        """Test that dashboard has a refresh rate configured."""
        refresh = infrastructure_dashboard.get("refresh")
        assert refresh is not None and len(str(refresh)) > 0, \
            "Dashboard missing or empty refresh rate"

    def test_dashboard_time_range_configured(self, infrastructure_dashboard):
        """Test that dashboard has a default time range."""
        time_config = infrastructure_dashboard.get("time")
        assert time_config is not None, "Dashboard missing 'time' configuration"
        assert "from" in time_config and "to" in time_config, \
            "Dashboard 'time' configuration incomplete"

    def test_dashboard_tags_configured(self, infrastructure_dashboard, application_dashboard,
                                       business_dashboard):
        """Test that dashboards have tags for organization."""
        dashboards = {
            "Infrastructure": infrastructure_dashboard,
            "Application": application_dashboard,
            "Business": business_dashboard
        }

        for name, dashboard in dashboards.items():
            tags = dashboard.get("tags", [])
            assert isinstance(tags, list) and len(tags) > 0, \
                f"{name} dashboard should have tags"

    def test_dashboard_uid_unique(self, infrastructure_dashboard, application_dashboard,
                                   business_dashboard):
        """Test that dashboards have unique UIDs."""
        dashboards = {
            "Infrastructure": infrastructure_dashboard,
            "Application": application_dashboard,
            "Business": business_dashboard
        }

        uids = []
        for name, dashboard in dashboards.items():
            uid = dashboard.get("uid")
            assert uid is not None and len(str(uid)) > 0, \
                f"{name} dashboard missing or empty UID"
            uids.append(uid)

        # Check for duplicates
        assert len(uids) == len(set(uids)), \
            f"Duplicate UIDs found: {[uid for uid in uids if uids.count(uid) > 1]}"

    def test_panel_types_are_valid(self, infrastructure_dashboard):
        """Test that panel types are valid Grafana types."""
        valid_types = [
            "timeseries", "graph", "gauge", "stat", "table", "piechart",
            "text", "alertlist", "dashlist", "row", "worldmap-panel"
        ]

        for panel in infrastructure_dashboard.get("panels", []):
            panel_type = panel.get("type")
            assert panel_type in valid_types, \
                f"Panel '{panel.get('title')}' has invalid type: {panel_type}"

    def test_panel_targets_have_expressions(self, infrastructure_dashboard):
        """Test that time series panels have Prometheus expressions."""
        for panel in infrastructure_dashboard.get("panels", []):
            if panel.get("type") in ["timeseries", "graph"]:
                targets = panel.get("targets", [])
                assert len(targets) > 0, \
                    f"Panel '{panel.get('title')}' has no targets"

                for target in targets:
                    # Should have either 'expr' (Prometheus) or 'query'
                    has_query = "expr" in target or "query" in target
                    assert has_query, \
                        f"Target in '{panel.get('title')}' missing expr or query"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
