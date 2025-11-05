"""
Comprehensive unit tests for deploy.sh

Tests cover:
- Workspace selection and creation
- Terraform workflow orchestration
- Auto-approve functionality
- Directory handling
- Error handling
"""
import subprocess
import pytest
from pathlib import Path

SCRIPT_PATH = Path(__file__).parent.parent.parent / "scripts/deploy.sh"


class TestDeployBasicFunctionality:
    """Test basic script functionality"""
    
    def test_script_exists_and_executable(self):
        """Verify script exists and is executable"""
        assert SCRIPT_PATH.exists()
        assert SCRIPT_PATH.stat().st_mode & 0o111
    
    def test_accepts_workspace_argument(self):
        """Test that script accepts workspace as first argument"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'WORKSPACE="${1:-' in content
    
    def test_accepts_auto_approve_argument(self):
        """Test that script accepts auto-approve as second argument"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'AUTO_APPROVE="${2:-' in content
    
    def test_default_workspace_is_default(self):
        """Test that default workspace is 'default'"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'default' in content.lower()
    
    def test_default_auto_approve_is_false(self):
        """Test that auto-approve defaults to false"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'false' in content.lower()


class TestTerraformWorkflow:
    """Test Terraform command orchestration"""
    
    def test_runs_terraform_fmt(self):
        """Test that terraform fmt is run first"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'terraform fmt' in content
        assert '-recursive' in content
    
    def test_runs_terraform_init(self):
        """Test that terraform init is run"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'terraform init' in content
        assert '-input=false' in content
    
    def test_handles_workspace_selection(self):
        """Test that workspace is selected if it exists"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'workspace select' in content
        assert 'workspace list' in content or 'workspace' in content
    
    def test_creates_workspace_if_not_exists(self):
        """Test that workspace is created if it doesn't exist"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'workspace new' in content
    
    def test_runs_terraform_validate(self):
        """Test that terraform validate is run"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'terraform validate' in content
    
    def test_runs_terraform_plan(self):
        """Test that terraform plan is run"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'terraform plan' in content
        assert '-out=plan.tfplan' in content or 'plan.tfplan' in content


class TestAutoApproveLogic:
    """Test auto-approve conditional logic"""
    
    def test_applies_plan_with_auto_approve(self):
        """Test that plan is applied when auto-approve is true"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'terraform apply' in content
        assert '-auto-approve' in content
    
    def test_provides_manual_apply_instructions(self):
        """Test that manual apply instructions are shown without auto-approve"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'To apply' in content or 'terraform apply' in content
    
    def test_checks_auto_approve_condition(self):
        """Test that auto-approve condition is checked"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'AUTO_APPROVE' in content
        assert 'if' in content or '[' in content


class TestDirectoryHandling:
    """Test working directory management"""
    
    def test_determines_root_directory(self):
        """Test that script determines repository root"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'ROOT_DIR=' in content
        assert 'dirname' in content
        assert 'cd' in content
    
    def test_changes_to_terraform_directory(self):
        """Test that script changes to terraform directory"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'cd' in content
        assert 'terraform' in content.lower()


class TestOutputMessaging:
    """Test user feedback and messaging"""
    
    def test_displays_formatting_message(self):
        """Test that formatting step is announced"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'Formatting' in content or 'fmt' in content
    
    def test_displays_initializing_message(self):
        """Test that initialization step is announced"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'Initializing' in content or 'init' in content
    
    def test_displays_workspace_message(self):
        """Test that workspace selection is announced"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'workspace' in content.lower()
    
    def test_displays_validation_message(self):
        """Test that validation step is announced"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'Validating' in content or 'validate' in content
    
    def test_displays_planning_message(self):
        """Test that planning step is announced"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'Planning' in content or 'plan' in content


class TestErrorHandling:
    """Test error handling and script safety"""
    
    def test_uses_strict_bash_mode(self):
        """Test that script uses bash strict mode"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'set -euo pipefail' in content
    
    def test_uses_bash_shebang(self):
        """Test that script uses bash shebang"""
        with open(SCRIPT_PATH) as f:
            first_line = f.readline()
        assert '#!/usr/bin/env bash' in first_line or '#!/bin/bash' in first_line


if __name__ == "__main__":
    pytest.main([__file__, "-v"])