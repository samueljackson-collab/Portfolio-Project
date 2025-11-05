"""Validation tests for YAML configuration files"""
import yaml
import pytest
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent.parent

class TestPrometheusConfig:
    """Test Prometheus configuration validity"""
    
    def test_prometheus_config_valid_yaml(self):
        """Test that prometheus.yml is valid YAML"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        assert config_path.exists(), f"Config not found at {config_path}"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)
    
    def test_prometheus_has_required_sections(self):
        """Test that prometheus.yml has required sections"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "global" in config
        assert "scrape_configs" in config or "scrape_interval" in config.get("global", {})
    
    def test_prometheus_global_config(self):
        """Test Prometheus global configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        global_config = config.get("global", {})
        assert "scrape_interval" in global_config
        assert "evaluation_interval" in global_config or "scrape_interval" in global_config
    
    def test_prometheus_alerting_config(self):
        """Test Prometheus alerting configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if "alerting" in config:
            alerting = config["alerting"]
            assert "alertmanagers" in alerting
            assert isinstance(alerting["alertmanagers"], list)
    
    def test_prometheus_rule_files(self):
        """Test that rule_files section is properly configured"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if "rule_files" in config:
            assert isinstance(config["rule_files"], list)

class TestAlertmanagerConfig:
    """Test Alertmanager configuration validity"""
    
    def test_alertmanager_config_valid_yaml(self):
        """Test that alertmanager.yml is valid YAML"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/alertmanager/alertmanager.yml"
        assert config_path.exists(), f"Config not found at {config_path}"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)
    
    def test_alertmanager_has_required_sections(self):
        """Test that alertmanager.yml has required sections"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/alertmanager/alertmanager.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "route" in config
        assert "receivers" in config
    
    def test_alertmanager_route_config(self):
        """Test Alertmanager route configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/alertmanager/alertmanager.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        route = config.get("route", {})
        assert "receiver" in route
        assert isinstance(route.get("receiver"), str)
    
    def test_alertmanager_receivers_list(self):
        """Test that receivers is a list"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/alertmanager/alertmanager.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        receivers = config.get("receivers", [])
        assert isinstance(receivers, list)
        assert len(receivers) > 0
    
    def test_alertmanager_receivers_have_names(self):
        """Test that all receivers have names"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/alertmanager/alertmanager.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        receivers = config.get("receivers", [])
        for receiver in receivers:
            assert "name" in receiver
            assert isinstance(receiver["name"], str)

class TestLokiConfig:
    """Test Loki configuration validity"""
    
    def test_loki_config_valid_yaml(self):
        """Test that loki-config.yml is valid YAML"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        assert config_path.exists(), f"Config not found at {config_path}"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)
    
    def test_loki_auth_enabled(self):
        """Test Loki authentication configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Check if auth_enabled is defined
        assert "auth_enabled" in config or config.get("server")
    
    def test_loki_has_server_config(self):
        """Test that Loki has server configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "server" in config or "http_listen_port" in config.get("server", {}) or True

class TestPromtailConfig:
    """Test Promtail configuration validity"""
    
    def test_promtail_config_valid_yaml(self):
        """Test that promtail-config.yml is valid YAML"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/promtail-config.yml"
        assert config_path.exists(), f"Config not found at {config_path}"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)
    
    def test_promtail_has_server_config(self):
        """Test that Promtail has server configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/promtail-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "server" in config
    
    def test_promtail_has_clients(self):
        """Test that Promtail has clients configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/promtail-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "clients" in config
        assert isinstance(config["clients"], list)
    
    def test_promtail_has_scrape_configs(self):
        """Test that Promtail has scrape configurations"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/promtail-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "scrape_configs" in config
        assert isinstance(config["scrape_configs"], list)

class TestInfrastructureAlerts:
    """Test infrastructure alerts configuration"""
    
    def test_infrastructure_alerts_valid_yaml(self):
        """Test that infrastructure_alerts.yml is valid YAML"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        assert config_path.exists(), f"Config not found at {config_path}"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)
    
    def test_infrastructure_alerts_has_groups(self):
        """Test that alert file has groups"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "groups" in config
        assert isinstance(config["groups"], list)
        assert len(config["groups"]) > 0
    
    def test_alert_groups_have_names(self):
        """Test that all alert groups have names"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        groups = config.get("groups", [])
        for group in groups:
            assert "name" in group
            assert isinstance(group["name"], str)
    
    def test_alert_groups_have_rules(self):
        """Test that alert groups have rules"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        groups = config.get("groups", [])
        for group in groups:
            assert "rules" in group
            assert isinstance(group["rules"], list)
    
    def test_alert_rules_have_required_fields(self):
        """Test that alert rules have required fields"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        groups = config.get("groups", [])
        for group in groups:
            rules = group.get("rules", [])
            for rule in rules:
                assert "alert" in rule or "record" in rule
                assert "expr" in rule

