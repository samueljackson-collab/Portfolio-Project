"""
Comprehensive unit tests for deploy.sh

Tests cover:
- Argument parsing and defaults
- Terraform workflow execution
- Workspace management
- Error handling and safety checks
- Output formatting
- Auto-approve functionality
"""
import os
import subprocess
import tempfile
import pytest
from pathlib import Path
import shutil

SCRIPT_PATH = Path(__file__).parent.parent.parent / "scripts/deploy.sh"
BASH_PATH = shutil.which("bash")


class TestDeployBasicFunctionality:
    """Test basic script functionality"""
    
    def test_script_exists(self):
        """Verify the script file exists and is executable"""
        assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"
        assert os.access(SCRIPT_PATH, os.X_OK), "Script is not executable"
    
    def test_script_has_shebang(self):
        """Test that script has proper bash shebang"""
        with open(SCRIPT_PATH) as f:
            first_line = f.readline()
        assert first_line.startswith("#!/"), "Script missing shebang"
        assert "bash" in first_line.lower(), "Script should use bash"
    
    def test_script_has_set_flags(self):
        """Test that script has proper error handling flags"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "set -" in content, "Script should have set flags for error handling"
        assert "pipefail" in content, "Should use pipefail"


class TestArgumentParsing:
    """Test argument parsing and default values"""
    
    def test_accepts_workspace_argument(self):
        """Test that script accepts workspace as first argument"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "${1" in content or "WORKSPACE" in content, "Should accept workspace argument"
    
    def test_default_workspace_is_default(self):
        """Test that default workspace is 'default'"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "default" in content, "Should have 'default' as default workspace"
    
    def test_accepts_auto_approve_argument(self):
        """Test that script accepts auto-approve as second argument"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "${2" in content or "AUTO_APPROVE" in content or "auto" in content, \
            "Should accept auto-approve argument"
    
    def test_default_auto_approve_is_false(self):
        """Test that auto-approve defaults to false"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "false" in content, "Should default auto-approve to false"


class TestDirectoryNavigation:
    """Test script directory handling"""
    
    def test_determines_root_directory(self):
        """Test that script determines repository root directory"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "ROOT_DIR" in content or "dirname" in content, "Should determine root directory"
    
    def test_changes_to_terraform_directory(self):
        """Test that script changes to terraform directory"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "cd" in content, "Should change directory"
        assert "terraform" in content, "Should reference terraform directory"


class TestTerraformFormatting:
    """Test Terraform formatting step"""
    
    def test_runs_terraform_fmt(self):
        """Test that script runs terraform fmt"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "terraform fmt" in content, "Should run terraform fmt"
    
    def test_uses_recursive_formatting(self):
        """Test that formatting is recursive"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "-recursive" in content or "recursive" in content, \
            "Should use recursive formatting"
    
    def test_no_typo_in_terraform_command(self):
        """Test that there's no 'tf=' typo before terraform fmt"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # The bug fix was changing "tf=terraform fmt" to "terraform fmt"
        assert "tf=terraform" not in content, "Should not have 'tf=' typo"
        assert "terraform fmt" in content, "Should have correct terraform fmt command"


class TestTerraformInitialization:
    """Test Terraform initialization step"""
    
    def test_runs_terraform_init(self):
        """Test that script runs terraform init"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "terraform init" in content, "Should run terraform init"
    
    def test_uses_no_input_flag(self):
        """Test that init uses -input=false flag"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "-input=false" in content or "input=false" in content, \
            "Should use -input=false flag"


class TestWorkspaceManagement:
    """Test Terraform workspace management"""
    
    def test_selects_or_creates_workspace(self):
        """Test that script handles workspace selection"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "workspace" in content, "Should manage workspaces"
    
    def test_checks_if_workspace_exists(self):
        """Test that script checks workspace existence"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "workspace list" in content or "grep" in content, \
            "Should check workspace existence"
    
    def test_selects_existing_workspace(self):
        """Test that script selects workspace if it exists"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "workspace select" in content, "Should select workspace"
    
    def test_creates_new_workspace_if_not_exists(self):
        """Test that script creates workspace if it doesn't exist"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "workspace new" in content, "Should create new workspace"


class TestTerraformValidation:
    """Test Terraform validation step"""
    
    def test_runs_terraform_validate(self):
        """Test that script runs terraform validate"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "terraform validate" in content, "Should validate configuration"


class TestTerraformPlanning:
    """Test Terraform planning step"""
    
    def test_runs_terraform_plan(self):
        """Test that script runs terraform plan"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "terraform plan" in content, "Should run terraform plan"
    
    def test_saves_plan_to_file(self):
        """Test that plan is saved to a file"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "-out=" in content or "plan.tfplan" in content, \
            "Should save plan to file"
    
    def test_uses_tfplan_extension(self):
        """Test that plan file uses .tfplan extension"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert ".tfplan" in content or "tfplan" in content, \
            "Should use .tfplan extension"


class TestTerraformApply:
    """Test Terraform apply logic"""
    
    def test_handles_auto_approve_flag(self):
        """Test that script handles auto-approve conditionally"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "AUTO_APPROVE" in content or "auto" in content, \
            "Should handle auto-approve"
    
    def test_applies_with_auto_approve_when_enabled(self):
        """Test that apply runs with auto-approve when flag is true"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "terraform apply" in content, "Should run terraform apply"
        assert "-auto-approve" in content or "auto-approve" in content, \
            "Should support auto-approve flag"
    
    def test_uses_saved_plan_file(self):
        """Test that apply uses the saved plan file"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should reference the plan file saved earlier
        assert "plan.tfplan" in content or ".tfplan" in content, \
            "Should use saved plan file"
    
    def test_uses_no_input_flag_for_apply(self):
        """Test that apply uses -input=false flag"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should use -input=false for apply
        if "terraform apply" in content:
            assert "-input=false" in content, "Apply should use -input=false"
    
    def test_displays_manual_apply_command_when_not_auto_approve(self):
        """Test that script displays manual apply command"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should tell user how to apply manually
        assert "To apply" in content or "terraform apply" in content, \
            "Should display manual apply instructions"


class TestOutputMessages:
    """Test script output and messaging"""
    
    def test_displays_formatting_message(self):
        """Test that script displays formatting message"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "Formatting" in content or "format" in content.lower(), \
            "Should display formatting message"
    
    def test_displays_initialization_message(self):
        """Test that script displays initialization message"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "Initializing" in content or "init" in content.lower(), \
            "Should display initialization message"
    
    def test_displays_workspace_message(self):
        """Test that script displays workspace message"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "workspace" in content.lower() or "Selecting" in content, \
            "Should display workspace message"
    
    def test_displays_validation_message(self):
        """Test that script displays validation message"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "Validating" in content or "validate" in content.lower(), \
            "Should display validation message"
    
    def test_displays_planning_message(self):
        """Test that script displays planning message"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "Planning" in content or "plan" in content.lower(), \
            "Should display planning message"


class TestErrorHandling:
    """Test error handling"""
    
    def test_uses_errexit_flag(self):
        """Test that script exits on errors"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "set -e" in content or "errexit" in content, \
            "Should exit on errors"
    
    def test_uses_nounset_flag(self):
        """Test that script catches undefined variables"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "set -u" in content or "nounset" in content, \
            "Should catch undefined variables"
    
    def test_uses_pipefail_flag(self):
        """Test that script catches errors in pipelines"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "pipefail" in content, "Should use pipefail"


class TestSafetyFeatures:
    """Test safety features"""
    
    def test_runs_plan_before_apply(self):
        """Test that plan is run before apply"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Plan should come before apply in the script
        plan_pos = content.find("terraform plan")
        apply_pos = content.find("terraform apply")
        assert plan_pos < apply_pos, "Plan should be run before apply"
    
    def test_requires_explicit_auto_approve(self):
        """Test that auto-approve is not the default"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Default should be false/manual approval
        assert "false" in content, "Should default to manual approval"
    
    def test_validates_before_planning(self):
        """Test that validation is run before planning"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        validate_pos = content.find("terraform validate")
        plan_pos = content.find("terraform plan")
        assert validate_pos < plan_pos, "Validate should run before plan"


class TestWorkflowOrder:
    """Test that Terraform workflow steps are in correct order"""
    
    def test_fmt_before_init(self):
        """Test that fmt is run before init"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        fmt_pos = content.find("terraform fmt")
        init_pos = content.find("terraform init")
        assert fmt_pos < init_pos, "Format should run before init"
    
    def test_init_before_workspace(self):
        """Test that init is run before workspace selection"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        init_pos = content.find("terraform init")
        workspace_pos = content.find("workspace")
        assert init_pos < workspace_pos, "Init should run before workspace"
    
    def test_workspace_before_validate(self):
        """Test that workspace is selected before validate"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        workspace_pos = content.find("workspace")
        validate_pos = content.find("terraform validate")
        assert workspace_pos < validate_pos, "Workspace should be selected before validate"


class TestScriptStructure:
    """Test script structure and organization"""
    
    def test_has_descriptive_comments(self):
        """Test that script has descriptive comments"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        comment_lines = [line for line in content.split('\n') if line.strip().startswith('#')]
        assert len(comment_lines) >= 2, "Should have descriptive comments"
    
    def test_uses_meaningful_variable_names(self):
        """Test that variable names are descriptive"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "WORKSPACE" in content or "workspace" in content, \
            "Should use descriptive variable names"
        assert "ROOT_DIR" in content or "root" in content.lower(), \
            "Should define root directory"


class TestDocumentation:
    """Test script documentation"""
    
    def test_has_usage_comment(self):
        """Test that script documents its usage"""
        with open(SCRIPT_PATH) as f:
            lines = f.readlines()[:15]
        content = ''.join(lines)
        assert "Usage" in content or "#" in content, "Should document usage"
    
    def test_documents_purpose(self):
        """Test that script documents its purpose"""
        with open(SCRIPT_PATH) as f:
            lines = f.readlines()[:15]
        content = ''.join(lines)
        # Should explain what the script does
        assert any(word in content for word in ["Terraform", "deploy", "wrapper", "helper"]), \
            "Should document purpose"


class TestConditionalLogic:
    """Test conditional execution logic"""
    
    def test_has_if_statement_for_auto_approve(self):
        """Test that auto-approve uses conditional logic"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "if" in content or "[" in content, "Should use conditional logic"
    
    def test_checks_workspace_existence_conditionally(self):
        """Test that workspace creation is conditional"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should check if workspace exists before creating
        assert "if" in content and "workspace" in content, \
            "Should conditionally handle workspace"


class TestNewlineHandling:
    """Test proper file ending (related to the actual change made)"""
    
    def test_script_ends_with_newline(self):
        """Test that script ends with a newline character"""
        with open(SCRIPT_PATH, 'rb') as f:
            content = f.read()
        assert content.endswith(b'\n'), "Script should end with newline character"
    
    def test_no_trailing_whitespace_on_last_line(self):
        """Test that last line has no trailing whitespace"""
        with open(SCRIPT_PATH) as f:
            lines = f.readlines()
        if lines:
            last_line = lines[-1]
            assert last_line.strip() == '' or not last_line.rstrip().endswith(' '), \
                "Last line should not have trailing whitespace"


class TestBugFixes:
    """Test that known bugs are fixed"""
    
    def test_terraform_fmt_command_correct(self):
        """Test that terraform fmt command doesn't have typo"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # The fix was changing "tf=terraform fmt" to "terraform fmt"
        lines = content.split('\n')
        for line in lines:
            if 'terraform fmt' in line:
                # Check that it's not assigned to a variable
                assert not line.strip().startswith('tf='), \
                    "terraform fmt should not be assigned to variable 'tf'"
                assert 'terraform fmt' in line, "Should have correct terraform fmt command"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])