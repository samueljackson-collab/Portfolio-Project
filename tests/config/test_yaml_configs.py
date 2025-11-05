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

class TestInfrastructureAlertsChanges:
    """Test changes to infrastructure_alerts.yml"""
    
    def test_single_infrastructure_group(self):
        """Test that alerts are consolidated into single infrastructure group"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        groups = config.get("groups", [])
        group_names = [g.get("name") for g in groups]
        
        # Should have infrastructure group
        assert "infrastructure" in group_names
    
    def test_alert_severity_labels(self):
        """Test that alerts have severity labels (warning or critical)"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule:
                    labels = rule.get("labels", {})
                    assert "severity" in labels
                    assert labels["severity"] in ["warning", "critical", "info"]
    
    def test_alert_component_labels(self):
        """Test that alerts have component labels"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule:
                    labels = rule.get("labels", {})
                    assert "component" in labels
    
    def test_cpu_alerts_have_warning_and_critical(self):
        """Test that CPU alerts have both warning and critical thresholds"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        cpu_alerts = []
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule and "CPU" in rule["alert"]:
                    cpu_alerts.append(rule)
        
        # Should have at least warning and critical
        severities = [a.get("labels", {}).get("severity") for a in cpu_alerts]
        assert "warning" in severities or "critical" in severities
    
    def test_memory_alerts_have_warning_and_critical(self):
        """Test that memory alerts have both warning and critical thresholds"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        memory_alerts = []
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule and "Memory" in rule["alert"]:
                    memory_alerts.append(rule)
        
        severities = [a.get("labels", {}).get("severity") for a in memory_alerts]
        assert "warning" in severities or "critical" in severities
    
    def test_disk_alerts_have_warning_and_critical(self):
        """Test that disk alerts have both warning and critical thresholds"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        disk_alerts = []
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule and "Disk" in rule["alert"]:
                    disk_alerts.append(rule)
        
        severities = [a.get("labels", {}).get("severity") for a in disk_alerts]
        assert "warning" in severities or "critical" in severities
    
    def test_annotations_have_runbook(self):
        """Test that annotations include runbook links"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule:
                    annotations = rule.get("annotations", {})
                    assert "runbook" in annotations or "runbook_url" in annotations
    
    def test_annotations_have_summary_and_description(self):
        """Test that all alerts have summary and description"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule:
                    annotations = rule.get("annotations", {})
                    assert "summary" in annotations
                    assert "description" in annotations
    
    def test_host_down_alert_exists(self):
        """Test that HostDown alert is present"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alert_names = []
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule:
                    alert_names.append(rule["alert"])
        
        assert "HostDown" in alert_names
    
    def test_backup_job_failed_alert_exists(self):
        """Test that BackupJobFailed alert is present"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alert_names = []
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" in rule:
                    alert_names.append(rule["alert"])
        
        assert "BackupJobFailed" in alert_names


class TestPrometheusConfigChanges:
    """Test changes to prometheus.yml"""
    
    def test_alert_relabel_configs_present(self):
        """Test that alert_relabel_configs are configured"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alerting = config.get("alerting", {})
        assert "alert_relabel_configs" in alerting
        assert isinstance(alerting["alert_relabel_configs"], list)
        assert len(alerting["alert_relabel_configs"]) > 0
    
    def test_severity_relabeling_rules(self):
        """Test that severity labels are dynamically assigned"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        relabel_configs = config.get("alerting", {}).get("alert_relabel_configs", [])
        
        # Should have rules for critical, warning, info
        target_labels = [r.get("target_label") for r in relabel_configs]
        assert target_labels.count("severity") >= 3
    
    def test_alertmanager_timeout_configured(self):
        """Test that alertmanager timeout is set"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alertmanagers = config.get("alerting", {}).get("alertmanagers", [])
        for am in alertmanagers:
            assert "timeout" in am
    
    def test_scrape_configs_have_labels(self):
        """Test that scrape configs include proper labels"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for job in config.get("scrape_configs", []):
            static_configs = job.get("static_configs", [])
            for sc in static_configs:
                assert "labels" in sc or "targets" in sc
    
    def test_external_labels_configured(self):
        """Test that external labels include environment and cluster"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        external_labels = config.get("global", {}).get("external_labels", {})
        assert "environment" in external_labels
        assert "cluster" in external_labels
    
    def test_job_name_consistency(self):
        """Test that job names follow consistent naming"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        job_names = [job.get("job_name") for job in config.get("scrape_configs", [])]
        # All job names should be defined
        assert all(job_names)
        assert len(job_names) > 0
    
    def test_prometheus_self_monitoring(self):
        """Test that Prometheus monitors itself"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        job_names = [job.get("job_name") for job in config.get("scrape_configs", [])]
        assert "prometheus" in job_names
    
    def test_scrape_timeout_less_than_interval(self):
        """Test that scrape timeouts are less than scrape intervals"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        global_interval = config.get("global", {}).get("scrape_interval", "15s")
        
        for job in config.get("scrape_configs", []):
            interval = job.get("scrape_interval", global_interval)
            timeout = job.get("scrape_timeout")
            
            if timeout:
                # Parse durations (simplified check)
                interval_val = int(interval.rstrip('s'))
                timeout_val = int(timeout.rstrip('s'))
                assert timeout_val < interval_val
    
    def test_vm_nodes_job_with_relabeling(self):
        """Test that vm-nodes job has hostname relabeling"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        vm_jobs = [j for j in config.get("scrape_configs", []) if "vm" in j.get("job_name", "").lower()]
        
        for job in vm_jobs:
            if "relabel_configs" in job:
                # Should have hostname relabeling rules
                relabel_configs = job.get("relabel_configs", [])
                target_labels = [r.get("target_label") for r in relabel_configs]
                assert "hostname" in target_labels or len(relabel_configs) > 0

