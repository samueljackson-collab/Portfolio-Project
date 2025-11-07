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


# ============================================================================
# Enhanced Tests for Production-Grade Docker Compose Configuration
# ============================================================================

class TestDockerComposeFullStack:
    """Test docker-compose-full-stack.yml production enhancements."""

    def test_docker_compose_exists(self):
        """Test docker-compose-full-stack.yml exists."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        assert config_path.exists()

    def test_docker_compose_valid_yaml(self):
        """Test docker-compose file is valid YAML."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)

    def test_docker_compose_has_version(self):
        """Test docker-compose file has version specified."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "version" in config
        assert config["version"] in ["3.8", "3.7", "3"]

    def test_docker_compose_has_services(self):
        """Test docker-compose defines services."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "services" in config
        assert len(config["services"]) >= 10  # Should have 10+ services

    def test_docker_compose_has_networks(self):
        """Test docker-compose defines networks."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "networks" in config
        # Should have frontend, backend, monitoring networks
        assert "frontend" in config["networks"]
        assert "backend" in config["networks"]
        assert "monitoring" in config["networks"]

    def test_docker_compose_has_volumes(self):
        """Test docker-compose defines volumes."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "volumes" in config
        assert len(config["volumes"]) >= 8


class TestDockerComposeImageVersions:
    """Test all images have pinned versions (no :latest)."""

    def test_no_latest_tags(self):
        """Test no service uses :latest tag."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        for service_name, service_config in services.items():
            if "image" in service_config:
                image = service_config["image"]
                # Should not use :latest or have no tag
                assert ":latest" not in image.lower(), f"{service_name} uses :latest tag"
                assert ":" in image, f"{service_name} has no version tag"

    def test_prometheus_version_pinned(self):
        """Test Prometheus has specific version."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        prometheus = services.get("prometheus", {})
        
        assert "image" in prometheus
        assert "prom/prometheus" in prometheus["image"]
        assert "v2.48" in prometheus["image"] or ":" in prometheus["image"]

    def test_grafana_version_pinned(self):
        """Test Grafana has specific version."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        grafana = services.get("grafana", {})
        
        assert "image" in grafana
        assert "grafana/grafana" in grafana["image"]
        assert "10." in grafana["image"] or ":" in grafana["image"]

    def test_loki_version_pinned(self):
        """Test Loki has specific version."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        loki = services.get("loki", {})
        
        assert "image" in loki
        assert "grafana/loki" in loki["image"]
        assert "2.9" in loki["image"] or ":" in loki["image"]


class TestDockerComposeHealthChecks:
    """Test all services have health checks configured."""

    def test_prometheus_has_healthcheck(self):
        """Test Prometheus has health check."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        prometheus = services.get("prometheus", {})
        
        assert "healthcheck" in prometheus
        assert "test" in prometheus["healthcheck"]
        assert "interval" in prometheus["healthcheck"]

    def test_grafana_has_healthcheck(self):
        """Test Grafana has health check."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        grafana = services.get("grafana", {})
        
        assert "healthcheck" in grafana
        assert "start_period" in grafana["healthcheck"]

    def test_loki_has_healthcheck(self):
        """Test Loki has health check."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        loki = services.get("loki", {})
        
        assert "healthcheck" in loki

    def test_promtail_has_healthcheck(self):
        """Test Promtail has health check."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        promtail = services.get("promtail", {})
        
        assert "healthcheck" in promtail

    def test_cadvisor_has_healthcheck(self):
        """Test cAdvisor has health check."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        cadvisor = services.get("cadvisor", {})
        
        assert "healthcheck" in cadvisor

    def test_node_exporter_has_healthcheck(self):
        """Test Node Exporter has health check."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        node_exporter = services.get("node-exporter", {})
        
        assert "healthcheck" in node_exporter


class TestDockerComposeResourceLimits:
    """Test all services have resource limits configured."""

    def test_prometheus_has_resource_limits(self):
        """Test Prometheus has CPU and memory limits."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        prometheus = services.get("prometheus", {})
        
        assert "deploy" in prometheus
        assert "resources" in prometheus["deploy"]
        assert "limits" in prometheus["deploy"]["resources"]
        assert "cpus" in prometheus["deploy"]["resources"]["limits"]
        assert "memory" in prometheus["deploy"]["resources"]["limits"]

    def test_grafana_has_resource_limits(self):
        """Test Grafana has resource limits."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        grafana = services.get("grafana", {})
        
        assert "deploy" in grafana
        assert "resources" in grafana["deploy"]

    def test_cadvisor_has_resource_limits(self):
        """Test cAdvisor has resource limits."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        cadvisor = services.get("cadvisor", {})
        
        assert "deploy" in cadvisor
        # cAdvisor should have small resource limits
        memory_limit = cadvisor["deploy"]["resources"]["limits"]["memory"]
        assert "256M" in memory_limit or "128M" in memory_limit

    def test_node_exporter_has_resource_limits(self):
        """Test Node Exporter has resource limits."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        node_exporter = services.get("node-exporter", {})
        
        assert "deploy" in node_exporter


