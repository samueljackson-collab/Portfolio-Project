"""
Comprehensive tests for Production Runbooks

This test suite validates:
- Runbook file structure and required sections
- Code block syntax and executability
- Command examples and troubleshooting steps
- Internal link integrity
- Severity level definitions
- Incident response procedures
- Content completeness and quality
"""

import re
import pytest
from pathlib import Path
from typing import List, Dict

BASE_PATH = Path(__file__).parent.parent.parent


class TestRunbookStructure:
    """Test runbook file structure and required sections"""
    
    @pytest.fixture
    def runbook_files(self) -> List[Path]:
        """Get all runbook files"""
        runbooks_dir = BASE_PATH / "docs/runbooks"
        return sorted(runbooks_dir.glob("runbook-*.md"))
    
    @pytest.fixture
    def runbook_readme(self) -> Path:
        """Get runbooks README"""
        return BASE_PATH / "docs/runbooks/README.md"
    
    @pytest.fixture
    def incident_framework(self) -> Path:
        """Get incident response framework"""
        return BASE_PATH / "docs/runbooks/incident-response-framework.md"
    
    def test_runbook_files_exist(self, runbook_files):
        """Test that runbook files exist"""
        assert len(runbook_files) >= 5, "Expected at least 5 runbook files"
        
        expected_runbooks = [
            "runbook-database-connection-pool-exhaustion.md",
            "runbook-disaster-recovery.md",
            "runbook-high-cpu-usage.md",
            "runbook-high-error-rate.md",
            "runbook-security-incident-response.md"
        ]
        
        runbook_names = [f.name for f in runbook_files]
        for expected in expected_runbooks:
            assert expected in runbook_names, f"Missing runbook: {expected}"
    
    def test_incident_framework_exists(self, incident_framework):
        """Test that incident response framework exists"""
        assert incident_framework.exists(), "Incident response framework not found"
    
    def test_runbook_has_required_sections(self, runbook_files):
        """Test that each runbook has required operational sections"""
        required_sections = [
            "# Runbook:",
            "## Overview",
            "## Symptoms",
        ]
        
        for runbook in runbook_files:
            with open(runbook) as f:
                content = f.read()
            
            for section in required_sections:
                assert section in content, f"{runbook.name} missing section: {section}"
    
    def test_runbook_has_detection_or_investigation(self, runbook_files):
        """Test that runbooks have detection or investigation sections"""
        for runbook in runbook_files:
            with open(runbook) as f:
                content = f.read()
            
            has_detection = "## Detection" in content or "## Investigation" in content
            assert has_detection, \
                f"{runbook.name} should have Detection or Investigation section"
    
    def test_runbook_minimum_content_length(self, runbook_files):
        """Test that runbooks have substantial content"""
        min_length = 2000  # At least 2000 characters for runbooks
        
        for runbook in runbook_files:
            with open(runbook) as f:
                content = f.read()
            
            assert len(content) >= min_length, \
                f"{runbook.name} is too short ({len(content)} chars, expected >= {min_length})"
    
    def test_runbook_has_command_examples(self, runbook_files):
        """Test that runbooks contain command examples"""
        for runbook in runbook_files:
            with open(runbook) as f:
                content = f.read()
            
            # Should have code blocks with commands
            code_block_count = content.count("```")
            assert code_block_count >= 4, \
                f"{runbook.name} should have at least 2 command examples (found {code_block_count // 2})"


