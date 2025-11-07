"""Validation tests for PR_DESCRIPTION.md

These tests ensure that the PR description contains all necessary information
for deploying and validating the monitoring stack changes.
"""
import re
import pytest
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent.parent


class TestPRDescriptionContent:
    """Test that PR_DESCRIPTION.md has comprehensive deployment information"""
    
    def test_pr_description_exists(self):
        """Test that PR_DESCRIPTION.md exists"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        assert pr_desc_path.exists(), "PR_DESCRIPTION.md not found"
    
    def test_pr_description_not_empty(self):
        """Test that PR_DESCRIPTION.md is not empty"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        assert len(content) > 100, "PR description is too short"
    
    def test_pr_has_overview_section(self):
        """Test that PR has an overview or summary section"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Should have some kind of overview
        assert "overview" in content.lower() or "summary" in content.lower() or "description" in content.lower()
    
    def test_pr_documents_changes(self):
        """Test that PR documents the changes made"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Should mention the key changes
        assert "environment variable" in content.lower() or "env var" in content.lower()
        assert "service discovery" in content.lower() or "service name" in content.lower()


class TestPRDeploymentInstructions:
    """Test that PR has complete deployment instructions"""
    
    def test_pr_has_quick_start_section(self):
        """Test that PR has quick start or deployment section"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        assert "quick start" in content.lower() or "deployment" in content.lower()
    
    def test_pr_has_directory_preparation_steps(self):
        """Test that PR includes directory preparation instructions"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Should have mkdir commands
        assert "mkdir" in content
        assert "/opt/monitoring" in content
        
        # Should mention ownership/permissions
        assert "chown" in content or "chmod" in content
    
    def test_pr_documents_required_env_vars(self):
        """Test that PR documents all required environment variables"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Check for new environment variables that were introduced
        required_env_vars = [
            "SMTP_USERNAME",
            "SMTP_PASSWORD",
            "CRITICAL_EMAIL_TO",
            "SLACK_WEBHOOK_URL",
            "HOSTNAME",
            "GRAFANA_ADMIN_PASSWORD"
        ]
        
        for env_var in required_env_vars:
            assert env_var in content, f"Required environment variable {env_var} not documented"
    
    def test_pr_has_env_file_example(self):
        """Test that PR has .env file example"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Should have .env file creation
        assert ".env" in content
        
        # Should show how to create it
        assert "cat >" in content or "echo" in content
    
    def test_pr_documents_docker_compose_deployment(self):
        """Test that PR documents docker-compose deployment"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Should mention docker-compose
        assert "docker-compose" in content or "docker compose" in content
        
        # Should mention the monitoring stack file
        assert "monitoring-stack" in content.lower()
    
    def test_pr_has_verification_steps(self):
        """Test that PR includes verification steps"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Should have verification section
        assert "verify" in content.lower() or "validation" in content.lower() or "test" in content.lower()
        
        # Should include curl commands or similar
        assert "curl" in content.lower() or "http" in content.lower()
    
    def test_pr_verification_covers_all_services(self):
        """Test that verification covers Prometheus, Loki, and Grafana"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Should verify core services
        assert "prometheus" in content.lower()
        assert "loki" in content.lower()
        assert "grafana" in content.lower()
        
        # Should have health/status checks
        assert "9090" in content or "prometheus" in content.lower()  # Prometheus port
        assert "3100" in content or "loki" in content.lower()  # Loki port
        assert "3000" in content or "grafana" in content.lower()  # Grafana port


class TestPRCodeExamples:
    """Test that PR has proper code examples"""
    
    def test_pr_has_code_blocks(self):
        """Test that PR uses markdown code blocks"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Should have code blocks
        assert "```" in content, "No code blocks found"
        
        # Count code blocks
        code_block_count = content.count("```")
        assert code_block_count >= 4, f"Expected at least 4 code blocks (open/close pairs), found {code_block_count}"
    
    def test_pr_code_blocks_are_bash(self):
        """Test that deployment code blocks specify bash language"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Should have bash code blocks
        assert "```bash" in content or "```sh" in content
    
    def test_pr_commands_are_safe(self):
        """Test that PR doesn't include dangerous commands without warnings"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Check for potentially dangerous patterns
        dangerous_patterns = [
            r"rm\s+-rf\s+/",  # Destructive rm on root
            r"chmod\s+777",    # Overly permissive
            r">[^>]*/dev/null\s+2>&1\s*$",  # Silent error suppression in examples
        ]
        
        for pattern in dangerous_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            assert len(matches) == 0, f"Found potentially dangerous pattern: {pattern}"