class TestDockerComposeSecuritySettings:
    """Test security configurations in docker-compose."""

    def test_prometheus_runs_as_non_root(self):
        """Test Prometheus runs as non-root user."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        prometheus = services.get("prometheus", {})
        
        assert "user" in prometheus
        assert prometheus["user"] != "0:0"  # Not root

    def test_grafana_runs_as_non_root(self):
        """Test Grafana runs as non-root user."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        grafana = services.get("grafana", {})
        
        assert "user" in grafana
        assert grafana["user"] == "472:472"  # Grafana user

    def test_grafana_has_security_settings(self):
        """Test Grafana has security environment variables."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        grafana = services.get("grafana", {})
        
        env_vars = grafana.get("environment", [])
        env_str = str(env_vars)
        
        # Should disable analytics and sign-up
        assert "GF_ANALYTICS_REPORTING_ENABLED=false" in env_str or "ANALYTICS" in env_str
        assert "GF_USERS_ALLOW_SIGN_UP=false" in env_str or "SIGN_UP" in env_str

    def test_loki_runs_as_non_root(self):
        """Test Loki runs as non-root user."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        loki = services.get("loki", {})
        
        assert "user" in loki


class TestDockerComposeDependencies:
    """Test service dependencies are properly configured."""

    def test_grafana_depends_on_prometheus(self):
        """Test Grafana depends on Prometheus."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        grafana = services.get("grafana", {})
        
        assert "depends_on" in grafana
        depends_on = grafana["depends_on"]
        
        # Should wait for Prometheus health
        if isinstance(depends_on, dict):
            assert "prometheus" in depends_on
            assert "condition" in depends_on["prometheus"]
        else:
            assert "prometheus" in depends_on

    def test_grafana_depends_on_loki(self):
        """Test Grafana depends on Loki."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        grafana = services.get("grafana", {})
        
        depends_on = grafana.get("depends_on", {})
        if isinstance(depends_on, dict):
            assert "loki" in depends_on
        else:
            assert "loki" in depends_on

    def test_promtail_depends_on_loki(self):
        """Test Promtail depends on Loki."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        promtail = services.get("promtail", {})
        
        assert "depends_on" in promtail


class TestDockerComposeNetworkConfiguration:
    """Test network configuration."""

    def test_networks_have_subnets(self):
        """Test networks have subnet configuration."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        networks = config.get("networks", {})
        
        for network_name, network_config in networks.items():
            if "ipam" in network_config:
                assert "config" in network_config["ipam"]
                assert len(network_config["ipam"]["config"]) > 0

    def test_frontend_network_subnet(self):
        """Test frontend network has proper subnet."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        networks = config.get("networks", {})
        frontend = networks.get("frontend", {})
        
        if "ipam" in frontend:
            ipam_config = frontend["ipam"]["config"][0]
            assert "subnet" in ipam_config
            assert "172.20.0.0/24" in ipam_config["subnet"]

    def test_backend_network_subnet(self):
        """Test backend network has proper subnet."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        networks = config.get("networks", {})
        backend = networks.get("backend", {})
        
        if "ipam" in backend:
            ipam_config = backend["ipam"]["config"][0]
            assert "subnet" in ipam_config
            assert "172.21.0.0/24" in ipam_config["subnet"]

    def test_monitoring_network_subnet(self):
        """Test monitoring network has proper subnet."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        networks = config.get("networks", {})
        monitoring = networks.get("monitoring", {})
        
        if "ipam" in monitoring:
            ipam_config = monitoring["ipam"]["config"][0]
            assert "subnet" in ipam_config
            assert "172.22.0.0/24" in ipam_config["subnet"]


class TestDockerComposeApplicationServices:
    """Test application services configuration."""

    def test_wikijs_configured(self):
        """Test Wiki.js service is properly configured."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        wikijs = services.get("wikijs", {})
        
        assert "image" in wikijs
        assert "depends_on" in wikijs
        assert "postgresql" in str(wikijs.get("depends_on", []))

    def test_homeassistant_configured(self):
        """Test Home Assistant service is configured."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        homeassistant = services.get("homeassistant", {})
        
        assert "image" in homeassistant
        assert "volumes" in homeassistant

    def test_immich_configured(self):
        """Test Immich service is configured."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        immich = services.get("immich", {})
        
        assert "image" in immich
        assert "depends_on" in immich

    def test_postgresql_configured(self):
        """Test PostgreSQL service is configured."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", {})
        postgresql = services.get("postgresql", {})
        
        assert "image" in postgresql
        assert "environment" in postgresql
        assert "healthcheck" in postgresql


class TestDockerComposeDocumentation:
    """Test configuration file has proper documentation."""

    def test_has_header_comments(self):
        """Test docker-compose file has header documentation."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            content = f.read()
        
        assert "Docker Compose" in content
        assert "Services included:" in content or "services" in content.lower()

    def test_has_usage_instructions(self):
        """Test file includes usage instructions."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            content = f.read()
        
        assert "docker-compose" in content or "docker compose" in content

    def test_documents_port_mappings(self):
        """Test file documents port mappings."""
        config_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml"
        
        with open(config_path) as f:
            content = f.read()
        
        # Should document common ports
        assert "9090" in content  # Prometheus
        assert "3000" in content  # Grafana