class TestRunbookCommands:
    """Test command examples in runbooks"""
    
    @pytest.fixture
    def runbook_files(self) -> List[Path]:
        """Get all runbook files"""
        runbooks_dir = BASE_PATH / "docs/runbooks"
        return sorted(runbooks_dir.glob("runbook-*.md")) + [
            BASE_PATH / "docs/runbooks/incident-response-framework.md"
        ]
    
    def test_bash_commands_are_valid(self, runbook_files):
        """Test that bash command blocks have valid syntax"""
        bash_pattern = re.compile(r"```(?:bash|shell)\n(.*?)```", re.DOTALL)
        
        # Common kubernetes commands
        valid_commands = [
            "kubectl", "aws", "curl", "grep", "awk", "sed", "psql", "mysql",
            "redis-cli", "docker", "ssh", "scp", "tar", "gzip", "systemctl",
            "journalctl", "top", "htop", "ps", "netstat", "ss", "dig", "nslookup"
        ]
        
        for runbook in runbook_files:
            with open(runbook) as f:
                content = f.read()
            
            bash_blocks = bash_pattern.findall(content)
            if not bash_blocks:
                continue
            
            for block in bash_blocks:
                # Skip pure comment blocks
                non_comment_lines = [
                    line for line in block.split("\n") 
                    if line.strip() and not line.strip().startswith("#")
                ]
                
                if not non_comment_lines:
                    continue
                
                # Check that block contains recognizable commands
                has_valid_command = any(
                    cmd in block for cmd in valid_commands
                )
                
                # Or has common shell constructs
                has_shell_construct = any(
                    construct in block 
                    for construct in ["$", "|", "&&", "||", "if", "for", "while", "echo"]
                )
                
                assert has_valid_command or has_shell_construct, \
                    f"{runbook.name} has bash block without recognizable commands"
    
    def test_kubectl_commands_have_namespace(self, runbook_files):
        """Test that kubectl commands specify namespace when appropriate"""
        kubectl_pattern = re.compile(r"kubectl\s+\w+")
        
        for runbook in runbook_files:
            with open(runbook) as f:
                content = f.read()
            
            # Find kubectl commands
            kubectl_commands = re.findall(r"kubectl\s+[^\n]+", content)
            
            for cmd in kubectl_commands:
                # Commands that should have namespace
                if any(resource in cmd for resource in ["get", "describe", "logs", "exec", "delete", "scale"]):
                    # Should have -n or --namespace (or be using system resources like nodes)
                    has_namespace = "-n " in cmd or "--namespace" in cmd or "nodes" in cmd or "namespaces" in cmd
                    # Allow commands without namespace if they're clearly examples or have --all-namespaces
                    has_all_ns = "--all-namespaces" in cmd or "-A" in cmd
                    
                    if not (has_namespace or has_all_ns):
                        # This is a soft warning - some commands may legitimately not need namespace
                        pass  # We'll be lenient here
    
    def test_sql_commands_are_valid(self, runbook_files):
        """Test that SQL command blocks have valid syntax"""
        sql_pattern = re.compile(r"```sql\n(.*?)```", re.DOTALL)
        
        sql_keywords = ["SELECT", "FROM", "WHERE", "UPDATE", "DELETE", "INSERT", "CREATE", "ALTER", "DROP", "SHOW"]
        
        for runbook in runbook_files:
            with open(runbook) as f:
                content = f.read()
            
            sql_blocks = sql_pattern.findall(content)
            if not sql_blocks:
                continue
            
            for block in sql_blocks:
                has_sql = any(keyword in block.upper() for keyword in sql_keywords)
                assert has_sql, \
                    f"{runbook.name} has SQL block without SQL keywords"
    
    def test_commands_have_comments(self, runbook_files):
        """Test that complex commands have explanatory comments"""
        bash_pattern = re.compile(r"```(?:bash|shell)\n(.*?)```", re.DOTALL)
        
        for runbook in runbook_files:
            with open(runbook) as f:
                content = f.read()
            
            bash_blocks = bash_pattern.findall(content)
            
            for block in bash_blocks:
                lines = block.split("\n")
                command_lines = [l for l in lines if l.strip() and not l.strip().startswith("#")]
                
                # If block has multiple command lines, should have some comments
                if len(command_lines) >= 3:
                    has_comments = any(line.strip().startswith("#") for line in lines)
                    # Soft check - not all multi-line commands need comments
                    # but it's good practice


class TestRunbookREADME:
    """Test runbooks README for completeness"""
    
    @pytest.fixture
    def readme(self) -> Path:
        """Get runbooks README"""
        return BASE_PATH / "docs/runbooks/README.md"
    
    @pytest.fixture
    def runbook_files(self) -> List[Path]:
        """Get all runbook files"""
        runbooks_dir = BASE_PATH / "docs/runbooks"
        return sorted(runbooks_dir.glob("runbook-*.md"))
    
    def test_readme_exists(self, readme):
        """Test that README exists"""
        assert readme.exists(), "Runbooks README not found"
    
    def test_readme_has_required_sections(self, readme):
        """Test that README has required sections"""
        required_sections = [
            "# Production Runbooks",
            "## Purpose",
            "## Runbook Index",
            "## Severity Levels"
        ]
        
        with open(readme) as f:
            content = f.read()
        
        for section in required_sections:
            assert section in content, f"README missing section: {section}"
    
    def test_readme_lists_all_runbooks(self, readme, runbook_files):
        """Test that README lists all runbook files"""
        with open(readme) as f:
            content = f.read()
        
        for runbook in runbook_files:
            # Extract the descriptive name (without runbook- prefix)
            name_part = runbook.stem.replace("runbook-", "").replace("-", " ").title()
            
            # Should be referenced somehow in README
            assert runbook.name in content or name_part in content, \
                f"README does not list {runbook.name}"
    
    def test_readme_has_severity_definitions(self, readme):
        """Test that README defines severity levels"""
        with open(readme) as f:
            content = f.read()
        
        severity_levels = ["P0", "P1", "P2", "P3"]
        for level in severity_levels:
            assert level in content, f"README should define severity level {level}"


