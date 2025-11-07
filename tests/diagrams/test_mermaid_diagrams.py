"""
Comprehensive tests for Mermaid diagram files.

This test suite validates:
- Mermaid syntax correctness
- Diagram structure and completeness
- Node and edge definitions
- Subgraph organization
- Labels and descriptions
- Technical accuracy
"""

import re
from pathlib import Path
import pytest


BASE_PATH = Path(__file__).parent.parent.parent


@pytest.fixture
def database_diagram_path():
    """Return path to database infrastructure diagram."""
    return BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/assets/diagrams/database-infrastructure.mermaid"


@pytest.fixture
def database_diagram_content(database_diagram_path):
    """Read database diagram content."""
    return database_diagram_path.read_text()


@pytest.fixture
def virtualization_diagram_path():
    """Return path to virtualization architecture diagram."""
    return BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/diagrams/virtualization-architecture.mermaid"


@pytest.fixture
def virtualization_diagram_content(virtualization_diagram_path):
    """Read virtualization diagram content."""
    return virtualization_diagram_path.read_text()


class TestDatabaseInfrastructureDiagram:
    """Test database infrastructure Mermaid diagram."""

    def test_diagram_file_exists(self, database_diagram_path):
        """Verify database diagram file exists."""
        assert database_diagram_path.exists()
        assert database_diagram_path.is_file()

    def test_diagram_not_empty(self, database_diagram_content):
        """Verify diagram has content."""
        assert len(database_diagram_content) > 100

    def test_has_graph_declaration(self, database_diagram_content):
        """Verify diagram starts with graph declaration."""
        assert "graph TB" in database_diagram_content or "graph LR" in database_diagram_content

    def test_has_subgraphs(self, database_diagram_content):
        """Verify diagram uses subgraphs for organization."""
        assert "subgraph" in database_diagram_content
        # Should have multiple subgraphs
        subgraph_count = database_diagram_content.count("subgraph")
        assert subgraph_count >= 3

    def test_includes_internet_layer(self, database_diagram_content):
        """Verify diagram includes Internet layer."""
        assert "Internet" in database_diagram_content
        assert "Users" in database_diagram_content or "End Users" in database_diagram_content

    def test_includes_aws_cloud(self, database_diagram_content):
        """Verify diagram includes AWS Cloud."""
        assert "AWS" in database_diagram_content or "☁️" in database_diagram_content
        assert "us-east-1" in database_diagram_content

    def test_includes_vpc(self, database_diagram_content):
        """Verify diagram includes VPC."""
        assert "VPC" in database_diagram_content
        assert "10.0.0.0/16" in database_diagram_content

    def test_includes_public_subnets(self, database_diagram_content):
        """Verify diagram includes public subnets."""
        assert "Public Subnet" in database_diagram_content
        assert "10.0.1.0/24" in database_diagram_content or "10.0.2.0/24" in database_diagram_content

    def test_includes_private_subnets(self, database_diagram_content):
        """Verify diagram includes private subnets."""
        assert "Private Subnet" in database_diagram_content
        assert "10.0.10" in database_diagram_content or "10.0.11" in database_diagram_content

    def test_includes_database_subnets(self, database_diagram_content):
        """Verify diagram includes database subnets."""
        assert "Database Subnet" in database_diagram_content
        assert "10.0.20" in database_diagram_content or "10.0.21" in database_diagram_content

    def test_includes_load_balancer(self, database_diagram_content):
        """Verify diagram includes Application Load Balancer."""
        assert "ALB" in database_diagram_content or "Load Balancer" in database_diagram_content
        assert "443" in database_diagram_content

    def test_includes_nat_gateway(self, database_diagram_content):
        """Verify diagram includes NAT Gateway."""
        assert "NAT" in database_diagram_content

    def test_includes_app_servers(self, database_diagram_content):
        """Verify diagram includes application servers."""
        assert "App Server" in database_diagram_content or "Application" in database_diagram_content
        assert "ECS" in database_diagram_content or "EC2" in database_diagram_content

    def test_includes_security_groups(self, database_diagram_content):
        """Verify diagram includes security groups."""
        assert "Security Group" in database_diagram_content
        assert "sg-" in database_diagram_content

    def test_includes_rds_instance(self, database_diagram_content):
        """Verify diagram includes RDS instance."""
        assert "RDS" in database_diagram_content
        assert "PostgreSQL" in database_diagram_content
        assert "Primary" in database_diagram_content

    def test_includes_multi_az_configuration(self, database_diagram_content):
        """Verify diagram shows Multi-AZ configuration."""
        assert "Standby" in database_diagram_content or "Multi-AZ" in database_diagram_content
        assert "Replication" in database_diagram_content

    def test_includes_rds_specifications(self, database_diagram_content):
        """Verify diagram includes RDS instance specifications."""
        assert "db.t3" in database_diagram_content
        assert "PostgreSQL" in database_diagram_content
        # Should mention version
        assert re.search(r'PostgreSQL \d+', database_diagram_content)

    def test_includes_storage_details(self, database_diagram_content):
        """Verify diagram includes storage details."""
        assert "Storage" in database_diagram_content or "EBS" in database_diagram_content
        assert "Encrypted" in database_diagram_content
        assert "GB" in database_diagram_content

    def test_includes_monitoring_section(self, database_diagram_content):
        """Verify diagram includes monitoring section."""
        assert "Monitoring" in database_diagram_content or "CloudWatch" in database_diagram_content
        assert "Metrics" in database_diagram_content or "Logs" in database_diagram_content

    def test_includes_cloudwatch_alarms(self, database_diagram_content):
        """Verify diagram mentions CloudWatch alarms."""
        assert "CloudWatch" in database_diagram_content
        assert "Alarm" in database_diagram_content
        assert "CPU" in database_diagram_content or "Storage" in database_diagram_content

    def test_includes_sns_notifications(self, database_diagram_content):
        """Verify diagram includes SNS for notifications."""
        assert "SNS" in database_diagram_content
        assert "Alert" in database_diagram_content or "Notification" in database_diagram_content

    def test_includes_backup_section(self, database_diagram_content):
        """Verify diagram includes backup section."""
        assert "Backup" in database_diagram_content
        assert "Automated" in database_diagram_content or "Snapshot" in database_diagram_content

    def test_includes_backup_retention(self, database_diagram_content):
        """Verify diagram mentions backup retention."""
        assert "retention" in database_diagram_content
        assert "day" in database_diagram_content

    def test_includes_s3_backup_storage(self, database_diagram_content):
        """Verify diagram includes S3 for backup storage."""
        assert "S3" in database_diagram_content

    def test_includes_availability_zones(self, database_diagram_content):
        """Verify diagram mentions availability zones."""
        assert "AZ" in database_diagram_content
        # Should mention at least 2 AZs
        assert "AZ1" in database_diagram_content or "AZ-1" in database_diagram_content
        assert "AZ2" in database_diagram_content or "AZ-2" in database_diagram_content

    def test_includes_failover_details(self, database_diagram_content):
        """Verify diagram mentions failover."""
        assert "Failover" in database_diagram_content or "failover" in database_diagram_content

    def test_includes_port_numbers(self, database_diagram_content):
        """Verify diagram includes relevant port numbers."""
        assert "443" in database_diagram_content  # HTTPS
        assert "5432" in database_diagram_content  # PostgreSQL

    def test_uses_emojis_for_clarity(self, database_diagram_content):
        """Verify diagram uses emojis for visual clarity."""
        # Should have at least some emojis
        emoji_pattern = re.compile(r'[🌐☁️📊💾]')
        assert emoji_pattern.search(database_diagram_content)

    def test_has_proper_node_connections(self, database_diagram_content):
        """Verify diagram has node connections."""
        # Should have arrows showing connections
        assert "-->" in database_diagram_content or "---" in database_diagram_content

    def test_nodes_have_labels(self, database_diagram_content):
        """Verify nodes have descriptive labels."""
        # Check for pattern: NodeID[Label]
        label_pattern = re.compile(r'\w+\[.+\]')
        matches = label_pattern.findall(database_diagram_content)
        assert len(matches) >= 10  # Should have many labeled nodes


