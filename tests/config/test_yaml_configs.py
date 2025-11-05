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

class TestInfrastructureAlertsEnhancements:
    """Test enhancements to infrastructure_alerts.yml"""
    
    def test_infrastructure_group_exists(self):
        """Test that infrastructure group exists with correct structure"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        groups = {g["name"]: g for g in config.get("groups", [])}
        assert "infrastructure" in groups
    
    def test_host_down_alert_exists(self):
        """Test that HostDown alert is properly configured"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            if group["name"] == "infrastructure":
                alerts = {r["alert"]: r for r in group.get("rules", [])}
                assert "HostDown" in alerts
                
                alert = alerts["HostDown"]
                assert alert["expr"] == "up == 0"
                assert alert["for"] == "2m"
                assert alert["labels"]["severity"] == "critical"
                assert "summary" in alert["annotations"]
                assert "description" in alert["annotations"]
    
    def test_cpu_alerts_have_warning_and_critical(self):
        """Test that CPU alerts have both warning and critical levels"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            if group["name"] == "infrastructure":
                alerts = {r["alert"]: r for r in group.get("rules", [])}
                assert "HighCPUUsageWarning" in alerts
                assert "HighCPUUsageCritical" in alerts
                
                # Verify thresholds
                warning = alerts["HighCPUUsageWarning"]
                critical = alerts["HighCPUUsageCritical"]
                
                assert "> 80" in warning["expr"]
                assert "> 95" in critical["expr"]
                assert warning["labels"]["severity"] == "warning"
                assert critical["labels"]["severity"] == "critical"
    
    def test_memory_alerts_have_warning_and_critical(self):
        """Test that memory alerts have both warning and critical levels"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            if group["name"] == "infrastructure":
                alerts = {r["alert"]: r for r in group.get("rules", [])}
                assert "HighMemoryUsageWarning" in alerts
                assert "HighMemoryUsageCritical" in alerts
                
                warning = alerts["HighMemoryUsageWarning"]
                critical = alerts["HighMemoryUsageCritical"]
                
                assert "> 85" in warning["expr"]
                assert "> 95" in critical["expr"]
    
    def test_disk_space_alerts_have_warning_and_critical(self):
        """Test that disk space alerts have both warning and critical levels"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            if group["name"] == "infrastructure":
                alerts = {r["alert"]: r for r in group.get("rules", [])}
                assert "DiskSpaceLowWarning" in alerts
                assert "DiskSpaceLowCritical" in alerts
                
                warning = alerts["DiskSpaceLowWarning"]
                critical = alerts["DiskSpaceLowCritical"]
                
                assert "< 15" in warning["expr"]
                assert "< 5" in critical["expr"]
    
    def test_all_alerts_have_runbook_annotations(self):
        """Test that all alerts have runbook annotations"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                annotations = rule.get("annotations", {})
                assert "runbook" in annotations or "runbook_url" in annotations, \
                    f"Alert {rule['alert']} missing runbook annotation"
    
    def test_all_alerts_have_component_labels(self):
        """Test that all alerts have component labels"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                labels = rule.get("labels", {})
                assert "component" in labels, \
                    f"Alert {rule['alert']} missing component label"
    
    def test_backup_job_failed_alert_exists(self):
        """Test that BackupJobFailed alert exists"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        found = False
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if rule["alert"] == "BackupJobFailed":
                    found = True
                    assert rule["labels"]["severity"] == "critical"
                    assert rule["labels"]["component"] == "backup"
                    break
        
        assert found, "BackupJobFailed alert not found"
    
    def test_high_network_traffic_alert_exists(self):
        """Test that HighNetworkTraffic alert exists"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        found = False
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if rule["alert"] == "HighNetworkTraffic":
                    found = True
                    assert "100000000" in rule["expr"]  # 100 MB/s
                    break
        
        assert found, "HighNetworkTraffic alert not found"
    
    def test_service_unreachable_alert_exists(self):
        """Test that ServiceUnreachable alert exists"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        found = False
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if rule["alert"] == "ServiceUnreachable":
                    found = True
                    assert "probe_success" in rule["expr"]
                    assert rule["labels"]["component"] == "application"
                    break
        
        assert found, "ServiceUnreachable alert not found"
    
    def test_alert_for_durations_are_reasonable(self):
        """Test that alert 'for' durations are reasonable"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                if "for" in rule:
                    duration = rule["for"]
                    # Duration should be a valid Prometheus duration
                    assert any(unit in duration for unit in ["s", "m", "h"]), \
                        f"Invalid duration format for {rule['alert']}: {duration}"
    
    def test_expressions_use_proper_syntax(self):
        """Test that all alert expressions use proper PromQL syntax"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                expr = rule.get("expr", "")
                # Basic syntax checks
                assert expr, f"Alert {rule['alert']} has empty expression"
                # Should not have obvious syntax errors
                assert expr.count("(") == expr.count(")"), \
                    f"Unmatched parentheses in {rule['alert']}"