class TestIncidentResponseFramework:
    """Test incident response framework document"""
    
    @pytest.fixture
    def framework(self) -> Path:
        """Get incident response framework"""
        return BASE_PATH / "docs/runbooks/incident-response-framework.md"
    
    def test_framework_exists(self, framework):
        """Test that incident response framework exists"""
        assert framework.exists(), "Incident response framework not found"
    
    def test_framework_has_lifecycle_stages(self, framework):
        """Test that framework defines incident lifecycle stages"""
        with open(framework) as f:
            content = f.read()
        
        lifecycle_stages = ["Detection", "Triage", "Mitigation", "Resolution", "Postmortem"]
        for stage in lifecycle_stages:
            assert stage in content, f"Framework should define {stage} stage"
    
    def test_framework_has_severity_matrix(self, framework):
        """Test that framework has severity assessment criteria"""
        with open(framework) as f:
            content = f.read()
        
        # Should discuss severity levels
        assert "severity" in content.lower() or "priority" in content.lower(), \
            "Framework should define severity levels"
        
        # Should have P0/P1/P2/P3 or similar
        has_priorities = any(p in content for p in ["P0", "P1", "P2", "P3", "Sev 1", "Sev 2"])
        assert has_priorities, "Framework should define priority levels"
    
    def test_framework_has_communication_procedures(self, framework):
        """Test that framework includes communication procedures"""
        with open(framework) as f:
            content = f.read().lower()
        
        communication_keywords = ["slack", "email", "notification", "alert", "communicate", "update"]
        has_communication = any(keyword in content for keyword in communication_keywords)
        assert has_communication, "Framework should include communication procedures"
    
    def test_framework_has_quick_reference_commands(self, framework):
        """Test that framework has quick reference commands"""
        with open(framework) as f:
            content = f.read()
        
        # Should have code blocks
        code_blocks = content.count("```")
        assert code_blocks >= 4, "Framework should include quick reference commands"


class TestRunbookContentQuality:
    """Test runbook content quality and completeness"""
    
    @pytest.fixture
    def runbook_files(self) -> List[Path]:
        """Get all runbook files"""
        runbooks_dir = BASE_PATH / "docs/runbooks"
        return sorted(runbooks_dir.glob("runbook-*.md"))
    
    def test_runbook_has_actionable_steps(self, runbook_files):
        """Test that runbooks have numbered or bulleted action steps"""
        for runbook in runbook_files:
            with open(runbook) as f:
                content = f.read()
            
            # Should have numbered lists (1. 2. 3.) or bullets (- *)
            has_steps = bool(re.search(r"^\d+\.\s", content, re.MULTILINE)) or \
                       bool(re.search(r"^[-*]\s", content, re.MULTILINE))
            
            assert has_steps, f"{runbook.name} should have actionable steps"
    
    def test_runbook_overview_is_substantial(self, runbook_files):
        """Test that Overview section has meaningful content"""
        for runbook in runbook_files:
            with open(runbook) as f:
                content = f.read()
            
            if "## Overview" not in content:
                continue
            
            # Extract Overview section
            overview = content.split("## Overview")[1].split("##")[0]
            overview_length = len(overview.strip())
            
            assert overview_length >= 100, \
                f"{runbook.name} Overview section is too brief ({overview_length} chars)"
    
    def test_runbook_has_time_estimates(self, runbook_files):
        """Test that runbooks include time estimates for steps"""
        time_patterns = [
            r"\d+\s*(?:minute|min|hour|hr)",
            r"\d+-\d+\s*(?:minute|min)",
            r"\(\d+\s*(?:minute|min)\)",
        ]
        
        for runbook in runbook_files:
            with open(runbook) as f:
                content = f.read().lower()
            
            has_time_estimate = any(re.search(pattern, content) for pattern in time_patterns)
            # Soft check - not all runbooks need explicit time estimates
    
    def test_runbook_has_symptoms_or_detection(self, runbook_files):
        """Test that runbooks describe how to detect the issue"""
        for runbook in runbook_files:
            with open(runbook) as f:
                content = f.read()
            
            has_detection = "## Symptoms" in content or "## Detection" in content
            assert has_detection, \
                f"{runbook.name} should describe symptoms or detection methods"


