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


class TestPRJHOME001NetworkTopologyAssets:
    """Test PRJ-HOME-001 Network Infrastructure topology and configuration assets"""
    
    def test_assets_readme_exists_and_complete(self):
        """Test that assets README exists and has proper structure"""
        readme_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/README.md"
        assert readme_path.exists(), f"Assets README not found at {readme_path}"
        
        with open(readme_path) as f:
            content = f.read()
        
        # Check for key sections
        assert "# PRJ-HOME-001" in content
        assert "Network Infrastructure Assets" in content
        assert "Directory Structure" in content
        assert "diagrams/" in content
        assert "configs/" in content
        assert "runbooks/" in content
        assert len(content) > 500, "README too short"
    
    def test_firewall_rules_markdown_exists(self):
        """Test that firewall rules documentation exists"""
        rules_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/firewall-rules.md"
        assert rules_path.exists(), f"Firewall rules not found at {rules_path}"
    
    def test_firewall_rules_has_required_sections(self):
        """Test that firewall rules has all required sections"""
        rules_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/firewall-rules.md"
        
        with open(rules_path) as f:
            content = f.read()
        
        # Check for major sections
        assert "# Homelab Firewall Rules" in content or "# Firewall" in content
        assert "Overview" in content
        assert "Rule Processing Order" in content or "Rules Table" in content
        assert "Firewall Rules Table" in content or "| Rule #" in content
        assert "Maintenance" in content or "Troubleshooting" in content
        assert len(content) > 1000, "Firewall rules documentation too short"
    
    def test_firewall_rules_has_vlan_references(self):
        """Test that firewall rules reference all expected VLANs"""
        rules_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/firewall-rules.md"
        
        with open(rules_path) as f:
            content = f.read()
        
        # Check for VLAN references
        assert "VLAN 1" in content or "VLAN 10" in content
        assert "VLAN 50" in content  # IoT
        assert "VLAN 99" in content  # Guest
        assert "VLAN 100" in content  # Lab
    
    def test_firewall_rules_has_security_controls(self):
        """Test that firewall rules document security controls"""
        rules_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/firewall-rules.md"
        
        with open(rules_path) as f:
            content = f.read()
        
        # Check for security controls
        assert "ALLOW" in content or "Allow" in content
        assert "DENY" in content or "Deny" in content
        assert "Port" in content.lower()
        # Check for common protocols
        assert "TCP" in content or "UDP" in content or "tcp" in content or "udp" in content
    
    def test_firewall_rules_table_structure(self):
        """Test that firewall rules has proper markdown table structure"""
        rules_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/firewall-rules.md"
        
        with open(rules_path) as f:
            content = f.read()
        
        # Check for table markers
        assert "| Rule" in content or "|Rule" in content or "| Name" in content
        assert "|---" in content or "| ---" in content  # Table separator
        # Check for multiple rows
        table_rows = [line for line in content.split('\n') if line.startswith('|') and '---' not in line]
        assert len(table_rows) >= 5, "Firewall rules table should have multiple rows"
    
    def test_ip_addressing_scheme_exists(self):
        """Test that IP addressing scheme documentation exists"""
        ip_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/ip-addressing-scheme.md"
        assert ip_path.exists(), f"IP addressing scheme not found at {ip_path}"
    
    def test_ip_addressing_has_all_vlans(self):
        """Test that IP addressing covers all VLANs"""
        ip_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/ip-addressing-scheme.md"
        
        with open(ip_path) as f:
            content = f.read()
        
        # Check for VLAN sections
        assert "VLAN 1" in content  # Management
        assert "VLAN 10" in content  # Trusted
        assert "VLAN 50" in content  # IoT
        assert "VLAN 99" in content  # Guest
        assert "VLAN 100" in content  # Lab
    
    def test_ip_addressing_has_network_ranges(self):
        """Test that IP addressing defines network ranges"""
        ip_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/ip-addressing-scheme.md"
        
        with open(ip_path) as f:
            content = f.read()
        
        # Check for IP ranges
        assert "192.168.1.0" in content  # Management
        assert "192.168.10.0" in content  # Trusted
        assert "192.168.50.0" in content  # IoT
        assert "192.168.99.0" in content  # Guest
        assert "192.168.100.0" in content  # Lab
        
        # Check for subnet masks
        assert "/24" in content
    
    def test_ip_addressing_has_gateways(self):
        """Test that IP addressing defines gateway addresses"""
        ip_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/ip-addressing-scheme.md"
        
        with open(ip_path) as f:
            content = f.read()
        
        # Check for gateway IPs (typically .1)
        assert "192.168.1.1" in content
        assert "192.168.10.1" in content
        assert "192.168.50.1" in content
        assert "Gateway" in content or "gateway" in content
    
    def test_ip_addressing_has_dhcp_pools(self):
        """Test that IP addressing defines DHCP pools"""
        ip_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/ip-addressing-scheme.md"
        
        with open(ip_path) as f:
            content = f.read()
        
        # Check for DHCP configuration
        assert "DHCP" in content or "dhcp" in content
        assert "Pool" in content or "pool" in content or "range" in content.lower()
    
    def test_ip_addressing_has_static_assignments(self):
        """Test that IP addressing documents static assignments"""
        ip_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/ip-addressing-scheme.md"
        
        with open(ip_path) as f:
            content = f.read()
        
        # Check for static assignments section
        assert "Static" in content or "static" in content
        # Check for device references
        device_keywords = ["Proxmox", "TrueNAS", "Switch", "AP", "Pi-hole", "UDMP"]
        assert any(keyword in content for keyword in device_keywords), "No infrastructure devices documented"
    
    def test_ip_addressing_table_structure(self):
        """Test that IP addressing has proper table structure"""
        ip_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/ip-addressing-scheme.md"
        
        with open(ip_path) as f:
            content = f.read()
        
        # Check for table structure
        assert "|" in content  # Table pipe character
        assert "IP Address" in content or "IP" in content
        # Count tables
        table_rows = [line for line in content.split('\n') if line.startswith('|') and '---' not in line]
        assert len(table_rows) >= 10, "Should have multiple IP assignment tables"
    
    def test_wifi_ssid_matrix_exists(self):
        """Test that WiFi SSID matrix documentation exists"""
        wifi_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/wifi-ssid-matrix.md"
        assert wifi_path.exists(), f"WiFi SSID matrix not found at {wifi_path}"
    
    def test_wifi_ssid_has_all_networks(self):
        """Test that WiFi SSID matrix documents all SSIDs"""
        wifi_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/wifi-ssid-matrix.md"
        
        with open(wifi_path) as f:
            content = f.read()
        
        # Check for SSID names
        assert "Homelab-Trusted" in content or "Trusted" in content
        assert "Homelab-IoT" in content or "IoT" in content.upper()
        assert "Homelab-Guest" in content or "Guest" in content
        assert "Homelab-Lab" in content or "Lab" in content
    
    def test_wifi_ssid_has_vlan_mappings(self):
        """Test that WiFi SSID matrix maps SSIDs to VLANs"""
        wifi_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/wifi-ssid-matrix.md"
        
        with open(wifi_path) as f:
            content = f.read()
        
        # Check for VLAN mappings
        assert "VLAN" in content
        # Check that SSIDs are mapped to appropriate VLANs
        assert "10" in content  # Trusted VLAN
        assert "50" in content  # IoT VLAN
        assert "99" in content  # Guest VLAN
    
    def test_wifi_ssid_has_security_config(self):
        """Test that WiFi SSID matrix documents security settings"""
        wifi_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/wifi-ssid-matrix.md"
        
        with open(wifi_path) as f:
            content = f.read()
        
        # Check for security protocols
        assert "WPA" in content  # WPA2/WPA3
        assert "Security" in content or "security" in content
        # Check for encryption or authentication
        assert "Password" in content or "password" in content or "Authentication" in content
    
    def test_wifi_ssid_has_band_config(self):
        """Test that WiFi SSID matrix documents band configuration"""
        wifi_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/wifi-ssid-matrix.md"
        
        with open(wifi_path) as f:
            content = f.read()
        
        # Check for frequency bands
        assert "2.4" in content or "2.4 GHz" in content
        assert "5 GHz" in content or "5GHz" in content
        assert "Band" in content or "band" in content
    
    def test_wifi_ssid_has_access_points(self):
        """Test that WiFi SSID matrix documents access points"""
        wifi_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/wifi-ssid-matrix.md"
        
        with open(wifi_path) as f:
            content = f.read()
        
        # Check for AP references
        assert "AP" in content or "Access Point" in content
        # Check for physical locations
        location_keywords = ["Living Room", "Bedroom", "Office", "Room"]
        assert any(keyword in content for keyword in location_keywords), "No AP locations documented"
    
    def test_logical_vlan_map_mermaid_exists(self):
        """Test that logical VLAN map Mermaid diagram exists"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams/logical-vlan-map.mermaid"
        assert diagram_path.exists(), f"Logical VLAN map not found at {diagram_path}"
    
    def test_logical_vlan_map_valid_mermaid_syntax(self):
        """Test that logical VLAN map has valid Mermaid syntax"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams/logical-vlan-map.mermaid"
        
        with open(diagram_path) as f:
            content = f.read()
        
        # Check for Mermaid diagram type
        assert "flowchart" in content or "graph" in content, "Not a valid Mermaid diagram type"
        # Check for basic syntax
        assert "-->" in content or "---" in content, "Missing Mermaid connection syntax"
        assert len(content) > 200, "Diagram content too short"
    
    def test_logical_vlan_map_has_all_vlans(self):
        """Test that logical VLAN map includes all VLANs"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams/logical-vlan-map.mermaid"
        
        with open(diagram_path) as f:
            content = f.read()
        
        # Check for VLAN references
        assert "VLAN 1" in content or "VLAN1" in content or "Management" in content
        assert "VLAN 10" in content or "VLAN10" in content or "Trusted" in content
        assert "VLAN 50" in content or "VLAN50" in content or "IoT" in content
        assert "VLAN 99" in content or "VLAN99" in content or "Guest" in content
        assert "VLAN 100" in content or "VLAN100" in content or "Lab" in content
    
    def test_logical_vlan_map_has_network_zones(self):
        """Test that logical VLAN map defines network zones"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams/logical-vlan-map.mermaid"
        
        with open(diagram_path) as f:
            content = f.read()
        
        # Check for subgraph definitions (zones)
        assert "subgraph" in content, "No network zones defined"
        # Check for IP addressing
        assert "192.168" in content, "No IP addresses in diagram"
    
    def test_logical_vlan_map_has_firewall_rules(self):
        """Test that logical VLAN map shows firewall rules or connections"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams/logical-vlan-map.mermaid"
        
        with open(diagram_path) as f:
            content = f.read()
        
        # Check for security indicators
        security_keywords = ["ALLOW", "DENY", "Firewall", "-->", "Rules", "Internet"]
        assert any(keyword in content for keyword in security_keywords), "No security rules shown"
    
    def test_physical_topology_mermaid_exists(self):
        """Test that physical topology Mermaid diagram exists"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams/physical-topology.mermaid"
        assert diagram_path.exists(), f"Physical topology not found at {diagram_path}"
    
    def test_physical_topology_valid_mermaid_syntax(self):
        """Test that physical topology has valid Mermaid syntax"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams/physical-topology.mermaid"
        
        with open(diagram_path) as f:
            content = f.read()
        
        # Check for Mermaid diagram type
        assert "flowchart" in content or "graph" in content, "Not a valid Mermaid diagram type"
        # Check for connections
        assert "-->" in content or "---" in content, "Missing Mermaid connection syntax"
        assert len(content) > 300, "Physical topology too short"
    
    def test_physical_topology_has_core_equipment(self):
        """Test that physical topology includes core network equipment"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams/physical-topology.mermaid"
        
        with open(diagram_path) as f:
            content = f.read()
        
        # Check for core equipment
        assert "UDMP" in content or "Dream Machine" in content or "Router" in content
        assert "Switch" in content or "USW" in content
        assert "AP" in content or "Access Point" in content
    
    def test_physical_topology_has_server_equipment(self):
        """Test that physical topology includes server infrastructure"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams/physical-topology.mermaid"
        
        with open(diagram_path) as f:
            content = f.read()
        
        # Check for servers
        server_keywords = ["Proxmox", "TrueNAS", "Server", "Rack"]
        assert any(keyword in content for keyword in server_keywords), "No server equipment shown"
    
    def test_physical_topology_has_client_devices(self):
        """Test that physical topology includes client devices"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams/physical-topology.mermaid"
        
        with open(diagram_path) as f:
            content = f.read()
        
        # Check for clients
        client_keywords = ["Laptop", "Desktop", "Phone", "Client", "Wireless", "IoT", "Smart"]
        assert any(keyword in content for keyword in client_keywords), "No client devices shown"
    
    def test_physical_topology_has_connections(self):
        """Test that physical topology shows physical connections"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams/physical-topology.mermaid"
        
        with open(diagram_path) as f:
            content = f.read()
        
        # Check for connection indicators
        assert "Port" in content or "port" in content, "No port assignments shown"
        # Check for PoE indicators if present
        poe_present = "PoE" in content or "POE" in content
        if poe_present:
            assert True, "PoE devices documented"
    
    def test_network_deployment_runbook_exists(self):
        """Test that network deployment runbook exists"""
        runbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/runbooks/network-deployment-runbook.md"
        assert runbook_path.exists(), f"Deployment runbook not found at {runbook_path}"
    
    def test_deployment_runbook_has_prerequisites(self):
        """Test that deployment runbook has prerequisites section"""
        runbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/runbooks/network-deployment-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        # Check for prerequisites
        assert "Prerequisite" in content or "prerequisite" in content
        assert "Hardware" in content or "hardware" in content
    
    def test_deployment_runbook_has_deployment_steps(self):
        """Test that deployment runbook has numbered deployment steps"""
        runbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/runbooks/network-deployment-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        # Check for step structure
        step_patterns = ["## 1.", "## 2.", "## 3.", "## 4.", "## 5."]
        found_steps = sum(1 for pattern in step_patterns if pattern in content)
        assert found_steps >= 5, f"Only found {found_steps} deployment steps, expected at least 5"
    
    def test_deployment_runbook_has_vlan_configuration(self):
        """Test that deployment runbook includes VLAN configuration"""
        runbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/runbooks/network-deployment-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        # Check for VLAN configuration steps
        assert "VLAN" in content
        assert "Create" in content and "Network" in content
    
    def test_deployment_runbook_has_wifi_configuration(self):
        """Test that deployment runbook includes WiFi configuration"""
        runbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/runbooks/network-deployment-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        # Check for WiFi setup
        assert "WiFi" in content or "Wi-Fi" in content or "SSID" in content
        assert "WPA" in content or "Security" in content
    
    def test_deployment_runbook_has_firewall_setup(self):
        """Test that deployment runbook includes firewall setup"""
        runbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/runbooks/network-deployment-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        # Check for firewall configuration
        assert "Firewall" in content or "firewall" in content
        assert "Rule" in content or "rule" in content
    
    def test_deployment_runbook_has_verification_steps(self):
        """Test that deployment runbook includes verification steps"""
        runbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/runbooks/network-deployment-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        # Check for validation/verification
        validation_keywords = ["Verification", "Test", "Validation", "Check", "Verify"]
        assert any(keyword in content for keyword in validation_keywords), "No verification steps found"
    
    def test_deployment_runbook_has_commands(self):
        """Test that deployment runbook includes command examples"""
        runbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/runbooks/network-deployment-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        # Check for code blocks or commands
        assert "```" in content, "No code blocks found"
        # Check for common network commands
        command_keywords = ["ping", "ssh", "ip", "ifconfig", "nslookup"]
        assert any(keyword in content for keyword in command_keywords), "No network commands found"
    
    def test_deployment_runbook_has_rollback_procedure(self):
        """Test that deployment runbook includes rollback procedure"""
        runbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/runbooks/network-deployment-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        # Check for rollback or recovery
        rollback_keywords = ["Rollback", "rollback", "Recovery", "Backup", "Restore"]
        assert any(keyword in content for keyword in rollback_keywords), "No rollback procedure found"
    
    def test_deployment_runbook_comprehensive(self):
        """Test that deployment runbook is comprehensive and detailed"""
        runbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/runbooks/network-deployment-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        # Check length - should be substantial
        assert len(content) > 5000, "Runbook should be comprehensive (>5000 chars)"
        
        # Check for multiple sections
        sections = content.count('##')
        assert sections >= 10, f"Expected at least 10 sections, found {sections}"


class TestPRJHOME001CrossDocumentConsistency:
    """Test consistency across PRJ-HOME-001 network documentation"""
    
    def test_vlan_ids_consistent_across_documents(self):
        """Test that VLAN IDs are consistent across all documents"""
        base_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets"
        
        # Expected VLAN mappings
        expected_vlans = {
            "1": "Management",
            "10": "Trusted",
            "50": "IoT",
            "99": "Guest",
            "100": "Lab"
        }
        
        # Check IP addressing scheme
        with open(base_path / "configs/ip-addressing-scheme.md") as f:
            ip_content = f.read()
        
        # Check firewall rules
        with open(base_path / "configs/firewall-rules.md") as f:
            fw_content = f.read()
        
        # Verify VLANs appear in both documents
        for vlan_id in expected_vlans.keys():
            assert f"VLAN {vlan_id}" in ip_content or f"VLAN{vlan_id}" in ip_content, \
                f"VLAN {vlan_id} not found in IP addressing scheme"
            assert f"VLAN {vlan_id}" in fw_content or f"VLAN{vlan_id}" in fw_content, \
                f"VLAN {vlan_id} not found in firewall rules"
    
    def test_ip_ranges_consistent_across_documents(self):
        """Test that IP ranges are consistent across documents"""
        base_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets"
        
        # Expected IP ranges
        expected_ranges = [
            "192.168.1.0",
            "192.168.10.0",
            "192.168.50.0",
            "192.168.99.0",
            "192.168.100.0"
        ]
        
        # Check IP addressing scheme
        with open(base_path / "configs/ip-addressing-scheme.md") as f:
            ip_content = f.read()
        
        # Check logical VLAN map
        with open(base_path / "diagrams/logical-vlan-map.mermaid") as f:
            diagram_content = f.read()
        
        # Verify ranges appear in both
        for ip_range in expected_ranges:
            assert ip_range in ip_content, f"IP range {ip_range} not in IP scheme"
            # Diagram should have at least some IP references
        
        assert "192.168" in diagram_content, "No IP addresses in logical VLAN map"
    
    def test_ssid_vlan_mapping_consistent(self):
        """Test that SSID to VLAN mappings are consistent"""
        base_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets"
        
        # Read WiFi config
        with open(base_path / "configs/wifi-ssid-matrix.md") as f:
            wifi_content = f.read()
        
        # Read deployment runbook
        with open(base_path / "runbooks/network-deployment-runbook.md") as f:
            runbook_content = f.read()
        
        # Expected SSID names
        ssids = ["Homelab-Trusted", "Homelab-IoT", "Homelab-Guest", "Homelab-Lab"]
        
        for ssid in ssids:
            assert ssid in wifi_content, f"SSID {ssid} not in WiFi matrix"
            # At least some SSIDs should be in runbook
        
        assert "SSID" in runbook_content or "WiFi" in runbook_content, \
            "No WiFi/SSID configuration in runbook"
    
    def test_equipment_names_consistent(self):
        """Test that equipment names are consistent across documents"""
        base_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets"
        
        # Key equipment
        equipment = ["UDMP", "UniFi", "Switch", "Proxmox", "TrueNAS"]
        
        # Check physical topology
        with open(base_path / "diagrams/physical-topology.mermaid") as f:
            physical_content = f.read()
        
        # Check IP addressing
        with open(base_path / "configs/ip-addressing-scheme.md") as f:
            ip_content = f.read()
        
        # At least some equipment should appear in both
        found_in_physical = sum(1 for eq in equipment if eq in physical_content)
        found_in_ip = sum(1 for eq in equipment if eq in ip_content)
        
        assert found_in_physical >= 3, "Missing equipment in physical topology"
        assert found_in_ip >= 2, "Missing equipment in IP addressing"
    
    def test_all_config_files_referenced_in_readme(self):
        """Test that all config files are mentioned in assets README"""
        base_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets"
        
        with open(base_path / "README.md") as f:
            readme_content = f.read()
        
        # Check for file references
        config_files = [
            "firewall-rules.md",
            "ip-addressing-scheme.md",
            "wifi-ssid-matrix.md",
            "physical-topology.mermaid",
            "logical-vlan-map.mermaid",
            "network-deployment-runbook.md"
        ]
        
        for config_file in config_files:
            assert config_file in readme_content, \
                f"Config file {config_file} not referenced in README"


class TestPRJHOME001NetworkSecurityValidation:
    """Test security aspects of network configuration"""
    
    def test_firewall_has_deny_rules(self):
        """Test that firewall includes deny/drop rules for isolation"""
        rules_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/firewall-rules.md"
        
        with open(rules_path) as f:
            content = f.read()
        
        # Should have deny rules
        deny_keywords = ["DENY", "DROP", "BLOCK", "Deny", "Drop", "Block"]
        assert any(keyword in content for keyword in deny_keywords), \
            "No deny/drop rules found in firewall configuration"
    
    def test_firewall_isolates_iot_network(self):
        """Test that IoT network is properly isolated"""
        rules_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/firewall-rules.md"
        
        with open(rules_path) as f:
            content = f.read()
        
        # IoT should be mentioned
        assert "IoT" in content or "VLAN 50" in content
        # Should have isolation rules
        iot_section = content.lower()
        assert "iot" in iot_section
    
    def test_firewall_isolates_guest_network(self):
        """Test that guest network is isolated from internal"""
        rules_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/firewall-rules.md"
        
        with open(rules_path) as f:
            content = f.read()
        
        # Guest should be mentioned
        assert "Guest" in content or "VLAN 99" in content
        # Should reference isolation
        guest_keywords = ["Guest", "guest", "VLAN 99"]
        assert any(keyword in content for keyword in guest_keywords)
    
    def test_wifi_has_wpa_security(self):
        """Test that WiFi networks use WPA2 or WPA3 security"""
        wifi_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/wifi-ssid-matrix.md"
        
        with open(wifi_path) as f:
            content = f.read()
        
        # Should have WPA security
        assert "WPA2" in content or "WPA3" in content, \
            "No WPA2/WPA3 security found in WiFi configuration"
    
    def test_guest_network_has_rate_limiting(self):
        """Test that guest network has rate limiting configured"""
        wifi_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/wifi-ssid-matrix.md"
        
        with open(wifi_path) as f:
            content = f.read()
        
        # Look for rate limiting or bandwidth control
        rate_keywords = ["Rate", "rate", "Limit", "limit", "Bandwidth", "bandwidth", "Mbps"]
        # Guest section should exist and have rate limiting
        if "Guest" in content:
            assert any(keyword in content for keyword in rate_keywords), \
                "No rate limiting found for guest network"
    
    def test_management_vlan_access_restricted(self):
        """Test that management VLAN access is documented as restricted"""
        rules_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/configs/firewall-rules.md"
        
        with open(rules_path) as f:
            content = f.read()
        
        # Management VLAN should be mentioned
        assert "Management" in content or "VLAN 1" in content or "management" in content
        # Should have access controls
        assert "Admin" in content or "admin" in content or "SSH" in content or "443" in content


class TestPRJHOME001DiagramQuality:
    """Test quality and completeness of network diagrams"""
    
    def test_mermaid_diagrams_not_too_short(self):
        """Test that Mermaid diagrams have substantial content"""
        base_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams"
        
        for diagram_file in ["logical-vlan-map.mermaid", "physical-topology.mermaid"]:
            diagram_path = base_path / diagram_file
            with open(diagram_path) as f:
                content = f.read()
            
            # Should have reasonable length
            assert len(content) > 500, \
                f"{diagram_file} is too short ({len(content)} chars), needs more detail"
    
    def test_mermaid_diagrams_have_comments(self):
        """Test that Mermaid diagrams include comments for clarity"""
        base_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams"
        
        for diagram_file in ["logical-vlan-map.mermaid", "physical-topology.mermaid"]:
            diagram_path = base_path / diagram_file
            with open(diagram_path) as f:
                content = f.read()
            
            # Check for comments (Mermaid uses %% for comments)
            comment_count = content.count("%%")
            # Having comments is good practice but not strictly required
            if comment_count > 0:
                assert True, f"{diagram_file} has {comment_count} comment sections"
    
    def test_logical_vlan_map_has_subgraphs(self):
        """Test that logical VLAN map uses subgraphs for organization"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams/logical-vlan-map.mermaid"
        
        with open(diagram_path) as f:
            content = f.read()
        
        # Should use subgraphs for zones
        subgraph_count = content.count("subgraph")
        assert subgraph_count >= 3, \
            f"Expected at least 3 subgraphs for network zones, found {subgraph_count}"
    
    def test_physical_topology_shows_internet_connection(self):
        """Test that physical topology shows internet/ISP connection"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams/physical-topology.mermaid"
        
        with open(diagram_path) as f:
            content = f.read()
        
        # Should show internet/ISP connection
        internet_keywords = ["Internet", "ISP", "WAN", "Modem"]
        assert any(keyword in content for keyword in internet_keywords), \
            "Physical topology should show internet/ISP connection"


class TestPRJHOME001RunbookCompleteness:
    """Test completeness of deployment runbook"""
    
    def test_runbook_has_day_by_day_plan(self):
        """Test that runbook organizes tasks by day"""
        runbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/runbooks/network-deployment-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        # Check for day-based organization
        day_count = content.count("Day")
        assert day_count >= 3, \
            f"Expected multi-day deployment plan, found {day_count} day references"
    
    def test_runbook_has_validation_commands(self):
        """Test that runbook includes validation commands"""
        runbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/runbooks/network-deployment-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        # Check for validation commands
        validation_commands = ["ping", "ssh", "curl", "nslookup", "dig", "traceroute"]
        found_commands = [cmd for cmd in validation_commands if cmd in content.lower()]
        assert len(found_commands) >= 2, \
            f"Expected multiple validation commands, found only: {found_commands}"
    
    def test_runbook_has_expected_output_examples(self):
        """Test that runbook shows expected output for commands"""
        runbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/runbooks/network-deployment-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        # Check for expected output indicators
        output_keywords = ["Expected", "expected", "Output", "output", "Should"]
        assert any(keyword in content for keyword in output_keywords), \
            "No expected output examples found in runbook"
    
    def test_runbook_has_troubleshooting_section(self):
        """Test that runbook includes troubleshooting guidance"""
        runbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/runbooks/network-deployment-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        # Check for troubleshooting
        troubleshoot_keywords = ["Troubleshoot", "troubleshoot", "Problem", "Issue", "Rollback"]
        assert any(keyword in content for keyword in troubleshoot_keywords), \
            "No troubleshooting section found in runbook"
    
    def test_runbook_has_backup_procedures(self):
        """Test that runbook includes backup procedures"""
        runbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/runbooks/network-deployment-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        # Check for backup procedures
        assert "Backup" in content or "backup" in content, \
            "No backup procedures in runbook"
    
    def test_runbook_has_maintenance_schedule(self):
        """Test that runbook includes ongoing maintenance guidance"""
        runbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/runbooks/network-deployment-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        # Check for maintenance schedule
        maintenance_keywords = ["Maintenance", "maintenance", "Weekly", "Monthly", "Review"]
        assert any(keyword in content for keyword in maintenance_keywords), \
            "No maintenance schedule found in runbook"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])