"""Validation tests for homelab configuration files"""
import json
import yaml
import pytest
from pathlib import Path
from xml.etree import ElementTree as ET

BASE_PATH = Path(__file__).parent.parent.parent

class TestPRJHOME001Configs:
    """Test PRJ-HOME-001 Network Infrastructure configuration files"""
    
    def test_pfsense_config_valid_xml(self):
        """Test that pfSense config is valid XML"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/pfsense/pfsense-config.xml"
        assert config_path.exists(), f"pfSense config not found at {config_path}"
        
        # Parse XML
        tree = ET.parse(config_path)
        root = tree.getroot()
        
        assert root.tag == "pfsense"
        assert root.find("system") is not None
        assert root.find("interfaces") is not None
        
    def test_pfsense_has_required_interfaces(self):
        """Test that pfSense has all required VLANs configured"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/pfsense/pfsense-config.xml"
        tree = ET.parse(config_path)
        root = tree.getroot()
        
        interfaces = root.find("interfaces")
        assert interfaces.find("wan") is not None
        assert interfaces.find("lan") is not None
        assert interfaces.find("opt1") is not None  # IoT
        assert interfaces.find("opt2") is not None  # Guest
        assert interfaces.find("opt3") is not None  # Servers
        assert interfaces.find("opt4") is not None  # DMZ
    
    def test_unifi_config_valid_json(self):
        """Test that UniFi config is valid JSON"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/unifi/unifi-config.json"
        assert config_path.exists(), f"UniFi config not found at {config_path}"
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert config is not None
        assert isinstance(config, dict)
        assert "wireless_networks" in config
        assert "devices" in config
        assert "security_settings" in config
    
    def test_unifi_has_three_ssids(self):
        """Test that UniFi config has 3 wireless networks"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/unifi/unifi-config.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        wireless_networks = config.get("wireless_networks", [])
        assert len(wireless_networks) == 3
        
        ssid_names = [net["name"] for net in wireless_networks]
        assert "Homelab-Secure" in ssid_names
        assert "Homelab-IoT" in ssid_names
        assert "Homelab-Guest" in ssid_names
    
    def test_unifi_vlans_configured(self):
        """Test that UniFi has correct VLAN assignments"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/unifi/unifi-config.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        wireless_networks = config.get("wireless_networks", [])
        vlans = [net.get("vlan") for net in wireless_networks]
        
        assert 10 in vlans  # Trusted
        assert 20 in vlans  # IoT
        assert 30 in vlans  # Guest
    
    def test_network_architecture_mermaid_exists(self):
        """Test that network architecture diagram exists"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/documentation/network-architecture.mermaid"
        assert diagram_path.exists()
        
        with open(diagram_path) as f:
            content = f.read()
        
        assert "graph TB" in content or "graph LR" in content or "flowchart" in content
        assert "VLAN" in content
        assert len(content) > 100
    
    def test_network_inventory_exists(self):
        """Test that network inventory documentation exists"""
        inventory_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/documentation/network-inventory.md"
        assert inventory_path.exists()
        
        with open(inventory_path) as f:
            content = f.read()
        
        assert "# Network Inventory" in content
        assert "VLAN 10" in content
        assert "192.168" in content
        assert len(content) > 1000
    
    def test_security_policies_exists(self):
        """Test that security policies documentation exists"""
        policies_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/documentation/security-policies.md"
        assert policies_path.exists()
        
        with open(policies_path) as f:
            content = f.read()
        
        assert "# Network Security Policies" in content
        assert "Firewall" in content or "firewall" in content
        assert len(content) > 1000


