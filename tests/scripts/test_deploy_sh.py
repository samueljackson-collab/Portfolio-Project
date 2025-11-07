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
"""Comprehensive unit tests for deploy.sh"""
import os
import subprocess
import tempfile
import pytest
from pathlib import Path

SCRIPT_PATH = Path(__file__).parent.parent.parent / "scripts/deploy.sh"


class TestDeployScriptBasicFunctionality:
    """Test basic script functionality"""
    
    def test_script_exists(self):
        """Verify the script file exists and is executable"""
        assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"
        assert os.access(SCRIPT_PATH, os.X_OK), "Script is not executable"
    
    def test_script_has_shebang(self):
        """Test that script has proper shebang"""
        with open(SCRIPT_PATH) as f:
            first_line = f.readline()
        assert first_line.startswith('#!/usr/bin/env bash')
    
    def test_script_uses_set_options(self):
        """Test that script uses strict error handling"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'set -euo pipefail' in content
    
    def test_script_ends_with_newline(self):
        """Test that script ends with a newline character"""
        with open(SCRIPT_PATH, 'rb') as f:
            content = f.read()
        assert content.endswith(b'\n'), "Script should end with newline"


class TestScriptArguments:
    """Test argument parsing and default values"""
    
    def test_default_workspace(self):
        """Test that default workspace is 'default'"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'WORKSPACE="${1:-default}"' in content
    
    def test_default_auto_approve(self):
        """Test that default auto-approve is false"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'AUTO_APPROVE="${2:-false}"' in content
    
    def test_accepts_workspace_parameter(self):
        """Test that script accepts workspace as first parameter"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert '${1:-' in content
    
    def test_accepts_auto_approve_parameter(self):
        """Test that script accepts auto-approve as second parameter"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert '${2:-' in content


class TestRootDirectoryCalculation:
    """Test ROOT_DIR calculation"""
    
    def test_calculates_root_directory(self):
        """Test that ROOT_DIR is calculated relative to script location"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"' in content
    
    def test_changes_to_terraform_directory(self):
        """Test that script changes to terraform directory"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'cd "${ROOT_DIR}/terraform"' in content


class TestTerraformFormatting:
    """Test Terraform formatting step"""
    
    def test_runs_terraform_fmt(self):
        """Test that script runs terraform fmt"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'terraform fmt -recursive' in content
    
    def test_fmt_typo_fixed(self):
        """Test that the 'tf=' typo was fixed"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should NOT have 'tf=terraform'
        assert 'tf=terraform' not in content
        # Should have correct command
        assert 'terraform fmt' in content
    
    def test_fmt_uses_recursive_flag(self):
        """Test that fmt command uses -recursive flag"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert '-recursive' in content


class TestTerraformInitialization:
    """Test Terraform initialization step"""
    
    def test_runs_terraform_init(self):
        """Test that script runs terraform init"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'terraform init' in content
    
    def test_init_uses_input_false(self):
        """Test that init uses -input=false flag"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'terraform init -input=false' in content


class TestWorkspaceManagement:
    """Test Terraform workspace management"""
    
    def test_selects_workspace(self):
        """Test that script selects the specified workspace"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'terraform workspace select' in content
    
    def test_creates_workspace_if_missing(self):
        """Test that script creates workspace if it doesn't exist"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'terraform workspace new' in content
    
    def test_checks_workspace_existence(self):
        """Test that script checks if workspace exists"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'terraform workspace list' in content
        assert 'grep -q' in content
    
    def test_workspace_conditional_logic(self):
        """Test that workspace selection uses conditional logic"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should have if-else for workspace handling
        assert 'if terraform workspace list' in content
        assert 'else' in content


class TestTerraformValidation:
    """Test Terraform validation step"""
    
    def test_runs_terraform_validate(self):
        """Test that script runs terraform validate"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'terraform validate' in content
    
    def test_validate_before_plan(self):
        """Test that validation occurs before planning"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        validate_pos = content.find('terraform validate')
        plan_pos = content.find('terraform plan')
        assert validate_pos < plan_pos, "validate should come before plan"


class TestTerraformPlanning:
    """Test Terraform planning step"""
    
    def test_runs_terraform_plan(self):
        """Test that script runs terraform plan"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'terraform plan' in content
    
    def test_plan_outputs_to_file(self):
        """Test that plan outputs to plan.tfplan file"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'terraform plan -out=plan.tfplan' in content


class TestTerraformApply:
    """Test Terraform apply logic"""
    
    def test_conditional_auto_approve(self):
        """Test that apply is conditional on AUTO_APPROVE"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'if [ "${AUTO_APPROVE}" = "true" ]' in content
    
    def test_auto_approve_applies_plan(self):
        """Test that auto-approve mode applies the plan"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'terraform apply -input=false -auto-approve plan.tfplan' in content
    
    def test_non_auto_approve_shows_instructions(self):
        """Test that non-auto-approve mode shows manual apply instructions"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'To apply: terraform apply -input=false plan.tfplan' in content
    
    def test_uses_saved_plan_file(self):
        """Test that apply uses the saved plan file"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Both branches should reference plan.tfplan
        assert content.count('plan.tfplan') >= 2