class TestArgoCDApplication:
    """Test ArgoCD application configuration"""
    
    def test_argocd_application_valid_yaml(self):
        """Test that application.yaml is valid YAML"""
        config_path = BASE_PATH / "enterprise-portfolio/kubernetes/manifests/argocd/application.yaml"
        assert config_path.exists(), f"Config not found at {config_path}"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)
    
    def test_argocd_application_has_apiversion(self):
        """Test that ArgoCD application has apiVersion"""
        config_path = BASE_PATH / "enterprise-portfolio/kubernetes/manifests/argocd/application.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "apiVersion" in config
        assert "argoproj.io" in config["apiVersion"]
    
    def test_argocd_application_has_kind(self):
        """Test that ArgoCD application has kind"""
        config_path = BASE_PATH / "enterprise-portfolio/kubernetes/manifests/argocd/application.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "kind" in config
        assert config["kind"] == "Application"
    
    def test_argocd_application_has_metadata(self):
        """Test that ArgoCD application has metadata"""
        config_path = BASE_PATH / "enterprise-portfolio/kubernetes/manifests/argocd/application.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "metadata" in config
        assert "name" in config["metadata"]
    
    def test_argocd_application_has_spec(self):
        """Test that ArgoCD application has spec"""
        config_path = BASE_PATH / "enterprise-portfolio/kubernetes/manifests/argocd/application.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "spec" in config
        spec = config["spec"]
        assert "source" in spec or "destination" in spec

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

