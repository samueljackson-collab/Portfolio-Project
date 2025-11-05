"""Validation tests for Markdown documentation and diagrams"""
import pytest
from pathlib import Path
import re

BASE_PATH = Path(__file__).parent.parent.parent

class TestVLANAssignmentsMarkdown:
    """Test VLAN assignments documentation"""
    
    def test_vlan_assignments_file_exists(self):
        """Test that vlan-assignments.md exists"""
        doc_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/documentation/vlan-assignments.md"
        assert doc_path.exists(), f"Documentation not found at {doc_path}"
    
    def test_vlan_assignments_has_title(self):
        """Test that document has a title"""
        doc_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/documentation/vlan-assignments.md"
        
        with open(doc_path) as f:
            content = f.read()
        
        # Should start with a heading
        assert content.startswith("#"), "Document should start with a markdown heading"
        assert "VLAN" in content.split('\n')[0]
    
    def test_vlan_assignments_has_vlan_definitions(self):
        """Test that document defines VLANs"""
        doc_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/documentation/vlan-assignments.md"
        
        with open(doc_path) as f:
            content = f.read()
        
        # Should contain VLAN definitions
        assert "VLAN 10" in content or "VLAN10" in content
        assert "VLAN 20" in content or "VLAN20" in content
        assert "Management" in content or "Servers" in content
    
    def test_vlan_assignments_has_network_cidr(self):
        """Test that document includes network CIDR"""
        doc_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/documentation/vlan-assignments.md"
        
        with open(doc_path) as f:
            content = f.read()
        
        # Should contain CIDR notation
        cidr_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}'
        assert re.search(cidr_pattern, content), "Document should contain CIDR notation"
    
    def test_vlan_assignments_has_firewall_rules(self):
        """Test that document includes firewall rules"""
        doc_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/documentation/vlan-assignments.md"
        
        with open(doc_path) as f:
            content = f.read()
        
        # Should mention firewall rules
        assert "firewall" in content.lower() or "rules" in content.lower()
    
    def test_vlan_assignments_has_sanitization_notes(self):
        """Test that document includes sanitization guidelines"""
        doc_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/documentation/vlan-assignments.md"
        
        with open(doc_path) as f:
            content = f.read()
        
        # Should have security/sanitization notes
        assert "Sanitization" in content or "sanitization" in content.lower()
    
    def test_vlan_assignments_structure(self):
        """Test document structure and completeness"""
        doc_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/documentation/vlan-assignments.md"
        
        with open(doc_path) as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Should have multiple sections
        headings = [line for line in lines if line.startswith('#')]
        assert len(headings) >= 1, "Document should have at least one heading"
        
        # Should have substantive content
        non_empty_lines = [line for line in lines if line.strip()]
        assert len(non_empty_lines) >= 10, "Document should have substantial content"