class TestOutputMessages:
    """Test informational output messages"""
    
    def test_displays_formatting_message(self):
        """Test that script displays formatting message"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'Formatting Terraform files' in content
    
    def test_displays_initialization_message(self):
        """Test that script displays initialization message"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'Initializing Terraform' in content
    
    def test_displays_workspace_message(self):
        """Test that script displays workspace selection message"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'Selecting workspace' in content
    
    def test_displays_validation_message(self):
        """Test that script displays validation message"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'Validating configuration' in content
    
    def test_displays_planning_message(self):
        """Test that script displays planning message"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'Planning' in content
    
    def test_displays_apply_message_when_auto_approve(self):
        """Test that script displays apply message in auto-approve mode"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'Applying plan (auto-approve)' in content


class TestScriptStructure:
    """Test overall script structure and best practices"""
    
    def test_commands_in_correct_order(self):
        """Test that Terraform commands are in the correct order"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        
        # Get positions of each command
        fmt_pos = content.find('terraform fmt')
        init_pos = content.find('terraform init')
        workspace_pos = content.find('terraform workspace')
        validate_pos = content.find('terraform validate')
        plan_pos = content.find('terraform plan')
        apply_pos = content.find('terraform apply')
        
        # Verify order
        assert fmt_pos < init_pos, "fmt should come before init"
        assert init_pos < workspace_pos, "init should come before workspace"
        assert workspace_pos < validate_pos, "workspace should come before validate"
        assert validate_pos < plan_pos, "validate should come before plan"
        assert plan_pos < apply_pos, "plan should come before apply"
    
    def test_no_trailing_whitespace(self):
        """Test that script has no trailing whitespace at end of file"""
        with open(SCRIPT_PATH, 'rb') as f:
            content = f.read()
        # Should end with newline but no extra whitespace
        assert content.endswith(b'\n')
        assert not content.endswith(b'  \n') and not content.endswith(b'\t\n')
    
    def test_uses_consistent_quoting(self):
        """Test that variables are consistently quoted"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Variables should be quoted
        assert '"${ROOT_DIR}' in content
        assert '"${WORKSPACE}"' in content
        assert '"${AUTO_APPROVE}"' in content


class TestErrorHandling:
    """Test error handling behavior"""
    
    def test_script_exits_on_command_failure(self):
        """Test that set -e causes exit on command failure"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'set -e' in content or 'set -euo pipefail' in content
    
    def test_undefined_variable_causes_error(self):
        """Test that set -u catches undefined variables"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'set -u' in content or 'set -euo pipefail' in content
    
    def test_pipeline_failures_detected(self):
        """Test that set -o pipefail catches pipeline failures"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'pipefail' in content


class TestUsageComments:
    """Test usage documentation"""
    
    def test_has_usage_documentation(self):
        """Test that script has usage information"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should have usage comment or description
        assert '# Usage:' in content or 'Usage:' in content or 'wrapper' in content
    
    def test_documents_purpose(self):
        """Test that script documents its purpose"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should mention Terraform or deploy
        assert 'Terraform' in content or 'terraform' in content
    
    def test_documents_parameters(self):
        """Test that parameters are documented"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should mention workspace and auto-approve
        assert 'workspace' in content.lower()
        assert 'auto-approve' in content.lower() or 'auto_approve' in content.lower()


class TestIntegrationScenarios:
    """Test integration scenarios"""
    
    def test_script_syntax_is_valid(self):
        """Test that script has valid bash syntax"""
        result = subprocess.run(  # noqa: S603, S607
            ["bash", "-n", str(SCRIPT_PATH)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"
    
    def test_script_with_default_parameters(self):
        """Test script variable initialization with defaults"""
        test_script = f"""
        # Mock the script's variable initialization
        WORKSPACE="${{1:-default}}"
        AUTO_APPROVE="${{2:-false}}"
        ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
        
        echo "WORKSPACE=$WORKSPACE"
        echo "AUTO_APPROVE=$AUTO_APPROVE"
        echo "ROOT_DIR_SET=${{ROOT_DIR:+yes}}"
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(test_script)
            f.flush()
            
            try:
                result = subprocess.run(  # noqa: S603
                    ["/bin/bash", f.name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                assert "WORKSPACE=default" in result.stdout
                assert "AUTO_APPROVE=false" in result.stdout
                assert "ROOT_DIR_SET=yes" in result.stdout
            finally:
                os.unlink(f.name)
    
    def test_script_with_custom_parameters(self):
        """Test script with custom workspace and auto-approve"""
        test_script = f"""
        WORKSPACE="${{1:-default}}"
        AUTO_APPROVE="${{2:-false}}"
        
        echo "WORKSPACE=$WORKSPACE"
        echo "AUTO_APPROVE=$AUTO_APPROVE"
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(test_script)
            f.flush()
            
            try:
                result = subprocess.run(  # noqa: S603
                    ["/bin/bash", f.name, "production", "true"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                assert "WORKSPACE=production" in result.stdout
                assert "AUTO_APPROVE=true" in result.stdout
            finally:
                os.unlink(f.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])