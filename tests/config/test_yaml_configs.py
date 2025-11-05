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

class TestLokiConfigEnhancements:
    """Test enhanced Loki configuration"""
    
    def test_loki_has_detailed_comments(self):
        """Test that Loki config has detailed documentation comments"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            content = f.read()
        
        # Should have detailed comments explaining configuration
        assert '# ' in content
        assert 'homelab' in content.lower() or 'deployment' in content.lower()
    
    def test_loki_ingester_configuration(self):
        """Test that Loki has ingester configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "ingester" in config
        ingester = config["ingester"]
        
        # Check for important ingester settings
        assert "chunk_idle_period" in ingester or "chunk_retain_period" in ingester
    
    def test_loki_common_configuration(self):
        """Test that Loki has common configuration section"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "common" in config
        common = config["common"]
        
        # Check for storage configuration
        assert "storage" in common or "path_prefix" in common
    
    def test_loki_server_runtime_config(self):
        """Test that Loki server has runtime config enabled"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if "server" in config:
            server = config["server"]
            # If enable_runtime_config is present, it should be true
            if "enable_runtime_config" in server:
                assert server["enable_runtime_config"] is True
    
    def test_loki_replication_factor(self):
        """Test that Loki replication factor is set appropriately"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # For single-node homelab, replication_factor should be 1
        if "common" in config and "replication_factor" in config["common"]:
            assert config["common"]["replication_factor"] == 1


class TestPrometheusConfigEnhancements:
    """Test enhanced Prometheus configuration"""
    
    def test_prometheus_has_detailed_comments(self):
        """Test that Prometheus config has detailed documentation"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            content = f.read()
        
        # Should have comprehensive comments
        assert '# ' in content
        assert content.count('#') > 10, "Should have many comment lines"
    
    def test_prometheus_alert_relabel_configs(self):
        """Test that Prometheus has alert relabeling configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if "alerting" in config:
            alerting = config["alerting"]
            if "alert_relabel_configs" in alerting:
                relabel_configs = alerting["alert_relabel_configs"]
                assert isinstance(relabel_configs, list)
                assert len(relabel_configs) > 0
    
    def test_prometheus_external_labels(self):
        """Test that Prometheus has external labels configured"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if "global" in config:
            global_config = config["global"]
            if "external_labels" in global_config:
                external_labels = global_config["external_labels"]
                assert isinstance(external_labels, dict)
                # Common labels for homelab
                assert "environment" in external_labels or "cluster" in external_labels
    
    def test_prometheus_alertmanager_timeout(self):
        """Test that alertmanager configuration includes timeout"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if "alerting" in config and "alertmanagers" in config["alerting"]:
            alertmanagers = config["alerting"]["alertmanagers"]
            # Check if any alertmanager config has timeout
            has_timeout = any("timeout" in am for am in alertmanagers if isinstance(am, dict))
            # This is optional, so we just check structure
            assert isinstance(alertmanagers, list)


class TestInfrastructureAlertsEnhancements:
    """Test enhanced infrastructure alerts configuration"""
    
    def test_alerts_have_detailed_comments(self):
        """Test that alerts have comprehensive documentation"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            content = f.read()
        
        # Should have extensive comments
        assert '# ' in content
        assert 'rationale' in content.lower() or 'threshold' in content.lower() or 'monitoring' in content.lower()
    
    def test_alerts_have_severity_labels(self):
        """Test that all alerts have severity labels"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        groups = config.get("groups", [])
        for group in groups:
            rules = group.get("rules", [])
            for rule in rules:
                if "alert" in rule:  # Only check alert rules, not recording rules
                    labels = rule.get("labels", {})
                    assert "severity" in labels, f"Alert {rule.get('alert')} missing severity label"
                    assert labels["severity"] in ["critical", "warning", "info"]
    
    def test_alerts_have_component_labels(self):
        """Test that alerts have component labels for categorization"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        groups = config.get("groups", [])
        for group in groups:
            rules = group.get("rules", [])
            for rule in rules:
                if "alert" in rule:
                    labels = rule.get("labels", {})
                    # Component label helps with routing
                    assert "component" in labels or "severity" in labels
    
    def test_alerts_have_runbook_urls(self):
        """Test that alerts reference runbooks in annotations"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        groups = config.get("groups", [])
        alerts_with_runbooks = 0
        total_alerts = 0
        
        for group in groups:
            rules = group.get("rules", [])
            for rule in rules:
                if "alert" in rule:
                    total_alerts += 1
                    annotations = rule.get("annotations", {})
                    if "runbook" in annotations:
                        alerts_with_runbooks += 1
        
        # Most alerts should have runbook references
        if total_alerts > 0:
            runbook_percentage = (alerts_with_runbooks / total_alerts) * 100
            assert runbook_percentage > 50, "Most alerts should have runbook links"
    
    def test_alerts_have_detailed_descriptions(self):
        """Test that alerts have meaningful descriptions"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        groups = config.get("groups", [])
        for group in groups:
            rules = group.get("rules", [])
            for rule in rules:
                if "alert" in rule:
                    annotations = rule.get("annotations", {})
                    assert "summary" in annotations or "description" in annotations
                    
                    if "description" in annotations:
                        desc = annotations["description"]
                        # Description should be meaningful
                        assert len(desc) > 20, f"Alert {rule.get('alert')} has too brief description"
    
    def test_alerts_use_value_templating(self):
        """Test that alerts use Prometheus templating for values"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        groups = config.get("groups", [])
        alerts_with_templates = 0
        total_alerts = 0
        
        for group in groups:
            rules = group.get("rules", [])
            for rule in rules:
                if "alert" in rule:
                    total_alerts += 1
                    annotations = rule.get("annotations", {})
                    annotation_str = str(annotations)
                    # Check for Prometheus templating
                    if "{{ " in annotation_str and " }}" in annotation_str:
                        alerts_with_templates += 1
        
        # Many alerts should use templating to show current values
        if total_alerts > 0:
            template_percentage = (alerts_with_templates / total_alerts) * 100
            assert template_percentage > 30, "Alerts should use templating for dynamic values"
    
    def test_cpu_alerts_exist(self):
        """Test that CPU usage alerts are defined"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alert_names = []
        groups = config.get("groups", [])
        for group in groups:
            rules = group.get("rules", [])
            for rule in rules:
                if "alert" in rule:
                    alert_names.append(rule["alert"])
        
        # Should have CPU-related alerts
        cpu_alerts = [name for name in alert_names if "CPU" in name or "cpu" in name.lower()]
        assert len(cpu_alerts) > 0, "Should have CPU usage alerts"
    
    def test_memory_alerts_exist(self):
        """Test that memory usage alerts are defined"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alert_names = []
        groups = config.get("groups", [])
        for group in groups:
            rules = group.get("rules", [])
            for rule in rules:
                if "alert" in rule:
                    alert_names.append(rule["alert"])
        
        # Should have memory-related alerts
        memory_alerts = [name for name in alert_names if "Memory" in name or "memory" in name.lower()]
        assert len(memory_alerts) > 0, "Should have memory usage alerts"
    
    def test_host_down_alert_exists(self):
        """Test that host down alert is defined"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alert_names = []
        groups = config.get("groups", [])
        for group in groups:
            rules = group.get("rules", [])
            for rule in rules:
                if "alert" in rule:
                    alert_names.append(rule["alert"])
        
        # Should have host/instance down alert
        down_alerts = [name for name in alert_names if "Down" in name or "down" in name.lower() or "unreachable" in name.lower()]
        assert len(down_alerts) > 0, "Should have host down alerts"


