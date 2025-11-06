"""
Comprehensive tests for operational runbook documentation.

This test suite validates:
- Markdown syntax and structure
- Runbook completeness and organization
- Required sections and procedures
- Alert response procedures
- Troubleshooting guides
- Emergency contacts and escalation
- Technical accuracy and actionable steps
"""

import re
from pathlib import Path
import pytest


BASE_PATH = Path(__file__).parent.parent.parent


@pytest.fixture
def observability_runbook_path():
    """Return path to observability runbook."""
    return BASE_PATH / "projects/01-sde-devops/PRJ-SDE-002/assets/runbooks/OPERATIONAL_RUNBOOK.md"


@pytest.fixture
def observability_runbook_content(observability_runbook_path):
    """Read observability runbook content."""
    return observability_runbook_path.read_text()


@pytest.fixture
def network_runbook_path():
    """Return path to network operations runbook."""
    return BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/runbooks/NETWORK_OPERATIONS_RUNBOOK.md"


@pytest.fixture
def network_runbook_content(network_runbook_path):
    """Read network runbook content."""
    return network_runbook_path.read_text()


class TestObservabilityRunbook:
    """Test observability & backups operational runbook."""

    def test_runbook_file_exists(self, observability_runbook_path):
        """Verify runbook file exists."""
        assert observability_runbook_path.exists()
        assert observability_runbook_path.is_file()

    def test_runbook_not_empty(self, observability_runbook_content):
        """Verify runbook has substantial content."""
        assert len(observability_runbook_content) > 5000

    def test_has_title_and_metadata(self, observability_runbook_content):
        """Verify runbook has title and metadata."""
        assert "# " in observability_runbook_content
        assert "Operational Runbook" in observability_runbook_content
        assert "Version:" in observability_runbook_content
        assert "Last Updated:" in observability_runbook_content
        assert "Maintainer:" in observability_runbook_content

    def test_has_table_of_contents(self, observability_runbook_content):
        """Verify runbook has table of contents."""
        assert "## Table of Contents" in observability_runbook_content or "## Contents" in observability_runbook_content

    def test_has_overview_section(self, observability_runbook_content):
        """Verify runbook has overview section."""
        assert "## Overview" in observability_runbook_content
        assert "### Purpose" in observability_runbook_content
        assert "### Scope" in observability_runbook_content

    def test_defines_service_criticality(self, observability_runbook_content):
        """Verify runbook defines service criticality."""
        assert "Criticality" in observability_runbook_content
        assert "RTO" in observability_runbook_content
        assert "RPO" in observability_runbook_content

    def test_includes_key_metrics(self, observability_runbook_content):
        """Verify runbook includes key metrics."""
        assert "Uptime" in observability_runbook_content
        assert "Alert Response" in observability_runbook_content or "Response Time" in observability_runbook_content

    def test_has_service_architecture_section(self, observability_runbook_content):
        """Verify runbook documents service architecture."""
        assert "## Service Architecture" in observability_runbook_content or "## Architecture" in observability_runbook_content
        assert "### Component Overview" in observability_runbook_content or "Component" in observability_runbook_content

    def test_documents_prometheus(self, observability_runbook_content):
        """Verify runbook documents Prometheus."""
        assert "Prometheus" in observability_runbook_content
        assert "9090" in observability_runbook_content  # Default port

    def test_documents_grafana(self, observability_runbook_content):
        """Verify runbook documents Grafana."""
        assert "Grafana" in observability_runbook_content
        assert "3000" in observability_runbook_content  # Default port

    def test_documents_loki(self, observability_runbook_content):
        """Verify runbook documents Loki."""
        assert "Loki" in observability_runbook_content
        assert "3100" in observability_runbook_content  # Default port

    def test_documents_alertmanager(self, observability_runbook_content):
        """Verify runbook documents Alertmanager."""
        assert "Alertmanager" in observability_runbook_content or "Alert Manager" in observability_runbook_content

    def test_documents_backup_server(self, observability_runbook_content):
        """Verify runbook documents Proxmox Backup Server."""
        assert "Backup" in observability_runbook_content
        assert "PBS" in observability_runbook_content or "Proxmox Backup" in observability_runbook_content

    def test_includes_component_table(self, observability_runbook_content):
        """Verify runbook includes component table with details."""
        # Should have a table with components
        assert "|" in observability_runbook_content
        assert "Host" in observability_runbook_content or "IP" in observability_runbook_content
        assert "Port" in observability_runbook_content

    def test_includes_status_check_commands(self, observability_runbook_content):
        """Verify runbook includes health check commands."""
        assert "curl" in observability_runbook_content
        assert "http" in observability_runbook_content

    def test_has_alert_response_section(self, observability_runbook_content):
        """Verify runbook has alert response procedures."""
        assert "## Alert Response" in observability_runbook_content or "Alert" in observability_runbook_content
        assert "### Alert:" in observability_runbook_content or "Alert:" in observability_runbook_content

    def test_includes_hostdown_alert(self, observability_runbook_content):
        """Verify runbook includes HostDown alert procedure."""
        assert "HostDown" in observability_runbook_content or "Host Down" in observability_runbook_content
        assert "Trigger Condition" in observability_runbook_content or "trigger" in observability_runbook_content.lower()
        assert "Severity" in observability_runbook_content

    def test_alert_procedures_have_immediate_actions(self, observability_runbook_content):
        """Verify alert procedures include immediate actions."""
        assert "Immediate Actions" in observability_runbook_content or "Actions" in observability_runbook_content
        assert "```bash" in observability_runbook_content or "```shell" in observability_runbook_content

    def test_includes_troubleshooting_commands(self, observability_runbook_content):
        """Verify runbook includes troubleshooting commands."""
        # Should have various diagnostic commands
        assert "ping" in observability_runbook_content or "curl" in observability_runbook_content
        commands = ["ssh", "systemctl", "journalctl", "docker"]
        assert any(cmd in observability_runbook_content for cmd in commands)

    def test_has_troubleshooting_guide(self, observability_runbook_content):
        """Verify runbook has troubleshooting guide."""
        assert "## Troubleshooting" in observability_runbook_content or "Troubleshoot" in observability_runbook_content

    def test_has_maintenance_procedures(self, observability_runbook_content):
        """Verify runbook has maintenance procedures."""
        assert "## Maintenance" in observability_runbook_content

    def test_has_backup_operations_section(self, observability_runbook_content):
        """Verify runbook has backup operations section."""
        assert "## Backup" in observability_runbook_content
        assert "Backup Operations" in observability_runbook_content or "backup" in observability_runbook_content.lower()

    def test_has_service_recovery_section(self, observability_runbook_content):
        """Verify runbook has service recovery procedures."""
        assert "## Service Recovery" in observability_runbook_content or "Recovery" in observability_runbook_content

    def test_has_emergency_contacts(self, observability_runbook_content):
        """Verify runbook has emergency contacts section."""
        assert "## Emergency" in observability_runbook_content or "Contact" in observability_runbook_content

    def test_includes_ip_addresses(self, observability_runbook_content):
        """Verify runbook includes relevant IP addresses."""
        ip_pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        matches = ip_pattern.findall(observability_runbook_content)
        assert len(matches) >= 3

    def test_includes_code_blocks(self, observability_runbook_content):
        """Verify runbook includes code blocks for commands."""
        assert "```" in observability_runbook_content
        # Should have multiple code blocks
        code_block_count = observability_runbook_content.count("```")
        assert code_block_count >= 10  # At least 5 code blocks (start and end markers)

    def test_procedures_are_numbered(self, observability_runbook_content):
        """Verify procedures use numbered steps."""
        # Should have numbered lists
        numbered_pattern = re.compile(r'^\d+\. ', re.MULTILINE)
        matches = numbered_pattern.findall(observability_runbook_content)
        assert len(matches) >= 10


