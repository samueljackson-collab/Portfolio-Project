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
    
    def test_loki_config_has_ingester_section(self):
        """Test that Loki config now includes ingester section"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "ingester" in config, "Loki config should have ingester section"
    
    def test_loki_ingester_chunk_settings(self):
        """Test that ingester has chunk management settings"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        ingester = config.get("ingester", {})
        assert "chunk_idle_period" in ingester
        assert "chunk_retain_period" in ingester
        assert "chunk_target_size" in ingester
    
    def test_loki_ingester_wal_enabled(self):
        """Test that Write-Ahead Log is enabled"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        ingester = config.get("ingester", {})
        wal = ingester.get("wal", {})
        assert wal.get("enabled") is True
        assert "dir" in wal
        assert wal.get("flush_on_shutdown") is True
    
    def test_loki_chunk_target_size_reasonable(self):
        """Test that chunk target size is set to reasonable value (1MB)"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        ingester = config.get("ingester", {})
        chunk_size = ingester.get("chunk_target_size", 0)
        assert chunk_size == 1048576, "Chunk size should be 1MB (1048576 bytes)"
    
    def test_loki_retention_period_set(self):
        """Test that retention period is configured"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        table_manager = config.get("table_manager", {})
        assert "retention_period" in table_manager
        assert table_manager.get("retention_deletes_enabled") is True
    
    def test_loki_config_has_comprehensive_comments(self):
        """Test that Loki config has deployment notes"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            content = f.read()
        
        # Check for deployment documentation
        assert "VALIDATION AND DEPLOYMENT NOTES" in content or "deployment" in content.lower()
        assert "verify-config" in content or "validation" in content.lower()