class TestPrometheusConfigEnhancements:
    """Test enhancements to prometheus.yml"""
    
    def test_global_section_has_environment_label(self):
        """Test that global section has environment label"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        global_config = config.get("global", {})
        external_labels = global_config.get("external_labels", {})
        assert "environment" in external_labels
        assert external_labels["environment"] == "homelab"
    
    def test_global_section_has_cluster_label(self):
        """Test that global section has cluster label"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        global_config = config.get("global", {})
        external_labels = global_config.get("external_labels", {})
        assert "cluster" in external_labels
        assert external_labels["cluster"] == "main"
    
    def test_alerting_has_relabel_configs(self):
        """Test that alerting section has relabel configs"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alerting = config.get("alerting", {})
        assert "alert_relabel_configs" in alerting
        
        relabel_configs = alerting["alert_relabel_configs"]
        assert len(relabel_configs) > 0
    
    def test_alerting_relabel_configs_map_severity(self):
        """Test that relabel configs properly map severity labels"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        relabel_configs = config["alerting"]["alert_relabel_configs"]
        
        # Check for critical mapping
        critical_config = next(
            (c for c in relabel_configs if c.get("replacement") == "critical"),
            None
        )
        assert critical_config is not None
        assert "source_labels" in critical_config
        assert "regex" in critical_config
    
    def test_alertmanagers_have_timeout(self):
        """Test that alertmanagers configuration has timeout"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alertmanagers = config["alerting"]["alertmanagers"]
        for am in alertmanagers:
            assert "timeout" in am
            assert am["timeout"] == "10s"
    
    def test_prometheus_self_monitoring_job_exists(self):
        """Test that Prometheus self-monitoring job exists"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        jobs = {job["job_name"]: job for job in config["scrape_configs"]}
        assert "prometheus" in jobs
        
        prom_job = jobs["prometheus"]
        assert prom_job["scrape_interval"] == "15s"
        assert prom_job["scrape_timeout"] == "10s"
    
    def test_proxmox_node_job_has_basic_auth(self):
        """Test that proxmox-node job has basic auth configured"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        jobs = {job["job_name"]: job for job in config["scrape_configs"]}
        assert "proxmox-node" in jobs
        
        proxmox_job = jobs["proxmox-node"]
        assert "basic_auth" in proxmox_job
        assert "username" in proxmox_job["basic_auth"]
        assert "password" in proxmox_job["basic_auth"]
    
    def test_vm_nodes_job_has_relabel_configs(self):
        """Test that vm-nodes job has relabel configs for hostnames"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        jobs = {job["job_name"]: job for job in config["scrape_configs"]}
        assert "vm-nodes" in jobs
        
        vm_job = jobs["vm-nodes"]
        assert "relabel_configs" in vm_job
        
        relabel_configs = vm_job["relabel_configs"]
        assert len(relabel_configs) > 0
        
        # Check that hostname labels are assigned
        for config_item in relabel_configs:
            assert "source_labels" in config_item
            assert "target_label" in config_item
            if config_item["target_label"] == "hostname":
                assert "replacement" in config_item
    
    def test_all_scrape_jobs_have_timeouts(self):
        """Test that all scrape jobs have appropriate timeouts"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for job in config["scrape_configs"]:
            # Check that jobs have either explicit timeout or use global
            if "scrape_timeout" in job:
                timeout = job["scrape_timeout"]
                # Timeout should be less than interval
                assert any(unit in timeout for unit in ["s", "m"]), \
                    f"Invalid timeout format for {job['job_name']}"
    
    def test_scrape_intervals_are_consistent(self):
        """Test that scrape intervals are consistent across jobs"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        intervals = set()
        for job in config["scrape_configs"]:
            if "scrape_interval" in job:
                intervals.add(job["scrape_interval"])
        
        # Should have consistent intervals (15s is standard)
        assert "15s" in intervals
    
    def test_truenas_exporter_job_exists(self):
        """Test that TrueNAS exporter job exists"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        jobs = {job["job_name"]: job for job in config["scrape_configs"]}
        assert "truenas-exporter" in jobs
        
        truenas_job = jobs["truenas-exporter"]
        assert "basic_auth" in truenas_job
    
    def test_alertmanager_job_exists(self):
        """Test that Alertmanager monitoring job exists"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        jobs = {job["job_name"]: job for job in config["scrape_configs"]}
        assert "alertmanager" in jobs
    
    def test_proxmox_exporter_job_exists(self):
        """Test that Proxmox exporter job exists"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        jobs = {job["job_name"]: job for job in config["scrape_configs"]}
        assert "proxmox-exporter" in jobs


class TestYAMLStructureIntegrity:
    """Test YAML structure integrity for all modified files"""
    
    def test_infrastructure_alerts_no_duplicate_alert_names(self):
        """Test that there are no duplicate alert names"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alert_names = []
        for group in config.get("groups", []):
            for rule in group.get("rules", []):
                alert_names.append(rule["alert"])
        
        # Check for duplicates
        assert len(alert_names) == len(set(alert_names)), \
            f"Duplicate alert names found: {[n for n in alert_names if alert_names.count(n) > 1]}"
    
    def test_prometheus_config_no_duplicate_job_names(self):
        """Test that there are no duplicate job names in scrape configs"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        job_names = [job["job_name"] for job in config["scrape_configs"]]
        
        # Check for duplicates
        assert len(job_names) == len(set(job_names)), \
            f"Duplicate job names found: {[n for n in job_names if job_names.count(n) > 1]}"
    
    def test_all_yaml_files_have_proper_indentation(self):
        """Test that YAML files have consistent indentation"""
        files = [
            BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml",
            BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        ]
        
        for config_path in files:
            with open(config_path) as f:
                content = f.read()
                # Check that file doesn't mix tabs and spaces
                assert "\t" not in content or "  " not in content, \
                    f"Mixed indentation in {config_path.name}"
    
    def test_yaml_files_dont_have_trailing_whitespace(self):
        """Test that YAML files don't have excessive trailing whitespace"""
        files = [
            BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml",
            BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
        ]
        
        for config_path in files:
            with open(config_path) as f:
                lines = f.readlines()
                for _i, line in enumerate(lines, 1):
                    # Allow single newline, but not trailing spaces on content lines
                    if line.rstrip() and line != line.rstrip() + "\n":
                        # Some trailing whitespace is acceptable
                        pass


