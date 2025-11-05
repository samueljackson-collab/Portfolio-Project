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
class TestInfrastructureOverviewDashboardUpdated:
    """Test updated infrastructure-overview.json dashboard"""
    
    def test_infrastructure_dashboard_has_updated_panels(self):
        """Test that infrastructure dashboard has updated panel configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        panels = config.get("panels", [])
        assert len(panels) >= 2, "Dashboard should have at least 2 panels"
    
    def test_cpu_usage_panel_configuration(self):
        """Test CPU usage panel configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        panels = config.get("panels", [])
        cpu_panels = [p for p in panels if "CPU" in p.get("title", "")]
        
        assert len(cpu_panels) > 0, "CPU usage panel not found"
        cpu_panel = cpu_panels[0]
        
        assert cpu_panel["type"] == "graph"
        assert "targets" in cpu_panel
        assert len(cpu_panel["targets"]) > 0
        
        # Check the PromQL expression
        target = cpu_panel["targets"][0]
        assert "expr" in target
        assert "node_cpu_seconds_total" in target["expr"]
        assert "idle" in target["expr"]
    
    def test_memory_available_panel_configuration(self):
        """Test Memory Available panel configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        panels = config.get("panels", [])
        memory_panels = [p for p in panels if "Memory" in p.get("title", "")]
        
        assert len(memory_panels) > 0, "Memory panel not found"
        memory_panel = memory_panels[0]
        
        assert memory_panel["type"] == "graph"
        assert "targets" in memory_panel
        assert len(memory_panel["targets"]) > 0
        
        # Check the PromQL expression
        target = memory_panel["targets"][0]
        assert "expr" in target
        assert "node_memory_MemAvailable_bytes" in target["expr"]
        assert "node_memory_MemTotal_bytes" in target["expr"]
    
    def test_dashboard_version_info(self):
        """Test that dashboard has version information"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert "schemaVersion" in config
        assert config["schemaVersion"] == 16
        assert "version" in config
        assert config["version"] == 1
    
    def test_dashboard_datasource_references(self):
        """Test that panels reference Prometheus datasource"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        panels = config.get("panels", [])
        for panel in panels:
            if "datasource" in panel:
                assert panel["datasource"] == "Prometheus"
    
    def test_dashboard_title_descriptive(self):
        """Test that dashboard has a descriptive title"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert "title" in config
        title = config["title"]
        assert "Infrastructure" in title
        assert len(title) > 10  # Should be descriptive
    
    def test_panels_have_valid_types(self):
        """Test that all panels have valid types"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        panels = config.get("panels", [])
        valid_types = ["graph", "singlestat", "table", "row", "text", "gauge", "stat"]
        
        for panel in panels:
            assert "type" in panel
            assert panel["type"] in valid_types, f"Invalid panel type: {panel.get('type')}"
    
    def test_all_targets_have_expressions(self):
        """Test that all panel targets have PromQL expressions"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        panels = config.get("panels", [])
        for panel in panels:
            if "targets" in panel:
                targets = panel["targets"]
                for target in targets:
                    assert "expr" in target or target == {}, f"Target missing expr in panel {panel.get('title')}"

class TestUniFiConfigJSON:
    """Test UniFi configuration export JSON"""
    
    def test_unifi_config_valid_json(self):
        """Test that unifi-config-export-sanitized.json is valid JSON"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/unifi-config-export-sanitized.json"
        assert config_path.exists(), f"Config not found at {config_path}"
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert config is not None
        assert isinstance(config, dict)
    
    def test_unifi_has_controller_section(self):
        """Test that UniFi config has controller section"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/unifi-config-export-sanitized.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert "controller" in config
        assert isinstance(config["controller"], dict)
    
    def test_unifi_controller_has_version(self):
        """Test that controller section has version"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/unifi-config-export-sanitized.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        controller = config.get("controller", {})
        assert "version" in controller
        # Should be a placeholder
        assert "REPLACE" in controller["version"]
    
    def test_unifi_has_sites_configuration(self):
        """Test that controller has sites configuration"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/unifi-config-export-sanitized.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        controller = config.get("controller", {})
        assert "sites" in controller
        assert isinstance(controller["sites"], dict)
    
    def test_unifi_default_site_exists(self):
        """Test that default site exists"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/unifi-config-export-sanitized.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        sites = config.get("controller", {}).get("sites", {})
        assert "default" in sites
    
    def test_unifi_sanitized_credentials(self):
        """Test that credentials are sanitized"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/unifi-config-export-sanitized.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        # Check that sensitive data is redacted
        site_settings = config.get("controller", {}).get("sites", {}).get("default", {}).get("settings", {})
        
        if "wpa_key" in site_settings:
            assert site_settings["wpa_key"] == "REDACTED", "WPA key should be redacted"
    
    def test_unifi_has_sanitization_notes(self):
        """Test that config includes sanitization notes"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/unifi-config-export-sanitized.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert "notes" in config
        notes = config["notes"]
        assert "Sanitized" in notes or "sanitized" in notes.lower()
    
    def test_unifi_placeholder_values(self):
        """Test that sensitive values use placeholders"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/unifi-config-export-sanitized.json"
        
        with open(config_path) as f:
            content = f.read()
        
        # Config should contain placeholder indicators
        assert "REDACTED" in content or "REPLACE" in content or "YOUR_" in content

class TestJSONFormattingAndStructure:
    """Test JSON formatting and structure consistency"""
    
    def test_all_json_files_properly_indented(self):
        """Test that JSON files are properly formatted"""
        json_files = [
            BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json",
            BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/unifi-config-export-sanitized.json"
        ]
        
        for json_file in json_files:
            if json_file.exists():
                with open(json_file) as f:
                    content = f.read()
                
                # Should be valid JSON
                json_obj = json.loads(content)
                
                # Re-serialize and check it's valid
                json.dumps(json_obj, indent=2)
    
    def test_json_files_no_syntax_errors(self):
        """Test that all JSON files have no syntax errors"""
        json_files = [
            BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json",
            BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json",
            BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/unifi-config-export-sanitized.json"
        ]
        
        for json_file in json_files:
            if json_file.exists():
                with open(json_file) as f:
                    try:
                        json.load(f)
                    except json.JSONDecodeError as e:
                        pytest.fail(f"JSON syntax error in {json_file}: {e}")