class TestVirtualizationArchitectureDiagram:
    """Test virtualization architecture Mermaid diagram."""

    def test_diagram_file_exists(self, virtualization_diagram_path):
        """Verify virtualization diagram file exists."""
        assert virtualization_diagram_path.exists()
        assert virtualization_diagram_path.is_file()

    def test_diagram_not_empty(self, virtualization_diagram_content):
        """Verify diagram has content."""
        assert len(virtualization_diagram_content) > 100

    def test_has_graph_declaration(self, virtualization_diagram_content):
        """Verify diagram starts with graph declaration."""
        assert "graph TB" in virtualization_diagram_content or "graph LR" in virtualization_diagram_content

    def test_has_multiple_subgraphs(self, virtualization_diagram_content):
        """Verify diagram uses subgraphs for organization."""
        subgraph_count = virtualization_diagram_content.count("subgraph")
        # Should have many subgraphs for different layers
        assert subgraph_count >= 5

    def test_includes_management_layer(self, virtualization_diagram_content):
        """Verify diagram includes management layer."""
        assert "Management" in virtualization_diagram_content
        assert "Proxmox" in virtualization_diagram_content
        assert "Web UI" in virtualization_diagram_content or "WebUI" in virtualization_diagram_content

    def test_includes_proxmox_api(self, virtualization_diagram_content):
        """Verify diagram includes Proxmox API."""
        assert "API" in virtualization_diagram_content
        assert "REST" in virtualization_diagram_content or "WebSocket" in virtualization_diagram_content

    def test_includes_proxmox_cluster(self, virtualization_diagram_content):
        """Verify diagram includes Proxmox cluster."""
        assert "Cluster" in virtualization_diagram_content
        assert "HA" in virtualization_diagram_content or "High Availability" in virtualization_diagram_content

    def test_includes_multiple_nodes(self, virtualization_diagram_content):
        """Verify diagram shows multiple Proxmox nodes."""
        assert "Node 1" in virtualization_diagram_content or "Node1" in virtualization_diagram_content
        assert "Node 2" in virtualization_diagram_content or "Node2" in virtualization_diagram_content
        assert "Node 3" in virtualization_diagram_content or "Node3" in virtualization_diagram_content

    def test_includes_corosync(self, virtualization_diagram_content):
        """Verify diagram mentions Corosync for clustering."""
        assert "Corosync" in virtualization_diagram_content
        assert "Quorum" in virtualization_diagram_content

    def test_includes_storage_infrastructure(self, virtualization_diagram_content):
        """Verify diagram includes storage infrastructure."""
        assert "Storage" in virtualization_diagram_content
        assert "Ceph" in virtualization_diagram_content or "LVM" in virtualization_diagram_content

    def test_includes_ceph_distributed_storage(self, virtualization_diagram_content):
        """Verify diagram includes Ceph distributed storage."""
        assert "Ceph" in virtualization_diagram_content
        assert "OSD" in virtualization_diagram_content
        assert "RBD" in virtualization_diagram_content

    def test_includes_truenas(self, virtualization_diagram_content):
        """Verify diagram includes TrueNAS."""
        assert "TrueNAS" in virtualization_diagram_content
        assert "ZFS" in virtualization_diagram_content

    def test_includes_nfs_shares(self, virtualization_diagram_content):
        """Verify diagram includes NFS shares."""
        assert "NFS" in virtualization_diagram_content

    def test_includes_proxmox_backup_server(self, virtualization_diagram_content):
        """Verify diagram includes Proxmox Backup Server."""
        assert "Backup" in virtualization_diagram_content
        assert "PBS" in virtualization_diagram_content or "Proxmox Backup" in virtualization_diagram_content

    def test_includes_core_services(self, virtualization_diagram_content):
        """Verify diagram includes core infrastructure services."""
        assert "Services" in virtualization_diagram_content or "Infrastructure" in virtualization_diagram_content

    def test_includes_identity_management(self, virtualization_diagram_content):
        """Verify diagram includes identity management."""
        assert "FreeIPA" in virtualization_diagram_content or "LDAP" in virtualization_diagram_content

    def test_includes_dns_services(self, virtualization_diagram_content):
        """Verify diagram includes DNS services."""
        assert "DNS" in virtualization_diagram_content
        assert "Pi-hole" in virtualization_diagram_content or "pihole" in virtualization_diagram_content

    def test_includes_reverse_proxy(self, virtualization_diagram_content):
        """Verify diagram includes reverse proxy."""
        assert "Nginx" in virtualization_diagram_content or "Proxy" in virtualization_diagram_content
        assert "SSL" in virtualization_diagram_content

    def test_includes_logging(self, virtualization_diagram_content):
        """Verify diagram includes centralized logging."""
        assert "Log" in virtualization_diagram_content or "Syslog" in virtualization_diagram_content
        assert "Rsyslog" in virtualization_diagram_content

    def test_includes_ntp(self, virtualization_diagram_content):
        """Verify diagram includes NTP for time sync."""
        assert "NTP" in virtualization_diagram_content

    def test_includes_application_vms(self, virtualization_diagram_content):
        """Verify diagram includes application VMs."""
        assert "Application" in virtualization_diagram_content or "VM" in virtualization_diagram_content

    def test_includes_automation(self, virtualization_diagram_content):
        """Verify diagram includes automation tooling."""
        assert "Automation" in virtualization_diagram_content or "IaC" in virtualization_diagram_content
        assert "Ansible" in virtualization_diagram_content or "Terraform" in virtualization_diagram_content

    def test_includes_network_integration(self, virtualization_diagram_content):
        """Verify diagram includes network integration."""
        assert "Network" in virtualization_diagram_content
        assert "VLAN" in virtualization_diagram_content
        assert "192.168" in virtualization_diagram_content

    def test_includes_pfsense(self, virtualization_diagram_content):
        """Verify diagram mentions pfSense."""
        assert "pfSense" in virtualization_diagram_content or "Firewall" in virtualization_diagram_content

    def test_includes_ip_addresses(self, virtualization_diagram_content):
        """Verify diagram includes IP addresses."""
        # Should have VLAN 40 addresses
        assert "192.168.40" in virtualization_diagram_content

    def test_includes_port_numbers(self, virtualization_diagram_content):
        """Verify diagram includes relevant ports."""
        assert "8006" in virtualization_diagram_content  # Proxmox Web UI
        assert "8007" in virtualization_diagram_content or "8443" in virtualization_diagram_content

    def test_includes_operational_scripts(self, virtualization_diagram_content):
        """Verify diagram mentions operational scripts."""
        if "Scripts" in virtualization_diagram_content:
            assert ".sh" in virtualization_diagram_content

    def test_has_node_connections(self, virtualization_diagram_content):
        """Verify diagram shows connections between components."""
        # Should have various connection types
        assert "-->" in virtualization_diagram_content or "<-->" in virtualization_diagram_content

    def test_shows_data_flow(self, virtualization_diagram_content):
        """Verify diagram shows data flow between components."""
        # Look for labeled connections
        connection_pattern = re.compile(r'-->\|.+\|')
        matches = connection_pattern.findall(virtualization_diagram_content)
        assert len(matches) >= 5

    def test_uses_emojis_for_clarity(self, virtualization_diagram_content):
        """Verify diagram uses emojis for visual organization."""
        emoji_pattern = re.compile(r'[🖥️⚙️💾🌐🤖📦🛠️]')
        assert emoji_pattern.search(virtualization_diagram_content)

    def test_includes_udp_ports(self, virtualization_diagram_content):
        """Verify diagram mentions UDP ports for Corosync."""
        if "Corosync" in virtualization_diagram_content:
            assert "UDP" in virtualization_diagram_content
            assert "5404" in virtualization_diagram_content or "5405" in virtualization_diagram_content