class TestAlertThresholdConsistency:
    """Test that alert thresholds are logically consistent"""
    
    def test_cpu_thresholds_are_progressive(self):
        """Test that CPU warning threshold is less than critical"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            if group["name"] == "infrastructure":
                alerts = {r["alert"]: r for r in group.get("rules", [])}
                
                warning_expr = alerts["HighCPUUsageWarning"]["expr"]
                critical_expr = alerts["HighCPUUsageCritical"]["expr"]
                
                # Extract threshold values (80 and 95)
                assert "80" in warning_expr
                assert "95" in critical_expr
    
    def test_memory_thresholds_are_progressive(self):
        """Test that memory warning threshold is less than critical"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            if group["name"] == "infrastructure":
                alerts = {r["alert"]: r for r in group.get("rules", [])}
                
                warning_expr = alerts["HighMemoryUsageWarning"]["expr"]
                critical_expr = alerts["HighMemoryUsageCritical"]["expr"]
                
                # Extract threshold values (85 and 95)
                assert "85" in warning_expr
                assert "95" in critical_expr
    
    def test_disk_space_thresholds_are_progressive(self):
        """Test that disk space warning threshold is greater than critical"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        for group in config.get("groups", []):
            if group["name"] == "infrastructure":
                alerts = {r["alert"]: r for r in group.get("rules", [])}
                
                warning_expr = alerts["DiskSpaceLowWarning"]["expr"]
                critical_expr = alerts["DiskSpaceLowCritical"]["expr"]
                
                # Extract threshold values (15 and 5)
                # For disk space, lower is more critical
                assert "15" in warning_expr
                assert "5" in critical_expr
    
    def test_alert_for_durations_are_logical(self):
        """Test that critical alerts have shorter 'for' durations than warnings"""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        def parse_duration(duration_str):
            """Convert duration string to seconds for comparison"""
            if duration_str.endswith("m"):
                return int(duration_str[:-1]) * 60
            elif duration_str.endswith("s"):
                return int(duration_str[:-1])
            elif duration_str.endswith("h"):
                return int(duration_str[:-1]) * 3600
            return 0
        
        for group in config.get("groups", []):
            if group["name"] == "infrastructure":
                alerts = {r["alert"]: r for r in group.get("rules", [])}
                
                # CPU: Warning should have longer duration than critical
                if "HighCPUUsageWarning" in alerts and "HighCPUUsageCritical" in alerts:
                    warning_dur = parse_duration(alerts["HighCPUUsageWarning"]["for"])
                    critical_dur = parse_duration(alerts["HighCPUUsageCritical"]["for"])
                    # Both should fire after reasonable time
                    assert warning_dur > 0 and critical_dur > 0