class TestPREnvironmentVariableConsistency:
    """Test that environment variables are consistently documented"""
    
    def test_all_env_vars_have_descriptions_or_examples(self):
        """Test that all environment variables have context"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Extract environment variable assignments
        env_var_pattern = r"([A-Z_]+)="
        env_vars = re.findall(env_var_pattern, content)
        
        # Common environment variables that should be documented
        expected_vars = ["SMTP_USERNAME", "SMTP_PASSWORD", "CRITICAL_EMAIL_TO", "HOSTNAME"]
        
        for var in expected_vars:
            assert var in env_vars, f"Environment variable {var} not found in PR description"
    
    def test_env_vars_match_config_files(self):
        """Test that PR env vars match those used in config files"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        alertmanager_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/alertmanager/alertmanager.yml"
        promtail_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/promtail/promtail-config.yml"
        
        with open(pr_desc_path) as f:
            pr_content = f.read()
        
        with open(alertmanager_path) as f:
            am_content = f.read()
        
        with open(promtail_path) as f:
            promtail_content = f.read()
        
        # Variables used in alertmanager
        if "${SMTP_USERNAME}" in am_content:
            assert "SMTP_USERNAME" in pr_content, "SMTP_USERNAME used in config but not documented in PR"
        
        if "${CRITICAL_EMAIL_TO}" in am_content:
            assert "CRITICAL_EMAIL_TO" in pr_content, "CRITICAL_EMAIL_TO used in config but not documented in PR"
        
        # Variables used in promtail
        if "${HOSTNAME}" in promtail_content:
            assert "HOSTNAME" in pr_content, "HOSTNAME used in config but not documented in PR"


class TestPRPostDeploymentGuidance:
    """Test that PR includes post-deployment guidance"""
    
    def test_pr_has_post_deployment_section(self):
        """Test that PR has post-deployment guidance"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Should have post-deployment guidance
        assert "post-deployment" in content.lower() or "after deployment" in content.lower() or "next steps" in content.lower()
    
    def test_pr_mentions_grafana_dashboards(self):
        """Test that PR mentions importing Grafana dashboards"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Should mention dashboards
        if "grafana" in content.lower():
            # If Grafana is mentioned, dashboards should be discussed
            assert "dashboard" in content.lower(), "Grafana mentioned but no dashboard guidance"
    
    def test_pr_mentions_node_exporter_deployment(self):
        """Test that PR mentions deploying node exporters"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Should mention node exporter for collecting metrics
        assert "node" in content.lower() and "exporter" in content.lower()


class TestPRFormattingQuality:
    """Test PR description formatting and structure"""
    
    def test_pr_uses_proper_markdown_headers(self):
        """Test that PR uses markdown headers for sections"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Should have markdown headers
        assert re.search(r"^#{1,3}\s+", content, re.MULTILINE), "No markdown headers found"
    
    def test_pr_has_proper_structure(self):
        """Test that PR has a logical structure"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Headers should be in logical order
        lines = content.split("\n")
        header_lines = [i for i, line in enumerate(lines) if re.match(r"^#{1,3}\s+", line)]
        
        assert len(header_lines) >= 2, "PR should have multiple sections"
    
    def test_pr_is_comprehensive(self):
        """Test that PR description is comprehensive (not too short)"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Should be substantial
        assert len(content) > 2000, "PR description should be comprehensive (at least 2000 characters)"
        
        # Should have multiple sections
        section_count = content.count("\n##")
        assert section_count >= 3, f"PR should have at least 3 major sections, found {section_count}"


class TestPRMigrationGuidance:
    """Test that PR provides migration guidance from old to new config"""
    
    def test_pr_explains_breaking_changes(self):
        """Test that PR explains any breaking changes"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Since we're changing from hardcoded values to env vars, this is a breaking change
        # Should mention the transition
        change_indicators = [
            "environment variable" in content.lower(),
            "env var" in content.lower(),
            ".env" in content,
            "configuration" in content.lower()
        ]
        
        assert any(change_indicators), "PR should explain configuration changes"
    
    def test_pr_shows_old_vs_new_comparison(self):
        """Test that PR shows what changed from old approach to new"""
        pr_desc_path = BASE_PATH / "PR_DESCRIPTION.md"
        
        with open(pr_desc_path) as f:
            content = f.read()
        
        # Should give context about the change
        # Either through "before/after", "old/new", or showing the changes
        comparison_indicators = [
            "before" in content.lower() and "after" in content.lower(),
            "old" in content.lower() and "new" in content.lower(),
            "change" in content.lower() or "update" in content.lower(),
            "replaced" in content.lower() or "instead" in content.lower()
        ]
        
        assert any(comparison_indicators), "PR should explain what changed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])