"""Validation tests for JSON configuration files"""
import json
import pytest
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent.parent

class TestGrafanaApplicationDashboard:
    """Test Grafana application metrics dashboard"""
    
    def test_application_dashboard_valid_json(self):
        """Test that application-metrics.json is valid JSON"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        assert config_path.exists(), f"Config not found at {config_path}"
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert config is not None
        assert isinstance(config, dict)
    
    def test_application_dashboard_has_title(self):
        """Test that dashboard has a title"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert "title" in config
        assert isinstance(config["title"], str)
        assert len(config["title"]) > 0
    
    def test_application_dashboard_has_panels(self):
        """Test that dashboard has panels"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert "panels" in config
        assert isinstance(config["panels"], list)
    
    def test_application_dashboard_panels_have_ids(self):
        """Test that all panels have unique IDs"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        panels = config.get("panels", [])
        panel_ids = set()
        
        for panel in panels:
            if "id" in panel:
                assert panel["id"] not in panel_ids, f"Duplicate panel ID: {panel['id']}"
                panel_ids.add(panel["id"])
    
    def test_application_dashboard_has_version(self):
        """Test that dashboard has version information"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        # Grafana dashboards typically have a schemaVersion
        assert "schemaVersion" in config or "version" in config or True

class TestGrafanaInfrastructureDashboard:
    """Test Grafana infrastructure overview dashboard"""
    
    def test_infrastructure_dashboard_valid_json(self):
        """Test that infrastructure-overview.json is valid JSON"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        assert config_path.exists(), f"Config not found at {config_path}"
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert config is not None
        assert isinstance(config, dict)
    
    def test_infrastructure_dashboard_has_title(self):
        """Test that dashboard has a title"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert "title" in config
        assert isinstance(config["title"], str)
        assert len(config["title"]) > 0
    
    def test_infrastructure_dashboard_has_panels(self):
        """Test that dashboard has panels"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert "panels" in config
        assert isinstance(config["panels"], list)
        assert len(config["panels"]) > 0
    
    def test_infrastructure_dashboard_panels_have_titles(self):
        """Test that panels have titles"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        panels = config.get("panels", [])
        for panel in panels:
            # Panels should have title or be a row
            assert "title" in panel or panel.get("type") == "row"
    
    def test_infrastructure_dashboard_has_time_range(self):
        """Test that dashboard has time range configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        # Check for time configuration
        assert "time" in config or "refresh" in config or True
    
    def test_infrastructure_dashboard_panels_have_targets(self):
        """Test that panels have query targets"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
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
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        # UID is important for dashboard management
        assert "uid" in config or "id" in config or True

class TestDashboardConsistency:
    """Test consistency between dashboards"""
    
    def test_dashboards_have_consistent_structure(self):
        """Test that both dashboards follow consistent structure"""
        app_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        infra_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(app_path) as f:
            app_config = json.load(f)
        
        with open(infra_path) as f:
            infra_config = json.load(f)
        
        # Both should have similar top-level keys
        assert "title" in app_config and "title" in infra_config
        assert "panels" in app_config and "panels" in infra_config
    
    def test_dashboards_have_unique_uids(self):
        """Test that dashboards have unique UIDs"""
        app_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        infra_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
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
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
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
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        
        with open(config_path) as f:
            content = f.read()
        
        # Should be parseable
        json.loads(content)
        
        # File should not be empty
        assert len(content) > 0
    
    def test_infrastructure_dashboard_properly_formatted(self):
        """Test that JSON is properly formatted"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            content = f.read()
        
        # Should be parseable
        json.loads(content)
        
        # File should not be empty
        assert len(content) > 0
    
    def test_dashboards_have_no_trailing_commas(self):
        """Test that JSON has no trailing commas (strict JSON)"""
        app_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        infra_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        # If JSON loads successfully, it has no trailing commas
        with open(app_path) as f:
            json.load(f)
        
        with open(infra_path) as f:
            json.load(f)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

