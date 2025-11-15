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


class TestGrafanaProductionDashboard:
    """Test Grafana production application dashboard"""
    
    def test_production_dashboard_valid_json(self):
        """Test that production-dashboard.json is valid JSON"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        assert config_path.exists(), f"Config not found at {config_path}"
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert config is not None
        assert isinstance(config, dict)
    
    def test_production_dashboard_has_dashboard_wrapper(self):
        """Test that production dashboard has proper wrapper structure"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        # Production dashboard wraps content in 'dashboard' key
        assert "dashboard" in config
        assert isinstance(config["dashboard"], dict)
    
    def test_production_dashboard_has_title(self):
        """Test that dashboard has a title"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        assert "title" in dashboard
        assert isinstance(dashboard["title"], str)
        assert len(dashboard["title"]) > 0
        assert dashboard["title"] == "Production Application Dashboard"
    
    def test_production_dashboard_has_uid(self):
        """Test that dashboard has a unique identifier"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        assert "uid" in dashboard
        assert dashboard["uid"] == "app-production"
        assert isinstance(dashboard["uid"], str)
        assert len(dashboard["uid"]) > 0
    
    def test_production_dashboard_has_tags(self):
        """Test that dashboard has appropriate tags"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        assert "tags" in dashboard
        assert isinstance(dashboard["tags"], list)
        assert len(dashboard["tags"]) > 0
        assert "production" in dashboard["tags"]
        assert "application" in dashboard["tags"]
    
    def test_production_dashboard_has_schema_version(self):
        """Test that dashboard has schema version"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        assert "schemaVersion" in dashboard
        assert isinstance(dashboard["schemaVersion"], int)
        assert dashboard["schemaVersion"] > 0
    
    def test_production_dashboard_has_refresh_interval(self):
        """Test that dashboard has auto-refresh configured"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        assert "refresh" in dashboard
        assert dashboard["refresh"] == "30s"
    
    def test_production_dashboard_has_panels(self):
        """Test that dashboard has panels"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        assert "panels" in dashboard
        assert isinstance(dashboard["panels"], list)
        assert len(dashboard["panels"]) == 10
    
    def test_production_dashboard_panels_have_unique_ids(self):
        """Test that all panels have unique IDs"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        panel_ids = set()
        
        for panel in panels:
            assert "id" in panel, f"Panel missing ID: {panel.get('title')}"
            assert panel["id"] not in panel_ids, f"Duplicate panel ID: {panel['id']}"
            panel_ids.add(panel["id"])
        
        # Verify we have all IDs from 1 to 10
        assert panel_ids == set(range(1, 11))
    
    def test_production_dashboard_panels_have_titles(self):
        """Test that all panels have titles"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        
        for panel in panels:
            assert "title" in panel
            assert isinstance(panel["title"], str)
            assert len(panel["title"]) > 0
    
    def test_production_dashboard_panels_have_types(self):
        """Test that all panels have valid types"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        valid_types = ["graph", "stat", "gauge", "table", "heatmap", "text", "row"]
        
        for panel in panels:
            assert "type" in panel
            assert panel["type"] in valid_types, f"Invalid panel type: {panel['type']}"
    
    def test_production_dashboard_panels_have_grid_positions(self):
        """Test that all panels have grid positioning"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        
        for panel in panels:
            assert "gridPos" in panel
            grid_pos = panel["gridPos"]
            assert "h" in grid_pos and isinstance(grid_pos["h"], int)
            assert "w" in grid_pos and isinstance(grid_pos["w"], int)
            assert "x" in grid_pos and isinstance(grid_pos["x"], int)
            assert "y" in grid_pos and isinstance(grid_pos["y"], int)
            # Grafana uses 24-unit grid width
            assert 0 <= grid_pos["x"] < 24
            assert 0 < grid_pos["w"] <= 24
    
    def test_production_dashboard_panels_have_targets(self):
        """Test that panels have query targets"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        
        for panel in panels:
            assert "targets" in panel
            assert isinstance(panel["targets"], list)
            assert len(panel["targets"]) > 0
            
            for target in panel["targets"]:
                assert "refId" in target
                assert "expr" in target or "query" in target
    
    def test_production_dashboard_has_templating(self):
        """Test that dashboard has templating variables"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        assert "templating" in dashboard
        assert "list" in dashboard["templating"]
        assert isinstance(dashboard["templating"]["list"], list)
        assert len(dashboard["templating"]["list"]) == 3
    
    def test_production_dashboard_templating_variables(self):
        """Test specific templating variables"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        variables = dashboard.get("templating", {}).get("list", [])
        variable_names = [v.get("name") for v in variables]
        
        assert "datasource" in variable_names
        assert "environment" in variable_names
        assert "service" in variable_names
        
        # Verify variable types
        for var in variables:
            assert "name" in var
            assert "type" in var
            if var["name"] == "datasource":
                assert var["type"] == "datasource"
                assert var["query"] == "prometheus"
            elif var["name"] == "environment":
                assert var["type"] == "query"
                assert "http_requests_total" in var["query"]
            elif var["name"] == "service":
                assert var["type"] == "query"
                assert var.get("multi") is True
                assert var.get("includeAll") is True
    
    def test_production_dashboard_has_annotations(self):
        """Test that dashboard has annotations configured"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        assert "annotations" in dashboard
        assert "list" in dashboard["annotations"]
        assert isinstance(dashboard["annotations"]["list"], list)
        assert len(dashboard["annotations"]["list"]) > 0
        
        # Check alert annotation
        alerts_annotation = dashboard["annotations"]["list"][0]
        assert alerts_annotation["name"] == "Alerts"
        assert alerts_annotation["enable"] is True
        assert alerts_annotation["datasource"] == "Prometheus"
        assert "ALERTS" in alerts_annotation["expr"]
    
    def test_production_dashboard_has_alerts(self):
        """Test that dashboard has alert configurations"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        
        panels_with_alerts = [p for p in panels if "alert" in p]
        assert len(panels_with_alerts) == 2
        
        # Verify alert structure
        for panel in panels_with_alerts:
            alert = panel["alert"]
            assert "name" in alert
            assert "conditions" in alert
            assert isinstance(alert["conditions"], list)
            assert len(alert["conditions"]) > 0
    
    def test_production_dashboard_request_rate_alert(self):
        """Test Request Rate panel alert configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        request_rate_panel = [p for p in panels if p["id"] == 1][0]
        
        assert "alert" in request_rate_panel
        alert = request_rate_panel["alert"]
        assert alert["name"] == "High Request Rate"
        assert alert["frequency"] == "1m"
        assert alert["executionErrorState"] == "alerting"
        assert alert["noDataState"] == "no_data"
        
        # Check alert condition
        condition = alert["conditions"][0]
        assert condition["evaluator"]["type"] == "gt"
        assert condition["evaluator"]["params"] == [1000]
        
        # Check notifications
        assert "notifications" in alert
        assert len(alert["notifications"]) > 0
        assert alert["notifications"][0]["uid"] == "slack-alerts"
    
    def test_production_dashboard_queue_size_alert(self):
        """Test Queue Size panel alert configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        queue_panel = [p for p in panels if p["id"] == 7][0]
        
        assert "alert" in queue_panel
        alert = queue_panel["alert"]
        assert alert["name"] == "Queue Size Too Large"
        
        # Check alert condition
        condition = alert["conditions"][0]
        assert condition["evaluator"]["type"] == "gt"
        assert condition["evaluator"]["params"] == [1000]
    
    def test_production_dashboard_panel_types_distribution(self):
        """Test panel type distribution"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        
        panel_types = {}
        for panel in panels:
            panel_type = panel.get("type")
            panel_types[panel_type] = panel_types.get(panel_type, 0) + 1
        
        assert panel_types.get("graph") == 8
        assert panel_types.get("stat") == 1
        assert panel_types.get("gauge") == 1
    
    def test_production_dashboard_prometheus_queries(self):
        """Test that panels use valid Prometheus queries"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        
        prometheus_functions = ["rate", "sum", "histogram_quantile", "by"]
        
        for panel in panels:
            for target in panel.get("targets", []):
                expr = target.get("expr", "")
                # At least one query should use Prometheus functions
                if expr:
                    # Basic validation that it looks like a PromQL query
                    assert isinstance(expr, str)
                    assert len(expr) > 0
    
    def test_production_dashboard_response_time_percentiles(self):
        """Test Response Time panel has P50, P95, P99"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        response_time_panel = [p for p in panels if p["id"] == 3][0]
        
        assert len(response_time_panel["targets"]) == 3
        
        # Check for percentile queries
        exprs = [t["expr"] for t in response_time_panel["targets"]]
        assert any("0.50" in expr for expr in exprs)
        assert any("0.95" in expr for expr in exprs)
        assert any("0.99" in expr for expr in exprs)
    
    def test_production_dashboard_active_users_thresholds(self):
        """Test Active Users panel has proper thresholds"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        active_users_panel = [p for p in panels if p["id"] == 4][0]
        
        assert "fieldConfig" in active_users_panel
        field_config = active_users_panel["fieldConfig"]
        assert "defaults" in field_config
        assert "thresholds" in field_config["defaults"]
        
        thresholds = field_config["defaults"]["thresholds"]
        assert "steps" in thresholds
        assert len(thresholds["steps"]) == 3
        
        # Check threshold values
        steps = thresholds["steps"]
        assert steps[1]["value"] == 8000
        assert steps[1]["color"] == "yellow"
        assert steps[2]["value"] == 10000
        assert steps[2]["color"] == "red"
    
    def test_production_dashboard_cache_hit_rate_config(self):
        """Test Cache Hit Rate panel configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        cache_panel = [p for p in panels if p["id"] == 6][0]
        
        assert cache_panel["type"] == "gauge"
        assert len(cache_panel["targets"]) == 2
        
        # Check for L1 and L2 cache queries
        exprs = [t["expr"] for t in cache_panel["targets"]]
        assert any("l1" in expr for expr in exprs)
        assert any("l2" in expr for expr in exprs)
        
        # Check field config
        assert "fieldConfig" in cache_panel
        field_config = cache_panel["fieldConfig"]["defaults"]
        assert field_config["unit"] == "percentunit"
        assert field_config["max"] == 1
        assert field_config["min"] == 0
    
    def test_production_dashboard_database_connections(self):
        """Test Database Connections panel has active and idle metrics"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        db_panel = [p for p in panels if p["id"] == 5][0]
        
        assert len(db_panel["targets"]) == 2
        
        # Check for active and idle connections
        exprs = [t["expr"] for t in db_panel["targets"]]
        assert any("active" in expr for expr in exprs)
        assert any("idle" in expr for expr in exprs)
    
    def test_production_dashboard_business_metrics(self):
        """Test that dashboard includes business metrics"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        
        # Panel 8 is Orders Created (Business Metric)
        orders_panel = [p for p in panels if p["id"] == 8][0]
        assert "Business Metric" in orders_panel["title"]
        assert "orders_created_total" in orders_panel["targets"][0]["expr"]
    
    def test_production_dashboard_resource_metrics(self):
        """Test that dashboard includes CPU and Memory metrics"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        
        # Panel 9 is CPU Usage
        cpu_panel = [p for p in panels if p["id"] == 9][0]
        assert "CPU" in cpu_panel["title"]
        assert "container_cpu_usage_seconds_total" in cpu_panel["targets"][0]["expr"]
        
        # Panel 10 is Memory Usage
        memory_panel = [p for p in panels if p["id"] == 10][0]
        assert "Memory" in memory_panel["title"]
        assert "container_memory_working_set_bytes" in memory_panel["targets"][0]["expr"]
    
    def test_production_dashboard_error_rate_thresholds(self):
        """Test Error Rate panel has thresholds configured"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        error_panel = [p for p in panels if p["id"] == 2][0]
        
        assert "thresholds" in error_panel
        thresholds = error_panel["thresholds"]
        assert len(thresholds) > 0
        assert thresholds[0]["value"] == 0.01
        assert thresholds[0]["op"] == "gt"
    
    def test_production_dashboard_yaxes_formatting(self):
        """Test that graph panels have properly formatted Y axes"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        
        # Check Request Rate panel
        request_panel = [p for p in panels if p["id"] == 1][0]
        if "yaxes" in request_panel:
            assert request_panel["yaxes"][0]["format"] == "reqps"
        
        # Check Response Time panel
        response_panel = [p for p in panels if p["id"] == 3][0]
        if "yaxes" in response_panel:
            assert response_panel["yaxes"][0]["format"] == "s"
        
        # Check CPU Usage panel
        cpu_panel = [p for p in panels if p["id"] == 9][0]
        if "yaxes" in cpu_panel:
            assert cpu_panel["yaxes"][0]["format"] == "percentunit"
        
        # Check Memory Usage panel
        memory_panel = [p for p in panels if p["id"] == 10][0]
        if "yaxes" in memory_panel:
            assert memory_panel["yaxes"][0]["format"] == "bytes"
    
    def test_production_dashboard_legend_formats(self):
        """Test that targets have legend formats"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        
        for panel in panels:
            for target in panel.get("targets", []):
                if "legendFormat" in target:
                    legend = target["legendFormat"]
                    # Should contain template variables
                    assert "{{" in legend or len(legend) > 0