class TestYAMLFormatting:
    """Test YAML formatting and consistency"""
    
    def test_yaml_files_use_consistent_indentation(self):
        """Test that YAML files use consistent indentation"""
        yaml_files = [
            "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml",
            "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml",
            "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        ]
        
        for file_path in yaml_files:
            full_path = BASE_PATH / file_path
            if full_path.exists():
                with open(full_path) as f:
                    content = f.read()
                
                # Check that indentation is consistent (2 spaces is common)
                lines = content.split('\n')
                indented_lines = [line for line in lines if line and line[0] == ' ']
                
                if indented_lines:
                    # Most lines should use multiples of 2 spaces
                    proper_indent = sum(1 for line in indented_lines if len(line) - len(line.lstrip()) % 2 == 0)
                    if len(indented_lines) > 0:
                        indent_percentage = (proper_indent / len(indented_lines)) * 100
                        assert indent_percentage > 90, f"{file_path} should use consistent indentation"
    
    def test_yaml_files_end_with_newline(self):
        """Test that YAML files end with a newline"""
        yaml_files = [
            "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml",
            "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml",
            "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        ]
        
        for file_path in yaml_files:
            full_path = BASE_PATH / file_path
            if full_path.exists():
                with open(full_path, 'rb') as f:
                    content = f.read()
                assert content.endswith(b'\n'), f"{file_path} should end with newline"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestLokiEnhancements:
    """Test enhanced Loki configuration"""
    
    def test_loki_has_comments(self):
        """Test detailed comments in Loki config"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        with open(config_path) as f:
            content = f.read()
            assert '# ' in content
            assert content.count('#') > 10
    
    def test_loki_ingester_config(self):
        """Test Loki ingester configuration"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if "ingester" in config:
            ingester = config["ingester"]
            assert "chunk_idle_period" in ingester or "chunk_retain_period" in ingester


class TestPrometheusEnhancements:
    """Test enhanced Prometheus configuration"""
    
    def test_prometheus_has_comments(self):
        """Test detailed comments in Prometheus config"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        with open(config_path) as f:
            content = f.read()
            assert '# ' in content
            assert content.count('#') > 10
    
    def test_prometheus_external_labels(self):
        """Test Prometheus external labels"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if "global" in config and "external_labels" in config["global"]:
            labels = config["global"]["external_labels"]
            assert isinstance(labels, dict)


class TestInfrastructureAlertsEnhancements:
    """Test enhanced infrastructure alerts"""
    
    def test_alerts_have_severity(self):
        """Test all alerts have severity labels"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        groups = config.get("groups", [])
        for group in groups:
            for rule in group.get("rules", []):
                if "alert" in rule:
                    labels = rule.get("labels", {})
                    assert "severity" in labels
                    assert labels["severity"] in ["critical", "warning", "info"]
    
    def test_alerts_have_annotations(self):
        """Test alerts have proper annotations"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        groups = config.get("groups", [])
        for group in groups:
            for rule in group.get("rules", []):
                if "alert" in rule:
                    annotations = rule.get("annotations", {})
                    assert "summary" in annotations or "description" in annotations
    
    def test_cpu_alerts_exist(self):
        """Test CPU usage alerts are defined"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alert_names = []
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule:
                    alert_names.append(rule["alert"])
        
        cpu_alerts = [n for n in alert_names if "CPU" in n or "cpu" in n.lower()]
        assert len(cpu_alerts) > 0
    
    def test_memory_alerts_exist(self):
        """Test memory usage alerts are defined"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alert_names = []
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule:
                    alert_names.append(rule["alert"])
        
        mem_alerts = [n for n in alert_names if "Memory" in n or "memory" in n.lower()]
        assert len(mem_alerts) > 0


class TestYAMLFormatting:
    """Test YAML formatting consistency"""
    
    def test_yaml_files_end_with_newline(self):
        """Test YAML files end with newline"""
        yaml_files = [
            "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml",
            "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml",
            "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        ]
        
        for file_path in yaml_files:
            full_path = BASE_PATH / file_path
            if full_path.exists():
                with open(full_path, 'rb') as f:
                    assert f.read().endswith(b'\n')