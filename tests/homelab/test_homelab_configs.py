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