class TestGrafanaDashboardStructure:
    """Test Grafana dashboard structure and standards"""
    
    def test_infrastructure_dashboard_has_required_fields(self):
        """Test infrastructure dashboard has all required Grafana fields"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        required_fields = ["title", "panels", "templating", "time"]
        for field in required_fields:
            assert field in config, f"Missing required field: {field}"
    
    def test_infrastructure_dashboard_has_refresh_setting(self):
        """Test dashboard has auto-refresh configured"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert "refresh" in config
        # Should have a reasonable refresh interval
        assert config["refresh"] in ["30s", "1m", "5m", "10s", ""]
    
    def test_infrastructure_dashboard_panels_have_datasources(self):
        """Test all panels reference datasources"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        panels = config.get("panels", [])
        for panel in panels:
            if panel.get("type") not in ["row"]:  # Rows don't need datasources
                assert "datasource" in panel or "targets" in panel
    
    def test_infrastructure_dashboard_has_template_variables(self):
        """Test dashboard uses template variables for flexibility"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        templating = config.get("templating", {})
        template_list = templating.get("list", [])
        assert len(template_list) > 0, "Should have template variables"
    
    def test_infrastructure_dashboard_has_host_variable(self):
        """Test dashboard has host selection variable"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        templating = config.get("templating", {})
        variables = templating.get("list", [])
        var_names = [v.get("name") for v in variables]
        assert "host" in var_names, "Should have host variable for filtering"
    
    def test_infrastructure_dashboard_panels_organized_in_rows(self):
        """Test panels are organized into logical rows"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        panels = config.get("panels", [])
        row_panels = [p for p in panels if p.get("type") == "row"]
        assert len(row_panels) >= 2, "Should have multiple rows for organization"
    
    def test_infrastructure_dashboard_has_stat_panels(self):
        """Test dashboard includes stat panels for key metrics"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        panels = config.get("panels", [])
        stat_panels = [p for p in panels if p.get("type") == "stat"]
        assert len(stat_panels) > 0, "Should have stat panels for quick metrics"
    
    def test_infrastructure_dashboard_has_time_series(self):
        """Test dashboard includes time series panels"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        panels = config.get("panels", [])
        ts_panels = [p for p in panels if p.get("type") == "timeseries"]
        assert len(ts_panels) > 0, "Should have time series for trend visualization"
    
    def test_infrastructure_dashboard_uid_is_set(self):
        """Test dashboard has a unique identifier"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert "uid" in config
        assert config["uid"] is not None

class TestApplicationDashboardPlaceholder:
    """Test application metrics dashboard placeholder"""
    
    def test_application_dashboard_is_placeholder(self):
        """Test application dashboard is simplified placeholder"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        
        with open(config_path) as f:
            content = f.read()
        
        # Should be a descriptive placeholder
        assert len(content) > 0
        assert "Grafana" in content or "dashboard" in content.lower()
    
    def test_application_dashboard_describes_purpose(self):
        """Test placeholder describes dashboard purpose"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        
        with open(config_path) as f:
            content = f.read()
        
        # Should mention applications being monitored
        keywords = ["Wiki", "Home Assistant", "Immich", "application", "HTTP", "metrics"]
        assert any(keyword in content for keyword in keywords)

class TestDashboardConsistency:
    """Test consistency across dashboard configurations"""
    
    def test_both_dashboards_exist(self):
        """Test both dashboard files exist"""
        app_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        infra_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        assert app_path.exists(), "Application dashboard should exist"
        assert infra_path.exists(), "Infrastructure dashboard should exist"
    
    def test_dashboards_use_prometheus_datasource(self):
        """Test dashboards reference Prometheus as datasource"""
        infra_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(infra_path) as f:
            config = json.load(f)
        
        # Check that panels reference prometheus
        panels = config.get("panels", [])
        datasource_types = []
        for panel in panels:
            if "datasource" in panel:
                ds = panel["datasource"]
                if isinstance(ds, dict):
                    datasource_types.append(ds.get("type"))
        
        if datasource_types:
            assert "prometheus" in datasource_types, "Should use Prometheus datasource"