class TestNetworkOperationsRunbook:
    """Test network infrastructure operational runbook."""

    def test_runbook_file_exists(self, network_runbook_path):
        """Verify runbook file exists."""
        assert network_runbook_path.exists()
        assert network_runbook_path.is_file()

    def test_runbook_not_empty(self, network_runbook_content):
        """Verify runbook has substantial content."""
        assert len(network_runbook_content) > 5000

    def test_has_title_and_metadata(self, network_runbook_content):
        """Verify runbook has title and metadata."""
        assert "# Network" in network_runbook_content
        assert "Operational Runbook" in network_runbook_content
        assert "Version:" in network_runbook_content
        assert "Last Updated:" in network_runbook_content
        assert "Maintainer:" in network_runbook_content

    def test_has_table_of_contents(self, network_runbook_content):
        """Verify runbook has table of contents."""
        assert "## Table of Contents" in network_runbook_content or "## Contents" in network_runbook_content

    def test_has_overview_section(self, network_runbook_content):
        """Verify runbook has overview section."""
        assert "## Overview" in network_runbook_content
        assert "### Purpose" in network_runbook_content
        assert "### Scope" in network_runbook_content

    def test_defines_critical_infrastructure(self, network_runbook_content):
        """Verify runbook defines network as critical."""
        assert "Criticality" in network_runbook_content
        assert "P0" in network_runbook_content or "Critical" in network_runbook_content
        assert "RTO" in network_runbook_content
        assert "RPO" in network_runbook_content

    def test_has_network_architecture_section(self, network_runbook_content):
        """Verify runbook documents network architecture."""
        assert "## Network Architecture" in network_runbook_content or "## Architecture" in network_runbook_content

    def test_documents_vlan_summary(self, network_runbook_content):
        """Verify runbook documents VLAN summary."""
        assert "VLAN" in network_runbook_content
        assert "### VLAN" in network_runbook_content or "VLAN Summary" in network_runbook_content

    def test_includes_vlan_table(self, network_runbook_content):
        """Verify runbook includes VLAN table."""
        assert "|" in network_runbook_content
        assert "VLAN" in network_runbook_content
        assert "Network" in network_runbook_content
        assert "Gateway" in network_runbook_content

    def test_documents_vlan_10_trusted(self, network_runbook_content):
        """Verify runbook documents VLAN 10 (Trusted)."""
        assert "VLAN 10" in network_runbook_content or "10" in network_runbook_content
        assert "192.168.1.0/24" in network_runbook_content
        assert "Trusted" in network_runbook_content

    def test_documents_vlan_20_iot(self, network_runbook_content):
        """Verify runbook documents VLAN 20 (IoT)."""
        assert "VLAN 20" in network_runbook_content or "20" in network_runbook_content
        assert "192.168.20" in network_runbook_content
        assert "IoT" in network_runbook_content

    def test_documents_vlan_30_guest(self, network_runbook_content):
        """Verify runbook documents VLAN 30 (Guest)."""
        assert "VLAN 30" in network_runbook_content or "30" in network_runbook_content
        assert "192.168.30" in network_runbook_content
        assert "Guest" in network_runbook_content

    def test_documents_vlan_40_servers(self, network_runbook_content):
        """Verify runbook documents VLAN 40 (Servers)."""
        assert "VLAN 40" in network_runbook_content or "40" in network_runbook_content
        assert "192.168.40" in network_runbook_content
        assert "Server" in network_runbook_content

    def test_documents_vlan_50_dmz(self, network_runbook_content):
        """Verify runbook documents VLAN 50 (DMZ)."""
        assert "VLAN 50" in network_runbook_content or "50" in network_runbook_content
        assert "192.168.50" in network_runbook_content
        assert "DMZ" in network_runbook_content

    def test_documents_pfsense(self, network_runbook_content):
        """Verify runbook documents pfSense firewall."""
        assert "pfSense" in network_runbook_content
        assert "192.168.1.1" in network_runbook_content
        assert "Firewall" in network_runbook_content

    def test_documents_unifi_equipment(self, network_runbook_content):
        """Verify runbook documents UniFi equipment."""
        assert "UniFi" in network_runbook_content
        assert "Switch" in network_runbook_content or "Access Point" in network_runbook_content

    def test_includes_critical_services_table(self, network_runbook_content):
        """Verify runbook includes critical services table."""
        assert "Service" in network_runbook_content
        assert "IP Address" in network_runbook_content
        assert "Port" in network_runbook_content
        assert "Status Check" in network_runbook_content

    def test_documents_dns_service(self, network_runbook_content):
        """Verify runbook documents DNS service."""
        assert "DNS" in network_runbook_content
        assert "53" in network_runbook_content
        assert "Unbound" in network_runbook_content or "dig" in network_runbook_content

    def test_documents_dhcp_service(self, network_runbook_content):
        """Verify runbook documents DHCP service."""
        assert "DHCP" in network_runbook_content
        assert "67" in network_runbook_content

    def test_documents_openvpn(self, network_runbook_content):
        """Verify runbook documents OpenVPN."""
        assert "OpenVPN" in network_runbook_content or "VPN" in network_runbook_content
        assert "1194" in network_runbook_content

    def test_documents_firewall_rules(self, network_runbook_content):
        """Verify runbook documents firewall rules."""
        assert "Firewall Rules" in network_runbook_content or "Inter-VLAN" in network_runbook_content
        assert "ALLOW" in network_runbook_content
        assert "DENY" in network_runbook_content

    def test_has_incident_response_section(self, network_runbook_content):
        """Verify runbook has incident response section."""
        assert "## Incident Response" in network_runbook_content or "Incident" in network_runbook_content

    def test_includes_network_outage_procedure(self, network_runbook_content):
        """Verify runbook includes network outage procedure."""
        assert "Network Outage" in network_runbook_content or "Outage" in network_runbook_content
        assert "Symptoms" in network_runbook_content or "symptoms" in network_runbook_content

    def test_outage_procedures_have_immediate_steps(self, network_runbook_content):
        """Verify outage procedures have immediate steps."""
        # Should have step-by-step procedures
        numbered_pattern = re.compile(r'^\d+\. ', re.MULTILINE)
        matches = numbered_pattern.findall(network_runbook_content)
        assert len(matches) >= 15

    def test_has_troubleshooting_guide(self, network_runbook_content):
        """Verify runbook has troubleshooting guide."""
        assert "## Troubleshooting" in network_runbook_content

    def test_has_maintenance_procedures(self, network_runbook_content):
        """Verify runbook has maintenance procedures."""
        assert "## Maintenance" in network_runbook_content

    def test_documents_firmware_updates(self, network_runbook_content):
        """Verify runbook documents firmware updates."""
        if "Maintenance" in network_runbook_content:
            assert "firmware" in network_runbook_content.lower() or "update" in network_runbook_content.lower()

    def test_has_security_procedures(self, network_runbook_content):
        """Verify runbook has security procedures."""
        assert "## Security" in network_runbook_content
        assert "Security Procedures" in network_runbook_content or "security" in network_runbook_content.lower()

    def test_documents_ips_system(self, network_runbook_content):
        """Verify runbook documents IPS system."""
        assert "Suricata" in network_runbook_content or "IPS" in network_runbook_content

    def test_has_emergency_recovery_section(self, network_runbook_content):
        """Verify runbook has emergency recovery section."""
        assert "## Emergency Recovery" in network_runbook_content or "Recovery" in network_runbook_content

    def test_has_reference_information(self, network_runbook_content):
        """Verify runbook has reference information."""
        assert "## Reference" in network_runbook_content or "Reference" in network_runbook_content

    def test_includes_diagnostic_commands(self, network_runbook_content):
        """Verify runbook includes network diagnostic commands."""
        commands = ["ping", "traceroute", "dig", "nslookup", "ssh"]
        found_commands = sum(1 for cmd in commands if cmd in network_runbook_content)
        assert found_commands >= 3

    def test_includes_code_blocks(self, network_runbook_content):
        """Verify runbook includes code blocks."""
        assert "```" in network_runbook_content
        code_block_count = network_runbook_content.count("```")
        assert code_block_count >= 10

    def test_documents_backup_procedures(self, network_runbook_content):
        """Verify runbook documents configuration backup."""
        assert "backup" in network_runbook_content.lower() or "Backup" in network_runbook_content

    def test_includes_pfsense_webgui_url(self, network_runbook_content):
        """Verify runbook includes pfSense WebGUI URL."""
        assert "https://192.168.1.1" in network_runbook_content or "192.168.1.1" in network_runbook_content
        assert "443" in network_runbook_content

    def test_includes_port_numbers(self, network_runbook_content):
        """Verify runbook includes relevant port numbers."""
        ports = ["53", "67", "443", "1194"]
        found_ports = sum(1 for port in ports if port in network_runbook_content)
        assert found_ports >= 3

    def test_documents_escalation_path(self, network_runbook_content):
        """Verify runbook documents escalation path."""
        if "Emergency" in network_runbook_content or "Contact" in network_runbook_content:
            # Should have some form of escalation or contact info
            assert "Slack" in network_runbook_content or "email" in network_runbook_content or "@" in network_runbook_content