class TestNetworkTopologyMermaid:
    """Test network topology Mermaid diagram"""
    
    def test_network_topology_file_exists(self):
        """Test that network-topology.mmd exists"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams/network-topology.mmd"
        assert diagram_path.exists(), f"Diagram not found at {diagram_path}"
    
    def test_mermaid_diagram_syntax(self):
        """Test basic Mermaid syntax"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams/network-topology.mmd"
        
        with open(diagram_path) as f:
            content = f.read()
        
        # Should start with graph declaration
        assert content.strip().startswith("graph"), "Mermaid diagram should start with 'graph'"
    
    def test_network_topology_has_nodes(self):
        """Test that diagram defines network nodes"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams/network-topology.mmd"
        
        with open(diagram_path) as f:
            content = f.read()
        
        # Should contain key network components
        assert "Internet" in content or "internet" in content.lower()
        assert "Firewall" in content or "FW" in content
        assert "Switch" in content
    
    def test_network_topology_has_vlans(self):
        """Test that diagram includes VLANs"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams/network-topology.mmd"
        
        with open(diagram_path) as f:
            content = f.read()
        
        # Should reference VLANs
        assert "VLAN" in content
        # Should have multiple VLANs
        vlan_count = content.count("VLAN")
        assert vlan_count >= 2, "Diagram should show multiple VLANs"
    
    def test_network_topology_has_connections(self):
        """Test that diagram shows connections between nodes"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams/network-topology.mmd"
        
        with open(diagram_path) as f:
            content = f.read()
        
        # Should contain arrow notation for connections
        assert "-->" in content, "Diagram should show connections with arrows"
    
    def test_mermaid_has_usage_comment(self):
        """Test that diagram includes usage instructions"""
        diagram_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/diagrams/network-topology.mmd"
        
        with open(diagram_path) as f:
            content = f.read()
        
        # Should have comments explaining usage
        assert "%%" in content, "Diagram should have Mermaid comments"
        assert "Usage" in content or "Render" in content

class TestRDSRestoreRunbook:
    """Test RDS restore runbook documentation"""
    
    def test_rds_runbook_file_exists(self):
        """Test that rds-restore-runbook.md exists"""
        runbook_path = BASE_PATH / "projects/runbooks/rds-restore-runbook.md"
        assert runbook_path.exists(), f"Runbook not found at {runbook_path}"
    
    def test_rds_runbook_has_title(self):
        """Test that runbook has a title"""
        runbook_path = BASE_PATH / "projects/runbooks/rds-restore-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        # Should have a clear title
        assert content.startswith("#"), "Runbook should start with a heading"
        assert "RDS" in content.split('\n')[0]
        assert "Restore" in content.split('\n')[0] or "restore" in content.split('\n')[0].lower()
    
    def test_rds_runbook_has_overview(self):
        """Test that runbook has an overview section"""
        runbook_path = BASE_PATH / "projects/runbooks/rds-restore-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        assert "Overview" in content or "## Overview" in content
        assert "Purpose" in content or "purpose" in content.lower()
    
    def test_rds_runbook_has_prerequisites(self):
        """Test that runbook lists prerequisites"""
        runbook_path = BASE_PATH / "projects/runbooks/rds-restore-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        assert "Prerequisites" in content or "prerequisite" in content.lower()
        assert "AWS CLI" in content
    
    def test_rds_runbook_has_procedure(self):
        """Test that runbook includes restore procedure"""
        runbook_path = BASE_PATH / "projects/runbooks/rds-restore-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        assert "Procedure" in content or "procedure" in content.lower()
        # Should have AWS CLI commands
        assert "aws rds" in content
        assert "restore-db-instance-from-db-snapshot" in content
    
    def test_rds_runbook_has_code_blocks(self):
        """Test that runbook includes code blocks for commands"""
        runbook_path = BASE_PATH / "projects/runbooks/rds-restore-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        # Should have bash code blocks
        assert "```bash" in content or "```" in content
    
    def test_rds_runbook_has_preflight_checks(self):
        """Test that runbook includes preflight checks"""
        runbook_path = BASE_PATH / "projects/runbooks/rds-restore-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        assert "Pre-flight" in content or "preflight" in content.lower() or "checks" in content.lower()
        # Should have checkboxes
        assert "[ ]" in content or "- [ ]" in content
    
    def test_rds_runbook_has_snapshot_verification(self):
        """Test that runbook includes snapshot verification"""
        runbook_path = BASE_PATH / "projects/runbooks/rds-restore-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        assert "snapshot" in content.lower()
        assert "describe-db-snapshots" in content
    
    def test_rds_runbook_structure_complete(self):
        """Test that runbook has complete structure"""
        runbook_path = BASE_PATH / "projects/runbooks/rds-restore-runbook.md"
        
        with open(runbook_path) as f:
            content = f.read()
        
        required_sections = ["Overview", "Prerequisites", "Procedure"]
        
        for section in required_sections:
            assert section in content, f"Runbook missing required section: {section}"

class TestMarkdownFormattingConsistency:
    """Test markdown formatting and structure consistency"""
    
    def test_markdown_files_valid_structure(self):
        """Test that markdown files have valid structure"""
        md_files = [
            BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/documentation/vlan-assignments.md",
            BASE_PATH / "projects/runbooks/rds-restore-runbook.md"
        ]
        
        for md_file in md_files:
            if md_file.exists():
                with open(md_file) as f:
                    content = f.read()
                
                # Should not be empty
                assert len(content.strip()) > 0, f"{md_file.name} is empty"
                
                # Should have at least one heading
                assert "#" in content, f"{md_file.name} has no headings"
    
    def test_markdown_files_no_broken_formatting(self):
        """Test that markdown files don't have obvious formatting issues"""
        md_files = [
            BASE_PATH / "projects/06-homelab/PRJ-HOME-001/assets/documentation/vlan-assignments.md",
            BASE_PATH / "projects/runbooks/rds-restore-runbook.md"
        ]
        
        for md_file in md_files:
            if md_file.exists():
                with open(md_file) as f:
                    content = f.read()
                
                # Check for unclosed code blocks
                code_block_count = content.count("```")
                assert code_block_count % 2 == 0, f"{md_file.name} has unclosed code blocks"
    
    def test_markdown_technical_accuracy(self):
        """Test that markdown contains technically accurate information"""
        runbook_path = BASE_PATH / "projects/runbooks/rds-restore-runbook.md"
        
        if runbook_path.exists():
            with open(runbook_path) as f:
                content = f.read()
            
            # AWS CLI commands should be properly formatted
            if "aws rds" in content:
                # Should use correct AWS CLI syntax
                assert "--db-instance-identifier" in content or "--db-snapshot-identifier" in content

if __name__ == "__main__":
    pytest.main([__file__, "-v"])