class TestPRJHOME002Configs:
    """Test PRJ-HOME-002 Virtualization Platform configuration files"""
    
    def test_proxmox_cluster_conf_exists(self):
        """Test that Proxmox cluster config exists and is valid"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/proxmox/cluster.conf"
        assert config_path.exists()
        
        with open(config_path) as f:
            content = f.read()
        
        assert "cluster" in content
        assert "homelab-cluster" in content
        assert "proxmox-01" in content
        assert "proxmox-02" in content
        assert "proxmox-03" in content
    
    def test_proxmox_storage_cfg_exists(self):
        """Test that Proxmox storage config exists"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/proxmox/storage.cfg"
        assert config_path.exists()
        
        with open(config_path) as f:
            content = f.read()
        
        assert "local-lvm" in content or "local" in content
        assert "ceph" in content or "rbd" in content or "nfs" in content
    
    def test_proxmox_network_interfaces_exists(self):
        """Test that network interfaces config exists"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/proxmox/network-interfaces"
        assert config_path.exists()
        
        with open(config_path) as f:
            content = f.read()
        
        assert "vmbr0" in content
        assert "bridge" in content
        assert "192.168.40" in content
    
    def test_backup_config_valid_json(self):
        """Test that backup config is valid JSON"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/proxmox/backup-config.json"
        assert config_path.exists()
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert config is not None
        assert "backup_schedules" in config
        assert "backup_server" in config
    
    def test_backup_config_has_schedules(self):
        """Test that backup config has backup schedules"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/proxmox/backup-config.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        schedules = config.get("backup_schedules", [])
        assert len(schedules) > 0
        
        # Check critical-daily schedule exists
        schedule_names = [s.get("id") for s in schedules]
        assert "critical-daily" in schedule_names
    
    def test_cloud_init_config_valid_yaml(self):
        """Test that cloud-init config is valid YAML"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/proxmox/vm-templates/cloud-init-config.yml"
        assert config_path.exists()
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)
    
    def test_ansible_inventory_valid_yaml(self):
        """Test that Ansible inventory is valid YAML"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/inventory/hosts.yml"
        assert config_path.exists()
        
        with open(config_path) as f:
            inventory = yaml.safe_load(f)
        
        assert inventory is not None
        assert "all" in inventory
        assert "children" in inventory.get("all", {})
    
    def test_ansible_playbooks_valid_yaml(self):
        """Test that all Ansible playbooks are valid YAML"""
        playbooks_dir = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks"
        assert playbooks_dir.exists()
        
        playbook_files = list(playbooks_dir.glob("*.yml"))
        assert len(playbook_files) >= 5
        
        for playbook_file in playbook_files:
            with open(playbook_file) as f:
                playbook = yaml.safe_load(f)
            
            assert playbook is not None
            assert isinstance(playbook, list)
    
    def test_terraform_files_exist(self):
        """Test that Terraform files exist"""
        terraform_dir = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/terraform"
        
        assert (terraform_dir / "main.tf").exists()
        assert (terraform_dir / "variables.tf").exists()
        assert (terraform_dir / "outputs.tf").exists()
        assert (terraform_dir / "backend.tf").exists()
    
    def test_operational_scripts_exist(self):
        """Test that operational scripts exist and are executable"""
        scripts_dir = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/scripts"
        
        scripts = [
            "backup-verify.sh",
            "health-check.sh",
            "security-scan.sh",
            "disaster-recovery.sh"
        ]
        
        for script in scripts:
            script_path = scripts_dir / script
            assert script_path.exists()
            
            # Check that file has shebang
            with open(script_path) as f:
                first_line = f.readline()
            assert first_line.startswith("#!/bin/bash")
    
    def test_dr_plan_exists(self):
        """Test that disaster recovery plan exists"""
        dr_plan_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/recovery/disaster-recovery-plan.md"
        assert dr_plan_path.exists()
        
        with open(dr_plan_path) as f:
            content = f.read()
        
        assert "# Disaster Recovery Plan" in content
        assert "RTO" in content
        assert "RPO" in content
        assert len(content) > 5000
    
    def test_recovery_procedures_exist(self):
        """Test that recovery procedure documents exist"""
        recovery_dir = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/recovery/recovery-procedures"
        
        procedures = [
            "service-restoration.md",
            "vm-migration.md",
            "storage-failover.md"
        ]
        
        for procedure in procedures:
            procedure_path = recovery_dir / procedure
            assert procedure_path.exists()
            
            with open(procedure_path) as f:
                content = f.read()
            assert len(content) > 100
    
    def test_core_services_configs_exist(self):
        """Test that core service configurations exist"""
        services_dir = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/services"
        
        # Pi-hole
        assert (services_dir / "pihole/pihole-config.conf").exists()
        assert (services_dir / "pihole/custom-dns.list").exists()
        
        # FreeIPA
        assert (services_dir / "freeipa/freeipa-install.sh").exists()
        assert (services_dir / "freeipa/ipa-server.conf").exists()
        
        # NTP
        assert (services_dir / "ntp/ntp.conf").exists()
        
        # Nginx
        assert (services_dir / "nginx/nginx.conf").exists()
        assert (services_dir / "nginx/sites-available/homelab-services.conf").exists()
        
        # Rsyslog
        assert (services_dir / "rsyslog/rsyslog.conf").exists()




class TestPRJHOME002MonitoringConfigs:
    """Test PRJ-HOME-002 Monitoring Stack configuration files
    
    These tests validate the monitoring configurations that were updated
    to use environment variables and service discovery instead of hardcoded values.
    """
    
    # ============================================================================
    # Alertmanager Configuration Tests
    # ============================================================================
    
    def test_alertmanager_config_valid_yaml(self):
        """Test that alertmanager.yml is valid YAML"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/alertmanager/alertmanager.yml"
        assert config_path.exists(), f"Alertmanager config not found at {config_path}"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)
    
    def test_alertmanager_has_required_sections(self):
        """Test that alertmanager.yml has all required top-level sections"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/alertmanager/alertmanager.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Required sections
        assert "global" in config, "Missing 'global' section"
        assert "route" in config, "Missing 'route' section"
        assert "receivers" in config, "Missing 'receivers' section"
    
    def test_alertmanager_global_config(self):
        """Test Alertmanager global configuration for SMTP and resolve timeout"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/alertmanager/alertmanager.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        global_config = config.get("global", {})
        
        # Check SMTP configuration exists
        assert "smtp_from" in global_config
        assert "smtp_smarthost" in global_config
        assert "smtp_auth_username" in global_config
        assert "smtp_auth_password" in global_config
        assert "smtp_require_tls" in global_config
        assert "resolve_timeout" in global_config
        
        # Validate SMTP settings
        assert global_config["smtp_smarthost"] == "smtp.gmail.com:587"
        assert global_config["smtp_require_tls"] is True
    
    def test_alertmanager_uses_env_vars(self):
        """Test that alertmanager.yml uses environment variables instead of hardcoded values"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/alertmanager/alertmanager.yml"
        
        with open(config_path) as f:
            content = f.read()
        
        # Should use environment variables
        assert "${SMTP_USERNAME}" in content, "SMTP_USERNAME env var not used"
        assert "${SMTP_PASSWORD}" in content, "SMTP_PASSWORD env var not used"
        assert "${CRITICAL_EMAIL_TO}" in content, "CRITICAL_EMAIL_TO env var not used"
        assert "${SLACK_WEBHOOK_URL}" in content, "SLACK_WEBHOOK_URL env var not used"
        
        # Should NOT have hardcoded sensitive values
        assert "your-email@gmail.com" not in content, "Found hardcoded email address"
        assert "oncall@homelab.local" not in content, "Found hardcoded email recipient"
    
    def test_alertmanager_route_configuration(self):
        """Test Alertmanager routing configuration"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/alertmanager/alertmanager.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        route = config.get("route", {})
        
        # Check required route fields
        assert "receiver" in route
        assert "group_by" in route
        assert "group_wait" in route
        assert "group_interval" in route
        assert "repeat_interval" in route
        
        # Validate group_by includes key labels
        group_by = route.get("group_by", [])
        assert "alertname" in group_by
        
        # Check for severity-based sub-routes
        routes = route.get("routes", [])
        assert len(routes) > 0, "No sub-routes defined"
        
        # Find critical and warning routes
        critical_route = None
        warning_route = None
        
        for r in routes:
            match = r.get("match", {})
            if match.get("severity") == "critical":
                critical_route = r
            elif match.get("severity") == "warning":
                warning_route = r
        
        assert critical_route is not None, "No critical severity route found"
        assert warning_route is not None, "No warning severity route found"
        
        # Critical alerts should have shorter wait times
        critical_wait = critical_route.get("group_wait", "30s")
        assert critical_wait == "10s", f"Critical alerts should have 10s wait, got {critical_wait}"
    
    def test_alertmanager_inhibition_rules(self):
        """Test Alertmanager inhibition rules to prevent alert storms"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/alertmanager/alertmanager.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        inhibit_rules = config.get("inhibit_rules", [])
        assert len(inhibit_rules) > 0, "No inhibition rules defined"
        
        # Check for node-down inhibition rule
        has_node_down_inhibition = False
        has_critical_inhibition = False
        
        for rule in inhibit_rules:
            source_match = rule.get("source_match", {})
            if "NodeDown" in source_match.get("alertname", ""):
                has_node_down_inhibition = True
            if source_match.get("severity") == "critical":
                has_critical_inhibition = True
        
        assert has_node_down_inhibition, "Missing NodeDown inhibition rule"
        assert has_critical_inhibition, "Missing critical severity inhibition rule"
    
    def test_alertmanager_receivers_configuration(self):
        """Test that all required receivers are properly configured"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/alertmanager/alertmanager.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        receivers = config.get("receivers", [])
        assert len(receivers) > 0, "No receivers configured"
        
        # Collect receiver names
        receiver_names = [r.get("name") for r in receivers]
        
        # Check for required receivers
        assert "critical-alerts" in receiver_names, "Missing critical-alerts receiver"
        assert "slack-general" in receiver_names, "Missing slack-general receiver"
        assert "slack-warnings" in receiver_names, "Missing slack-warnings receiver"
        assert "null" in receiver_names, "Missing null receiver for discarded alerts"
        
        # Verify critical-alerts has both slack and email
        critical_receiver = next((r for r in receivers if r["name"] == "critical-alerts"), None)
        assert critical_receiver is not None
        assert "slack_configs" in critical_receiver, "Critical receiver missing Slack config"
        assert "email_configs" in critical_receiver, "Critical receiver missing email config"
    
    def test_alertmanager_receiver_names_valid(self):
        """Test that all receiver names are valid strings without special characters"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/alertmanager/alertmanager.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        receivers = config.get("receivers", [])
        
        for receiver in receivers:
            name = receiver.get("name")
            assert name is not None, "Receiver missing name"
            assert isinstance(name, str), f"Receiver name is not a string: {name}"
            assert len(name) > 0, "Receiver name is empty"
    
    def test_alertmanager_slack_configs_valid(self):
        """Test that Slack configurations are properly structured"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/alertmanager/alertmanager.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        receivers = config.get("receivers", [])
        
        for receiver in receivers:
            if "slack_configs" in receiver:
                slack_configs = receiver["slack_configs"]
                assert isinstance(slack_configs, list), "slack_configs should be a list"
                
                for slack_config in slack_configs:
                    # Check required fields
                    assert "channel" in slack_config, f"Slack config in {receiver['name']} missing channel"
                    assert slack_config["channel"].startswith("#"), f"Channel should start with # in {receiver['name']}"
                    
                    # Verify send_resolved is set
                    if "send_resolved" in slack_config:
                        assert isinstance(slack_config["send_resolved"], bool)
    
    # ============================================================================
    # Prometheus Configuration Tests
    # ============================================================================
    
    def test_prometheus_config_valid_yaml(self):
        """Test that prometheus.yml is valid YAML"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/prometheus/prometheus.yml"
        assert config_path.exists(), f"Prometheus config not found at {config_path}"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)
    
    def test_prometheus_has_required_sections(self):
        """Test that prometheus.yml has all required sections"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "global" in config, "Missing 'global' section"
        assert "alerting" in config, "Missing 'alerting' section"
        assert "rule_files" in config, "Missing 'rule_files' section"
        assert "scrape_configs" in config, "Missing 'scrape_configs' section"
    
    def test_prometheus_global_config(self):
        """Test Prometheus global configuration"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        global_config = config.get("global", {})
        
        # Check timing settings
        assert "scrape_interval" in global_config
        assert "evaluation_interval" in global_config
        assert "scrape_timeout" in global_config
        
        # Validate intervals are reasonable
        scrape_interval = global_config.get("scrape_interval")
        assert scrape_interval == "15s", f"Expected 15s scrape_interval, got {scrape_interval}"
        
        # Check external labels
        assert "external_labels" in global_config
        external_labels = global_config.get("external_labels", {})
        assert "environment" in external_labels
        assert external_labels["environment"] == "homelab"
    
    def test_prometheus_uses_service_discovery(self):
        """Test that Prometheus uses service names instead of hardcoded IPs"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            content = f.read()
        
        # Should use service discovery
        assert "alertmanager:9093" in content, "Should use 'alertmanager' service name"
        assert "blackbox-exporter:9115" in content, "Should use 'blackbox-exporter' service name"
        
        # Verify old hardcoded IPs are removed
        assert "192.168.40.30:9093" not in content, "Found hardcoded alertmanager IP"
        assert "192.168.40.30:9115" not in content, "Found hardcoded blackbox-exporter IP"
    
    def test_prometheus_alerting_config(self):
        """Test Prometheus alerting configuration"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        alerting = config.get("alerting", {})
        assert "alertmanagers" in alerting
        
        alertmanagers = alerting.get("alertmanagers", [])
        assert len(alertmanagers) > 0, "No alertmanagers configured"
        
        # Check first alertmanager config
        am = alertmanagers[0]
        assert "static_configs" in am or "dns_sd_configs" in am or "kubernetes_sd_configs" in am
        
        if "static_configs" in am:
            static_configs = am["static_configs"]
            targets = static_configs[0].get("targets", [])
            assert len(targets) > 0, "No alertmanager targets defined"
            assert "alertmanager:9093" in targets, "Alertmanager service name not found"
    
    def test_prometheus_scrape_configs_comprehensive(self):
        """Test that Prometheus has comprehensive scrape configurations"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        scrape_configs = config.get("scrape_configs", [])
        assert len(scrape_configs) > 0, "No scrape configs defined"
        
        # Collect job names
        job_names = [sc.get("job_name") for sc in scrape_configs]
        
        # Check for essential jobs
        assert "prometheus" in job_names, "Missing self-monitoring job"
        assert "node_exporter" in job_names, "Missing node_exporter job"
        assert "blackbox_http" in job_names, "Missing blackbox HTTP checks"
    
    def test_prometheus_scrape_configs_have_labels(self):
        """Test that scrape configs have proper labels for organization"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        scrape_configs = config.get("scrape_configs", [])
        
        for sc in scrape_configs:
            job_name = sc.get("job_name")
            
            if "static_configs" in sc:
                for static_config in sc["static_configs"]:
                    targets = static_config.get("targets", [])
                    if len(targets) > 0:
                        labels = static_config.get("labels", {})
                        
                        # Critical services should have tier and criticality labels
                        if "postgres" in job_name.lower():
                            assert "criticality" in labels, f"Job {job_name} missing criticality label"
                            assert labels.get("criticality") == "critical", f"Postgres should be critical"
    
    def test_prometheus_blackbox_relabel_configs(self):
        """Test that blackbox exporter has proper relabel configurations"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        scrape_configs = config.get("scrape_configs", [])
        
        # Find blackbox job
        blackbox_job = next((sc for sc in scrape_configs if "blackbox" in sc.get("job_name", "")), None)
        assert blackbox_job is not None, "Blackbox job not found"
        
        # Check relabel configs
        relabel_configs = blackbox_job.get("relabel_configs", [])
        assert len(relabel_configs) > 0, "No relabel configs for blackbox"
        
        # Verify target relabeling
        has_target_relabel = any(
            rc.get("target_label") == "__param_target" 
            for rc in relabel_configs
        )
        assert has_target_relabel, "Missing __param_target relabel"
        
        # Verify address replacement
        has_address_replacement = any(
            rc.get("target_label") == "__address__" 
            for rc in relabel_configs
        )
        assert has_address_replacement, "Missing __address__ relabel"
    
    def test_prometheus_rule_files_configured(self):
        """Test that rule files are configured"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/prometheus/prometheus.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        rule_files = config.get("rule_files", [])
        assert len(rule_files) > 0, "No rule files configured"
        
        # Should have alerts and recording rules
        has_alerts = any("alert" in rf for rf in rule_files)
        assert has_alerts, "No alert rule files configured"
    
    # ============================================================================
    # Promtail Configuration Tests
    # ============================================================================
    
    def test_promtail_config_valid_yaml(self):
        """Test that promtail-config.yml is valid YAML"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/promtail/promtail-config.yml"
        assert config_path.exists(), f"Promtail config not found at {config_path}"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)
    
    def test_promtail_has_required_sections(self):
        """Test that promtail-config.yml has all required sections"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/promtail/promtail-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "server" in config, "Missing 'server' section"
        assert "positions" in config, "Missing 'positions' section"
        assert "clients" in config, "Missing 'clients' section"
        assert "scrape_configs" in config, "Missing 'scrape_configs' section"
    
    def test_promtail_uses_env_vars_and_service_discovery(self):
        """Test that Promtail uses environment variables and service names"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/promtail/promtail-config.yml"
        
        with open(config_path) as f:
            content = f.read()
        
        # Should use environment variables
        assert "${HOSTNAME}" in content, "HOSTNAME env var not used"
        
        # Should use service discovery for Loki
        assert "loki:3100" in content, "Should use 'loki' service name"
        
        # Should NOT have hardcoded values
        assert "wikijs-vm" not in content, "Found hardcoded hostname"
        assert "192.168.40.30:3100" not in content, "Found hardcoded Loki IP"
    
    def test_promtail_server_config(self):
        """Test Promtail server configuration"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/promtail/promtail-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        server = config.get("server", {})
        
        assert "http_listen_port" in server, "Missing http_listen_port"
        assert isinstance(server["http_listen_port"], int), "Port should be an integer"
        assert server["http_listen_port"] > 0, "Port should be positive"
        
        if "log_level" in server:
            valid_levels = ["debug", "info", "warn", "error"]
            assert server["log_level"] in valid_levels, f"Invalid log level: {server['log_level']}"
    
    def test_promtail_clients_configuration(self):
        """Test Promtail clients configuration"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/promtail/promtail-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        clients = config.get("clients", [])
        assert len(clients) > 0, "No Loki clients configured"
        
        # Check first client
        client = clients[0]
        assert "url" in client, "Client missing URL"
        
        url = client["url"]
        assert "loki" in url.lower(), "Client URL should reference Loki"
        assert "/loki/api/v1/push" in url, "Client URL should have push endpoint"
        
        # Check external labels
        if "external_labels" in client:
            labels = client["external_labels"]
            assert "environment" in labels, "Missing environment label"
    
    def test_promtail_scrape_configs_comprehensive(self):
        """Test that Promtail has comprehensive scrape configurations"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/promtail/promtail-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        scrape_configs = config.get("scrape_configs", [])
        assert len(scrape_configs) > 0, "No scrape configs defined"
        
        # Collect job names
        job_names = [sc.get("job_name") for sc in scrape_configs]
        
        # Check for essential log sources
        assert "system" in job_names or "syslog" in " ".join(job_names), "Missing system logs"
        assert "docker" in " ".join(job_names).lower(), "Missing Docker logs"
    
    def test_promtail_scrape_configs_have_pipelines(self):
        """Test that scrape configs have proper pipeline stages"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/promtail/promtail-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        scrape_configs = config.get("scrape_configs", [])
        
        for sc in scrape_configs:
            job_name = sc.get("job_name")
            
            # Most jobs should have pipeline stages
            if job_name in ["system", "docker", "nginx-access", "nginx-error"]:
                assert "pipeline_stages" in sc, f"Job {job_name} missing pipeline_stages"
                
                pipeline_stages = sc["pipeline_stages"]
                assert len(pipeline_stages) > 0, f"Job {job_name} has empty pipeline_stages"
    
    def test_promtail_pipeline_stages_valid(self):
        """Test that pipeline stages are properly configured"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/promtail/promtail-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        scrape_configs = config.get("scrape_configs", [])
        
        for sc in scrape_configs:
            if "pipeline_stages" in sc:
                pipeline_stages = sc["pipeline_stages"]
                
                for stage in pipeline_stages:
                    # Each stage should have exactly one key
                    stage_keys = list(stage.keys())
                    assert len(stage_keys) > 0, "Pipeline stage is empty"
                    
                    # Valid stage types
                    valid_stages = ["regex", "json", "labels", "timestamp", "output", "match", "drop"]
                    stage_type = stage_keys[0]
                    assert stage_type in valid_stages, f"Invalid pipeline stage type: {stage_type}"
    
    def test_promtail_positions_file_configured(self):
        """Test that positions file is configured"""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/promtail/promtail-config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        positions = config.get("positions", {})
        assert "filename" in positions, "Positions filename not configured"
        assert positions["filename"], "Positions filename is empty"
    
    # ============================================================================
    # Monitoring README Tests
    # ============================================================================
    
    def test_monitoring_readme_exists_and_comprehensive(self):
        """Test that monitoring README exists and is comprehensive"""
        readme_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/README.md"
        assert readme_path.exists(), "Monitoring README not found"
        
        with open(readme_path) as f:
            content = f.read()
        
        # Check for key sections
        assert "# Homelab Monitoring Stack" in content or "Monitoring Stack" in content
        assert "Prometheus" in content
        assert "Grafana" in content
        assert "Loki" in content
        assert "Alertmanager" in content
        
        # Check for environment variables documentation
        assert "SMTP_USERNAME" in content, "SMTP_USERNAME not documented"
        assert "CRITICAL_EMAIL_TO" in content, "CRITICAL_EMAIL_TO not documented"
        assert "HOSTNAME" in content, "HOSTNAME not documented"
        
        # Should be substantial
        assert len(content) > 3000, "README seems too short"
    
    def test_monitoring_readme_deployment_instructions(self):
        """Test that README has deployment instructions"""
        readme_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/README.md"
        
        with open(readme_path) as f:
            content = f.read()
        
        # Should have deployment/setup instructions
        assert "deploy" in content.lower() or "setup" in content.lower() or "install" in content.lower()
        
        # Should reference docker-compose
        assert "docker-compose" in content.lower() or "docker compose" in content.lower()
        
        # Should mention environment variables
        assert ".env" in content or "environment" in content.lower()
    
    def test_monitoring_readme_architecture_diagram(self):
        """Test that README includes architecture information"""
        readme_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/README.md"
        
        with open(readme_path) as f:
            content = f.read()
        
        # Should have architecture section
        assert "architecture" in content.lower() or "diagram" in content.lower()
        
        # Should describe components
        assert "prometheus" in content.lower()
        assert "grafana" in content.lower()
    
    # ============================================================================
    # Integration Tests
    # ============================================================================
    
    def test_alertmanager_references_prometheus_config(self):
        """Test that Alertmanager receiver names match Prometheus alerting config"""
        am_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/alertmanager/alertmanager.yml"
        prom_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/prometheus/prometheus.yml"
        
        with open(am_path) as f:
            am_config = yaml.safe_load(f)
        
        with open(prom_path) as f:
            prom_config = yaml.safe_load(f)
        
        # Get Prometheus alertmanager targets
        alerting = prom_config.get("alerting", {})
        alertmanagers = alerting.get("alertmanagers", [])
        
        assert len(alertmanagers) > 0, "No alertmanagers in Prometheus config"
        
        # Verify the route receiver exists
        route = am_config.get("route", {})
        default_receiver = route.get("receiver")
        
        receiver_names = [r.get("name") for r in am_config.get("receivers", [])]
        assert default_receiver in receiver_names, f"Default receiver '{default_receiver}' not found in receivers list"
    
    def test_config_consistency_across_files(self):
        """Test that environment variables are consistently used across all configs"""
        configs = [
            "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/alertmanager/alertmanager.yml",
            "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/prometheus/prometheus.yml",
            "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/promtail/promtail-config.yml"
        ]
        
        for config_path in configs:
            full_path = BASE_PATH / config_path
            assert full_path.exists(), f"Config not found: {config_path}"
            
            with open(full_path) as f:
                content = f.read()
            
            # All configs should use environment labels consistently
            if "environment" in content.lower():
                # If environment is mentioned, it should be 'homelab'
                assert "homelab" in content.lower(), f"Environment should be 'homelab' in {config_path}"
    
    def test_no_placeholder_values_remain(self):
        """Test that no placeholder values remain in configurations"""
        configs = [
            "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/alertmanager/alertmanager.yml",
            "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/prometheus/prometheus.yml",
            "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/promtail/promtail-config.yml"
        ]
        
        placeholder_patterns = [
            "your-email@",
            "your_",
            "YOUR_",
            "changeme",
            "CHANGEME",
            "example.com",
            "localhost:3100",  # Should use service name
            "192.168.40.30:3100",  # Should use service name
            "192.168.40.30:9093",  # Should use service name
            "wikijs-vm",  # Should use env var
        ]
        
        for config_path in configs:
            full_path = BASE_PATH / config_path
            
            with open(full_path) as f:
                content = f.read()
            
            for pattern in placeholder_patterns:
                assert pattern not in content, f"Found placeholder '{pattern}' in {config_path}"
    
    def test_service_discovery_used_consistently(self):
        """Test that service discovery is used consistently instead of IPs"""
        prom_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/prometheus/prometheus.yml"
        
        with open(prom_path) as f:
            content = f.read()
        
        # Should use service names for internal services
        assert "alertmanager:9093" in content, "Should use alertmanager service name"
        assert "blackbox-exporter:9115" in content, "Should use blackbox-exporter service name"
        
        # May still use IPs for external targets (node exporters)
        # but internal stack services should use service names


class TestDocumentationCompleteness:
    """Test that README files are complete and comprehensive"""
    
    def test_prj_home_001_readme_complete(self):
        """Test that PRJ-HOME-001 README is comprehensive"""
        readme_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/README.md"
        assert readme_path.exists()
        
        with open(readme_path) as f:
            content = f.read()
        
        # Check for key sections
        assert "# PRJ-HOME-001" in content
        assert "pfSense" in content
        assert "UniFi" in content
        assert "VLAN" in content
        assert "Security" in content
        assert len(content) > 2000
    
    def test_prj_home_002_readme_complete(self):
        """Test that PRJ-HOME-002 README is comprehensive"""
        readme_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/README.md"
        assert readme_path.exists()
        
        with open(readme_path) as f:
            content = f.read()
        
        # Check for key sections
        assert "# PRJ-HOME-002" in content
        assert "Proxmox" in content
        assert "Virtualization" in content
        assert "High Availability" in content or "HA" in content
        assert "Backup" in content
        assert len(content) > 3000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])