class TestRunbookQuality:
    """Test runbook quality and best practices."""

    def test_runbooks_are_comprehensive(self, observability_runbook_content, network_runbook_content):
        """Verify runbooks are comprehensive."""
        # Both runbooks should be substantial
        assert len(observability_runbook_content) > 5000
        assert len(network_runbook_content) > 5000

    def test_runbooks_use_proper_markdown_headers(self, observability_runbook_content, network_runbook_content):
        """Verify runbooks use proper markdown header hierarchy."""
        for content in [observability_runbook_content, network_runbook_content]:
            # Should have various header levels
            assert "# " in content  # H1
            assert "## " in content  # H2
            assert "### " in content  # H3

    def test_runbooks_include_actionable_procedures(self, observability_runbook_content, network_runbook_content):
        """Verify runbooks include actionable procedures."""
        for content in [observability_runbook_content, network_runbook_content]:
            # Should have code blocks with commands
            assert "```bash" in content or "```shell" in content or "```" in content
            # Should have numbered steps
            numbered_pattern = re.compile(r'^\d+\. ', re.MULTILINE)
            matches = numbered_pattern.findall(content)
            assert len(matches) >= 10

    def test_runbooks_document_severity_levels(self, observability_runbook_content, network_runbook_content):
        """Verify runbooks document severity levels."""
        for content in [observability_runbook_content, network_runbook_content]:
            # Should mention severity
            assert "Severity" in content or "Critical" in content

    def test_runbooks_include_response_times(self, observability_runbook_content, network_runbook_content):
        """Verify runbooks include response time SLAs."""
        for content in [observability_runbook_content, network_runbook_content]:
            # Should mention response times
            assert "minutes" in content or "hour" in content
            # Should have time-based SLAs
            time_pattern = re.compile(r'<\s*\d+\s*(minute|hour)')
            assert time_pattern.search(content)

    def test_runbooks_use_tables_for_organization(self, observability_runbook_content, network_runbook_content):
        """Verify runbooks use tables for organization."""
        for content in [observability_runbook_content, network_runbook_content]:
            # Should have markdown tables
            assert "|" in content
            # Should have multiple tables
            table_headers = content.count("|---")
            assert table_headers >= 2

    def test_runbooks_provide_examples(self, observability_runbook_content, network_runbook_content):
        """Verify runbooks provide command examples."""
        for content in [observability_runbook_content, network_runbook_content]:
            # Should have code examples
            code_blocks = content.count("```")
            assert code_blocks >= 10  # At least 5 code blocks

    def test_runbooks_are_well_structured(self, observability_runbook_content, network_runbook_content):
        """Verify runbooks follow consistent structure."""
        required_sections = ["Overview", "Architecture", "Troubleshooting", "Maintenance"]
        for content in [observability_runbook_content, network_runbook_content]:
            found_sections = sum(1 for section in required_sections if section in content)
            assert found_sections >= 3

    def test_runbooks_document_prerequisites(self, observability_runbook_content, network_runbook_content):
        """Verify runbooks document prerequisites or requirements."""
        for content in [observability_runbook_content, network_runbook_content]:
            # Should mention access requirements
            assert "ssh" in content.lower() or "access" in content.lower() or "credential" in content.lower()

    def test_runbooks_include_health_checks(self, observability_runbook_content, network_runbook_content):
        """Verify runbooks include health check procedures."""
        for content in [observability_runbook_content, network_runbook_content]:
            # Should have health check commands
            assert "curl" in content or "ping" in content or "status" in content.lower()

    def test_runbooks_avoid_hardcoded_secrets(self, observability_runbook_content, network_runbook_content):
        """Verify runbooks don't contain hardcoded credentials."""
        for content in [observability_runbook_content, network_runbook_content]:
            # Should not have obvious passwords
            suspicious = ["password:", "passwd:", "apikey:"]
            for pattern in suspicious:
                if pattern in content.lower():
                    # Check if it's in a code example or placeholder
                    lines_with_pattern = [line for line in content.split('\n') if pattern in line.lower()]
                    for line in lines_with_pattern:
                        # Allow if it's clearly a placeholder
                        assert any(p in line.lower() for p in ["<", ">", "your", "example", "***"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])