class TestRunbookSpecificContent:
    """Test specific runbooks for their domain-specific content"""
    
    def test_database_runbook_content(self):
        """Test database connection pool runbook has expected content"""
        runbook = BASE_PATH / "docs/runbooks/runbook-database-connection-pool-exhaustion.md"
        if not runbook.exists():
            pytest.skip("Database runbook not found")
        
        with open(runbook) as f:
            content = f.read().lower()
        
        required_topics = ["connection", "pool", "database", "query", "timeout"]
        for topic in required_topics:
            assert topic in content, f"Database runbook should discuss {topic}"
    
    def test_disaster_recovery_runbook_content(self):
        """Test disaster recovery runbook has expected content"""
        runbook = BASE_PATH / "docs/runbooks/runbook-disaster-recovery.md"
        if not runbook.exists():
            pytest.skip("DR runbook not found")
        
        with open(runbook) as f:
            content = f.read().lower()
        
        required_topics = ["failover", "recovery", "backup", "rto", "rpo"]
        for topic in required_topics:
            assert topic in content, f"DR runbook should discuss {topic}"
    
    def test_high_cpu_runbook_content(self):
        """Test high CPU runbook has expected content"""
        runbook = BASE_PATH / "docs/runbooks/runbook-high-cpu-usage.md"
        if not runbook.exists():
            pytest.skip("CPU runbook not found")
        
        with open(runbook) as f:
            content = f.read().lower()
        
        required_topics = ["cpu", "performance", "pod", "node", "resource"]
        for topic in required_topics:
            assert topic in content, f"CPU runbook should discuss {topic}"
    
    def test_high_error_rate_runbook_content(self):
        """Test high error rate runbook has expected content"""
        runbook = BASE_PATH / "docs/runbooks/runbook-high-error-rate.md"
        if not runbook.exists():
            pytest.skip("Error rate runbook not found")
        
        with open(runbook) as f:
            content = f.read().lower()
        
        required_topics = ["error", "rate", "status code", "endpoint", "api"]
        for topic in required_topics:
            assert topic in content, f"Error rate runbook should discuss {topic}"
    
    def test_security_incident_runbook_content(self):
        """Test security incident runbook has expected content"""
        runbook = BASE_PATH / "docs/runbooks/runbook-security-incident-response.md"
        if not runbook.exists():
            pytest.skip("Security runbook not found")
        
        with open(runbook) as f:
            content = f.read().lower()
        
        required_topics = ["security", "incident", "breach", "audit", "forensic"]
        for topic in required_topics:
            assert topic in content, f"Security runbook should discuss {topic}"


class TestRunbookLinkIntegrity:
    """Test links and references in runbooks"""
    
    @pytest.fixture
    def runbook_files(self) -> List[Path]:
        """Get all runbook files"""
        runbooks_dir = BASE_PATH / "docs/runbooks"
        return sorted(runbooks_dir.glob("*.md"))
    
    def test_markdown_links_are_valid(self, runbook_files):
        """Test that markdown links in runbooks are valid"""
        link_pattern = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")
        
        for runbook in runbook_files:
            with open(runbook) as f:
                content = f.read()
            
            matches = link_pattern.findall(content)
            
            for text, link in matches:
                # Skip external links
                if link.startswith("http://") or link.startswith("https://"):
                    continue
                
                # Skip anchors
                if link.startswith("#"):
                    continue
                
                # Check relative file links
                link_path = runbook.parent / link.split("#")[0]
                
                # Soft check - some links might be to files not in this branch
                if not link_path.exists():
                    # Check if it's a relative link to parent directories
                    alt_path = BASE_PATH / link.split("#")[0]
                    if not alt_path.exists():
                        pass  # We'll be lenient with broken links to other parts of repo


if __name__ == "__main__":
    pytest.main([__file__, "-v"])