class TestDiagramQuality:
    """Test diagram quality and best practices."""

    def test_database_diagram_line_count(self, database_diagram_content):
        """Verify database diagram has reasonable complexity."""
        line_count = len(database_diagram_content.split('\n'))
        # Should be detailed but not overwhelming
        assert 50 < line_count < 500

    def test_virtualization_diagram_line_count(self, virtualization_diagram_content):
        """Verify virtualization diagram has reasonable complexity."""
        line_count = len(virtualization_diagram_content.split('\n'))
        # Should be comprehensive
        assert 100 < line_count < 500

    def test_diagrams_use_consistent_formatting(self, database_diagram_content, virtualization_diagram_content):
        """Verify diagrams use consistent formatting."""
        for content in [database_diagram_content, virtualization_diagram_content]:
            # Should have proper indentation
            lines = content.split('\n')
            indented_lines = [l for l in lines if l.startswith('    ') or l.startswith('  ')]
            # Most lines should be indented for subgraphs
            assert len(indented_lines) > len(lines) * 0.3

    def test_diagrams_have_descriptive_names(self, database_diagram_content, virtualization_diagram_content):
        """Verify node names are descriptive."""
        for content in [database_diagram_content, virtualization_diagram_content]:
            # Should avoid single-letter node names
            node_pattern = re.compile(r'\b[A-Z]{1}\[')
            single_letter_nodes = node_pattern.findall(content)
            # Allow some, but not many
            assert len(single_letter_nodes) < 5

    def test_diagrams_document_technical_specs(self, database_diagram_content, virtualization_diagram_content):
        """Verify diagrams include technical specifications."""
        # Database diagram should have instance types, versions
        assert "db.t3" in database_diagram_content
        assert re.search(r'\d+\.\d+', database_diagram_content)  # Version numbers
        
        # Virtualization diagram should have IP addresses, ports
        assert "192.168" in virtualization_diagram_content
        assert re.search(r':\d{4}', virtualization_diagram_content)  # Ports


if __name__ == "__main__":
    pytest.main([__file__, "-v"])