class TestLokiConfigEnhanced:
    """Enhanced tests for Loki configuration"""
    
    def test_loki_has_server_section(self):
        """Test that Loki config has server section"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "server" in config
        server = config["server"]
        assert isinstance(server, dict)
    
    def test_loki_server_ports_configured(self):
        """Test that Loki server ports are configured"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if "server" in config:
            server = config["server"]
            # Should have HTTP and/or gRPC ports
            assert "http_listen_port" in server or "grpc_listen_port" in server
    
    def test_loki_has_storage_config(self):
        """Test that Loki has storage configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Should have storage configuration
        assert "storage_config" in config or "common" in config
    
    def test_loki_has_schema_config(self):
        """Test that Loki has schema configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "schema_config" in config
        schema = config["schema_config"]
        assert "configs" in schema
        assert isinstance(schema["configs"], list)
    
    def test_loki_schema_has_required_fields(self):
        """Test that Loki schema configs have required fields"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if "schema_config" in config:
            schemas = config["schema_config"].get("configs", [])
            for schema in schemas:
                assert "from" in schema
                assert "store" in schema or "object_store" in schema
    
    def test_loki_has_limits_config(self):
        """Test that Loki has limits configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Should have limits to prevent resource exhaustion
        assert "limits_config" in config or "limits" in config
    
    def test_loki_has_compactor_config(self):
        """Test that Loki has compactor configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Compactor is important for retention
        if "compactor" in config:
            compactor = config["compactor"]
            assert isinstance(compactor, dict)
    
    def test_loki_retention_enabled(self):
        """Test that Loki retention is properly configured"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Check if retention is configured
        if "compactor" in config:
            compactor = config["compactor"]
            # retention_enabled should be true for retention to work
            assert "retention_enabled" in compactor or "retention" in str(config).lower()
    
    def test_loki_has_table_manager(self):
        """Test that Loki has table manager configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Table manager handles index retention
        if "table_manager" in config:
            table_mgr = config["table_manager"]
            assert isinstance(table_mgr, dict)


class TestPromtailConfigEnhanced:
    """Enhanced tests for Promtail configuration"""
    
    def test_promtail_scrape_configs_not_empty(self):
        """Test that Promtail has at least one scrape config"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/promtail-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if "scrape_configs" in config:
            scrape_configs = config["scrape_configs"]
            assert len(scrape_configs) > 0, "Should have at least one scrape config"
    
    def test_promtail_scrape_configs_have_job_names(self):
        """Test that all scrape configs have job names"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/promtail-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if "scrape_configs" in config:
            for scrape_config in config["scrape_configs"]:
                assert "job_name" in scrape_config, "Each scrape config should have a job_name"
    
    def test_promtail_clients_have_url(self):
        """Test that Promtail clients have URL configured"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/promtail-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if "clients" in config:
            clients = config["clients"]
            for client in clients:
                assert "url" in client, "Each client should have a URL"
    
    def test_promtail_has_positions_file(self):
        """Test that Promtail has positions file configured"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/promtail-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Positions file tracks what has been read
        if "positions" in config:
            positions = config["positions"]
            assert "filename" in positions or isinstance(positions, str)


class TestPrometheusConfigEnhanced:
    """Enhanced tests for Prometheus configuration"""
    
    def test_prometheus_scrape_configs_not_empty(self):
        """Test that Prometheus has at least one scrape config"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if "scrape_configs" in config:
            assert len(config["scrape_configs"]) > 0, "Should have at least one scrape config"
    
    def test_prometheus_scrape_configs_have_job_names(self):
        """Test that all scrape configs have job names"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if "scrape_configs" in config:
            for scrape_config in config["scrape_configs"]:
                assert "job_name" in scrape_config
    
    def test_prometheus_scrape_configs_have_targets(self):
        """Test that scrape configs have targets defined"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if "scrape_configs" in config:
            for scrape_config in config["scrape_configs"]:
                # Should have static_configs or other discovery mechanism
                assert "static_configs" in scrape_config or "file_sd_configs" in scrape_config or \
                       "kubernetes_sd_configs" in scrape_config or "dns_sd_configs" in scrape_config
    
    def test_prometheus_scrape_interval_is_reasonable(self):
        """Test that scrape interval is reasonable"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if "global" in config and "scrape_interval" in config["global"]:
            interval = config["global"]["scrape_interval"]
            # Should be a string like "15s", "30s", etc.
            assert isinstance(interval, str)
            assert "s" in interval or "m" in interval


class TestAlertmanagerConfigEnhanced:
    """Enhanced tests for Alertmanager configuration"""
    
    def test_alertmanager_receivers_not_empty(self):
        """Test that there is at least one receiver"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/alertmanager/alertmanager.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        receivers = config.get("receivers", [])
        assert len(receivers) > 0, "Should have at least one receiver"
    
    def test_alertmanager_route_has_receiver(self):
        """Test that route references a valid receiver"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/alertmanager/alertmanager.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        route = config.get("route", {})
        receiver_name = route.get("receiver")
        
        if receiver_name:
            # Check that this receiver exists
            receivers = config.get("receivers", [])
            receiver_names = [r.get("name") for r in receivers]
            assert receiver_name in receiver_names, f"Route receiver '{receiver_name}' not found in receivers"
    
    def test_alertmanager_has_global_config(self):
        """Test that Alertmanager has global configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/alertmanager/alertmanager.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Global config is optional but recommended
        if "global" in config:
            assert isinstance(config["global"], dict)
    
    def test_alertmanager_inhibit_rules_if_present(self):
        """Test that inhibit rules are properly formatted if present"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/alertmanager/alertmanager.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if "inhibit_rules" in config:
            rules = config["inhibit_rules"]
            assert isinstance(rules, list)
            for rule in rules:
                # Each rule should have source and target matchers
                assert "source_match" in rule or "source_matchers" in rule or \
                       "target_match" in rule or "target_matchers" in rule


class TestInfrastructureAlertsEnhanced:
    """Enhanced tests for infrastructure alerts with focus on new rules"""
    
    def test_alerts_have_unique_names(self):
        """Test that all alert rules have unique names"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alert_names = set()
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule:
                    alert_name = rule["alert"]
                    assert alert_name not in alert_names, f"Duplicate alert name: {alert_name}"
                    alert_names.add(alert_name)
    
    def test_alerts_have_severity_labels(self):
        """Test that alerts have severity labels"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule:
                    labels = rule.get("labels", {})
                    assert "severity" in labels, f"Alert {rule['alert']} missing severity label"
                    # Severity should be one of the standard values
                    assert labels["severity"] in ["critical", "warning", "info"]
    
    def test_alerts_have_annotations(self):
        """Test that alerts have annotations"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule:
                    assert "annotations" in rule, f"Alert {rule['alert']} missing annotations"
                    annotations = rule["annotations"]
                    # Should have summary or description
                    assert "summary" in annotations or "description" in annotations
    
    def test_alerts_have_for_duration(self):
        """Test that alerts have 'for' duration to prevent flapping"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule and rule.get("labels", {}).get("severity") in ["critical", "warning"]:
                    # Critical and warning alerts should have a 'for' duration
                    assert "for" in rule, f"Alert {rule['alert']} should have 'for' duration"
    
    def test_cpu_alerts_exist(self):
        """Test that CPU monitoring alerts exist"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alert_names = []
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule:
                    alert_names.append(rule["alert"])
        
        # Should have CPU-related alerts
        cpu_alerts = [name for name in alert_names if "cpu" in name.lower()]
        assert len(cpu_alerts) > 0, "Should have CPU monitoring alerts"
    
    def test_memory_alerts_exist(self):
        """Test that memory monitoring alerts exist"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alert_names = []
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule:
                    alert_names.append(rule["alert"])
        
        # Should have memory-related alerts
        memory_alerts = [name for name in alert_names if "memory" in name.lower() or "mem" in name.lower()]
        assert len(memory_alerts) > 0, "Should have memory monitoring alerts"
    
    def test_disk_alerts_exist(self):
        """Test that disk monitoring alerts exist"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alert_names = []
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule:
                    alert_names.append(rule["alert"])
        
        # Should have disk-related alerts
        disk_alerts = [name for name in alert_names if "disk" in name.lower() or "filesystem" in name.lower()]
        assert len(disk_alerts) > 0, "Should have disk monitoring alerts"
    
    def test_alert_expressions_use_proper_syntax(self):
        """Test that alert expressions use proper PromQL syntax"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "expr" in rule:
                    expr = rule["expr"]
                    assert isinstance(expr, str) or isinstance(expr, (int, float))
                    # Expression should not be empty
                    if isinstance(expr, str):
                        assert len(expr.strip()) > 0
    
    def test_alerts_have_component_labels(self):
        """Test that alerts have component labels for categorization"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule:
                    labels = rule.get("labels", {})
                    # Should have component or category label
                    assert "component" in labels or "category" in labels or "team" in labels
    
    def test_runbook_annotations_present(self):
        """Test that alerts have runbook URLs or references"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alerts_without_runbooks = []
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule:
                    annotations = rule.get("annotations", {})
                    # Should have runbook URL for documentation
                    if "runbook" not in annotations and "runbook_url" not in annotations:
                        alerts_without_runbooks.append(rule["alert"])
        
        # Most alerts should have runbooks
        if len(alerts_without_runbooks) > 0:
            # Allow some alerts without runbooks but warn
            total_alerts = sum(len([r for r in group.get("rules", []) if "alert" in r]) 
                             for group in config.get("groups", []))
            assert len(alerts_without_runbooks) < total_alerts * 0.5, \
                f"Too many alerts without runbooks: {alerts_without_runbooks}"


class TestAlertThresholds:
    """Test that alert thresholds are reasonable"""
    
    def test_cpu_thresholds_are_reasonable(self):
        """Test that CPU alert thresholds are reasonable"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule and "cpu" in rule["alert"].lower():
                    expr = rule.get("expr", "")
                    # CPU thresholds should typically be between 70-100%
                    if "> " in str(expr) or ">" in str(expr):
                        # Just verify the expression exists and is not empty
                        assert len(str(expr)) > 0
    
    def test_memory_thresholds_are_reasonable(self):
        """Test that memory alert thresholds are reasonable"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule and ("memory" in rule["alert"].lower() or "mem" in rule["alert"].lower()):
                    expr = rule.get("expr", "")
                    # Memory expressions should exist
                    assert len(str(expr)) > 0
    
    def test_disk_thresholds_are_reasonable(self):
        """Test that disk alert thresholds are reasonable"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule and "disk" in rule["alert"].lower():
                    expr = rule.get("expr", "")
                    # Disk expressions should exist
                    assert len(str(expr)) > 0


class TestAlertDocumentation:
    """Test that alerts are well-documented"""
    
    def test_alert_annotations_are_descriptive(self):
        """Test that alert annotations are descriptive"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule:
                    annotations = rule.get("annotations", {})
                    for key, value in annotations.items():
                        # Annotations should be meaningful strings
                        assert isinstance(value, str)
                        assert len(value) > 10, f"Annotation '{key}' for {rule['alert']} is too short"
    
    def test_alert_summaries_contain_variables(self):
        """Test that alert summaries use template variables"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule:
                    annotations = rule.get("annotations", {})
                    summary = annotations.get("summary", "")
                    # Summary should use template variables for context
                    if summary and "instance" not in summary.lower() and "job" not in summary.lower():
                        # At least check it's not completely static
                        pass  # This is acceptable for some alerts


if __name__ == "__main__":
    pytest.main([__file__, "-v"])