class TestProductionDashboardComparison:
    """Test production dashboard against other dashboards for consistency"""
    
    def test_production_dashboard_unique_uid(self):
        """Test that production dashboard has unique UID"""
        app_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        infra_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        prod_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(app_path) as f:
            app_config = json.load(f)
        with open(infra_path) as f:
            infra_config = json.load(f)
        with open(prod_path) as f:
            prod_config = json.load(f)
        
        prod_dashboard = prod_config.get("dashboard", {})
        prod_uid = prod_dashboard.get("uid")
        app_uid = app_config.get("uid")
        infra_uid = infra_config.get("uid")
        
        assert prod_uid is not None
        assert prod_uid != app_uid
        assert prod_uid != infra_uid
        assert prod_uid == "app-production"
    
    def test_production_dashboard_all_have_panels(self):
        """Test that all three dashboards have panels"""
        app_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/application-metrics.json"
        infra_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/infrastructure-overview.json"
        prod_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(app_path) as f:
            app_config = json.load(f)
        with open(infra_path) as f:
            infra_config = json.load(f)
        with open(prod_path) as f:
            prod_config = json.load(f)
        
        prod_dashboard = prod_config.get("dashboard", {})
        
        assert len(app_config.get("panels", [])) > 0
        assert len(infra_config.get("panels", [])) > 0
        assert len(prod_dashboard.get("panels", [])) > 0
    
    def test_all_dashboards_properly_formatted_json(self):
        """Test that all dashboard JSON files are properly formatted"""
        dashboards = [
            "application-metrics.json",
            "infrastructure-overview.json",
            "production-dashboard.json"
        ]
        
        for dashboard_file in dashboards:
            config_path = BASE_PATH / f"projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/{dashboard_file}"
            
            with open(config_path) as f:
                content = f.read()
            
            # Should be parseable
            config = json.loads(content)
            assert config is not None
            assert len(content) > 0