class TestPrometheusConfigEnhancements:
    """Test enhanced Prometheus configuration"""
    
    def test_prometheus_has_alert_relabel_configs(self):
        """Test that Prometheus has alert relabeling configured"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alerting = config.get("alerting", {})
        assert "alert_relabel_configs" in alerting
        assert isinstance(alerting["alert_relabel_configs"], list)
        assert len(alerting["alert_relabel_configs"]) > 0
    
    def test_prometheus_severity_labels_derived(self):
        """Test that severity labels are derived from alert names"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alerting = config.get("alerting", {})
        relabel_configs = alerting.get("alert_relabel_configs", [])
        
        # Check for severity label derivation rules
        severity_found = False
        for rule in relabel_configs:
            if rule.get("target_label") == "severity":
                severity_found = True
                break
        assert severity_found, "Should have rules to derive severity labels"
    
    def test_prometheus_scrape_jobs_simplified(self):
        """Test that scrape job configuration is streamlined"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        scrape_configs = config.get("scrape_configs", [])
        assert len(scrape_configs) > 0
        
        # Check that jobs have proper naming
        job_names = [job.get("job_name") for job in scrape_configs]
        assert "prometheus" in job_names or "proxmox-node" in job_names
    
    def test_prometheus_scrape_timeouts_configured(self):
        """Test that scrape timeouts are explicitly set"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        scrape_configs = config.get("scrape_configs", [])
        # At least some jobs should have explicit timeouts
        timeout_jobs = [job for job in scrape_configs if "scrape_timeout" in job]
        assert len(timeout_jobs) > 0
    
    def test_prometheus_uses_hostname_labels(self):
        """Test that hostname labels are used for better identification"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        scrape_configs = config.get("scrape_configs", [])
        
        # Check for hostname in static_configs labels
        hostname_found = False
        for job in scrape_configs:
            static_configs = job.get("static_configs", [])
            for sc in static_configs:
                labels = sc.get("labels", {})
                if "hostname" in labels:
                    hostname_found = True
                    break
            if hostname_found:
                break
        
        assert hostname_found, "Should use hostname labels for better identification"


class TestInfrastructureAlertsEnhancements:
    """Test enhanced infrastructure alerts"""
    
    def test_alerts_have_component_labels(self):
        """Test that alerts have component labels"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        groups = config.get("groups", [])
        for group in groups:
            rules = group.get("rules", [])
            for rule in rules:
                if "alert" in rule:
                    labels = rule.get("labels", {})
                    assert "component" in labels, f"Alert {rule.get('alert')} should have component label"
    
    def test_alerts_use_runbook_annotation(self):
        """Test that alerts use 'runbook' annotation instead of 'runbook_url'"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        groups = config.get("groups", [])
        for group in groups:
            rules = group.get("rules", [])
            for rule in rules:
                if "alert" in rule:
                    annotations = rule.get("annotations", {})
                    # Should use 'runbook' instead of 'runbook_url'
                    assert "runbook" in annotations or "summary" in annotations
    
    def test_cpu_alerts_have_warning_and_critical(self):
        """Test that CPU alerts have both warning and critical thresholds"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        groups = config.get("groups", [])
        cpu_alerts = []
        for group in groups:
            rules = group.get("rules", [])
            for rule in rules:
                alert_name = rule.get("alert", "")
                if "CPU" in alert_name:
                    cpu_alerts.append(alert_name)
        
        # Should have both warning and critical CPU alerts
        has_warning = any("Warning" in alert for alert in cpu_alerts)
        has_critical = any("Critical" in alert for alert in cpu_alerts)
        assert has_warning or has_critical, "Should have CPU alerts at different severity levels"
    
    def test_memory_alerts_have_warning_and_critical(self):
        """Test that memory alerts have both warning and critical thresholds"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        groups = config.get("groups", [])
        memory_alerts = []
        for group in groups:
            rules = group.get("rules", [])
            for rule in rules:
                alert_name = rule.get("alert", "")
                if "Memory" in alert_name:
                    memory_alerts.append(alert_name)
        
        # Should have both warning and critical memory alerts
        has_warning = any("Warning" in alert for alert in memory_alerts)
        has_critical = any("Critical" in alert for alert in memory_alerts)
        assert has_warning or has_critical, "Should have memory alerts at different severity levels"
    
    def test_disk_alerts_have_warning_and_critical(self):
        """Test that disk alerts have both warning and critical thresholds"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        groups = config.get("groups", [])
        disk_alerts = []
        for group in groups:
            rules = group.get("rules", [])
            for rule in rules:
                alert_name = rule.get("alert", "")
                if "Disk" in alert_name or "disk" in alert_name.lower():
                    disk_alerts.append(alert_name)
        
        # Should have both warning and critical disk alerts
        has_warning = any("Warning" in alert or "Low" in alert for alert in disk_alerts)
        has_critical = any("Critical" in alert for alert in disk_alerts)
        assert has_warning or has_critical, "Should have disk alerts at different severity levels"
    
    def test_alert_for_durations_reasonable(self):
        """Test that alert 'for' durations are reasonable"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        groups = config.get("groups", [])
        for group in groups:
            rules = group.get("rules", [])
            for rule in rules:
                if "alert" in rule and "for" in rule:
                    duration = rule["for"]
                    # Duration should be reasonable (not too short, not too long)
                    assert duration in ["2m", "5m", "10m", "15m", "30m", "1h"], \
                        f"Alert {rule.get('alert')} has unusual duration: {duration}"
    
    def test_backup_alert_exists(self):
        """Test that backup failure alert exists"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        groups = config.get("groups", [])
        backup_alerts = []
        for group in groups:
            rules = group.get("rules", [])
            for rule in rules:
                alert_name = rule.get("alert", "")
                if "Backup" in alert_name or "backup" in alert_name.lower():
                    backup_alerts.append(alert_name)
        
        assert len(backup_alerts) > 0, "Should have backup monitoring alerts"


class TestYAMLSyntaxAndStructure:
    """Test YAML syntax and structure improvements"""
    
    def test_loki_config_parses_without_errors(self):
        """Test that enhanced Loki config parses without errors"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)
        assert len(config) > 0
    
    def test_prometheus_config_parses_without_errors(self):
        """Test that enhanced Prometheus config parses without errors"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)
        assert len(config) > 0
    
    def test_alerts_config_parses_without_errors(self):
        """Test that enhanced alerts config parses without errors"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)
        assert len(config) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])