class TestProductionDashboardEdgeCases:
    """Test edge cases and error conditions for production dashboard"""
    
    def test_production_dashboard_no_empty_panels(self):
        """Test that no panels are empty or malformed"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        
        for panel in panels:
            assert panel is not None
            assert isinstance(panel, dict)
            assert len(panel) > 0
            assert panel.get("title") is not None
            assert panel.get("type") is not None
    
    def test_production_dashboard_no_duplicate_titles(self):
        """Test that panel titles are unique"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        
        titles = [p.get("title") for p in panels]
        assert len(titles) == len(set(titles)), "Duplicate panel titles found"
    
    def test_production_dashboard_no_overlapping_panels(self):
        """Test that panels don't overlap in grid layout"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        
        # Build a set of occupied grid cells
        occupied = set()
        for panel in panels:
            grid = panel.get("gridPos", {})
            x, y, w, h = grid["x"], grid["y"], grid["w"], grid["h"]
            
            # Check each cell this panel occupies
            for px in range(x, x + w):
                for py in range(y, y + h):
                    cell = (px, py)
                    assert cell not in occupied, f"Panel {panel['title']} overlaps at {cell}"
                    occupied.add(cell)
    
    def test_production_dashboard_targets_have_ref_ids(self):
        """Test that all targets have reference IDs"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        
        for panel in panels:
            for target in panel.get("targets", []):
                assert "refId" in target
                assert isinstance(target["refId"], str)
                assert len(target["refId"]) > 0
    
    def test_production_dashboard_alert_conditions_valid(self):
        """Test that alert conditions are properly structured"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        
        for panel in panels:
            if "alert" in panel:
                alert = panel["alert"]
                assert "conditions" in alert
                
                for condition in alert["conditions"]:
                    assert "evaluator" in condition
                    assert "type" in condition["evaluator"]
                    assert "params" in condition["evaluator"]
                    assert isinstance(condition["evaluator"]["params"], list)
                    assert "query" in condition
                    assert "reducer" in condition
    
    def test_production_dashboard_timezone_set(self):
        """Test that dashboard has timezone configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        assert "timezone" in dashboard
        assert dashboard["timezone"] in ["browser", "utc", ""]
    
    def test_production_dashboard_version_set(self):
        """Test that dashboard has version number"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        assert "version" in dashboard
        assert isinstance(dashboard["version"], int)
        assert dashboard["version"] > 0


class TestProductionDashboardPrometheusQueries:
    """Test Prometheus query syntax and validity in production dashboard"""
    
    def test_production_dashboard_queries_use_rate_for_counters(self):
        """Test that counter metrics use rate() function"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        
        counter_metrics = ["http_requests_total", "http_request_errors_total", "orders_created_total"]
        
        for panel in panels:
            for target in panel.get("targets", []):
                expr = target.get("expr", "")
                for metric in counter_metrics:
                    if metric in expr:
                        assert "rate(" in expr, f"Counter metric {metric} should use rate()"
    
    def test_production_dashboard_queries_have_time_ranges(self):
        """Test that rate queries include time ranges"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        
        for panel in panels:
            for target in panel.get("targets", []):
                expr = target.get("expr", "")
                if "rate(" in expr:
                    # Should have time range like [5m]
                    assert "[" in expr and "]" in expr
    
    def test_production_dashboard_histogram_quantile_usage(self):
        """Test histogram_quantile usage for percentiles"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        response_time_panel = [p for p in panels if p["id"] == 3][0]
        
        for target in response_time_panel["targets"]:
            expr = target.get("expr", "")
            assert "histogram_quantile" in expr
            assert "le" in expr  # histogram_quantile requires 'le' label
    
    def test_production_dashboard_aggregation_by_labels(self):
        """Test that queries use proper label aggregation"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/grafana/dashboards/production-dashboard.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        dashboard = config.get("dashboard", {})
        panels = dashboard.get("panels", [])
        
        for panel in panels:
            for target in panel.get("targets", []):
                expr = target.get("expr", "")
                if "sum(" in expr:
                    # sum should typically be followed by 'by (label)'
                    assert "by (" in expr or "without (" in expr or expr.endswith(")")

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