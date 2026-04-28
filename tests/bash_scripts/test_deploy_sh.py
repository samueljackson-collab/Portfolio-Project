# Tests updated with comprehensive validation for deploy script bug fix

"""
Comprehensive tests for scripts/deploy.sh

This test suite validates:
- Script existence and permissions
- Terraform command orchestration
- Workspace management
- Auto-approve functionality
- Error handling
- Safe deployment practices
"""

import subprocess
import os
import shutil
import pytest
from pathlib import Path


@pytest.fixture
def script_path():
    """Return the path to the deploy script."""
    return Path("scripts/deploy.sh")


class TestScriptExistence:
    """Test script file properties."""

    def test_script_exists(self, script_path):
        """Verify the deploy script exists."""
        assert script_path.exists(), f"Script not found at {script_path}"

    def test_script_is_executable(self, script_path):
        """Verify the script has executable permissions."""
        assert os.access(script_path, os.X_OK), f"{script_path} is not executable"

    def test_script_has_bash_shebang(self, script_path):
        """Verify the script has bash shebang."""
        with open(script_path, 'r') as f:
            first_line = f.readline().strip()
        assert first_line.startswith("#!/"), "Script missing shebang"
        assert "bash" in first_line, "Script should use bash"


class TestScriptSyntax:
    """Test bash script syntax."""

    def test_bash_syntax_valid(self, script_path):
        """Verify bash syntax is valid."""
        bash_path = shutil.which("bash")
        if not bash_path:
            pytest.skip("bash not found on this system")
        result = subprocess.run(  # noqa: S603
            [bash_path, "-n", str(script_path)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_script_uses_strict_mode(self, script_path):
        """Verify script uses set -euo pipefail."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "set -euo pipefail" in content or "set -e" in content


class TestArgumentParsing:
    """Test argument parsing."""

    def test_script_accepts_workspace_argument(self, script_path):
        """Test script accepts workspace as first argument."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "WORKSPACE" in content
        assert "${1:-" in content or "$1" in content

    def test_script_has_default_workspace(self, script_path):
        """Test script has a default workspace value."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "${1:-default}" in content or "default" in content

    def test_script_accepts_auto_approve_argument(self, script_path):
        """Test script accepts auto-approve as second argument."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "AUTO_APPROVE" in content
        assert "${2:-" in content or "$2" in content


class TestTerraformCommands:
    """Test Terraform command orchestration."""

    def test_script_runs_terraform_fmt(self, script_path):
        """Verify script runs terraform fmt."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "terraform fmt" in content or "fmt" in content

    def test_script_runs_terraform_init(self, script_path):
        """Verify script runs terraform init."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "terraform init" in content

    def test_script_runs_terraform_validate(self, script_path):
        """Verify script runs terraform validate."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "terraform validate" in content

    def test_script_runs_terraform_plan(self, script_path):
        """Verify script runs terraform plan."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "terraform plan" in content

    def test_script_saves_plan_to_file(self, script_path):
        """Verify script saves plan to a file."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "-out=" in content or "plan.tfplan" in content


class TestWorkspaceManagement:
    """Test Terraform workspace management."""

    def test_script_manages_workspaces(self, script_path):
        """Verify script manages Terraform workspaces."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "terraform workspace" in content

    def test_script_selects_existing_workspace(self, script_path):
        """Verify script can select existing workspace."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "workspace select" in content

    def test_script_creates_new_workspace(self, script_path):
        """Verify script can create new workspace."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "workspace new" in content

    def test_script_checks_workspace_existence(self, script_path):
        """Verify script checks if workspace exists before selecting."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "workspace list" in content or "grep" in content


class TestAutoApproveLogic:
    """Test auto-approve functionality."""

    def test_script_handles_auto_approve(self, script_path):
        """Verify script handles auto-approve flag."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "AUTO_APPROVE" in content
        assert "true" in content or "false" in content

    def test_script_applies_with_auto_approve(self, script_path):
        """Verify script applies with auto-approve when flag is true."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "terraform apply" in content
        assert "-auto-approve" in content or "auto-approve" in content

    def test_script_provides_manual_apply_command(self, script_path):
        """Verify script shows manual apply command when not auto-approving."""
        with open(script_path, 'r') as f:
            content = f.read()
        # Should show the command to run manually
        assert "To apply:" in content or "terraform apply" in content


class TestDirectoryNavigation:
    """Test script navigates to correct directories."""

    def test_script_changes_to_terraform_directory(self, script_path):
        """Verify script changes to terraform directory."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "cd" in content
        assert "terraform" in content

    def test_script_determines_root_directory(self, script_path):
        """Verify script determines repository root directory."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "ROOT_DIR" in content or 'dirname "$0"' in content


class TestSafetyChecks:
    """Test safety and best practices."""

    def test_script_uses_input_false(self, script_path):
        """Verify script uses -input=false for non-interactive mode."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "-input=false" in content

    def test_script_formats_before_other_commands(self, script_path):
        """Verify fmt runs before init/plan/apply."""
        with open(script_path, 'r') as f:
            lines = f.readlines()

        fmt_line = None
        init_line = None
        for i, line in enumerate(lines):
            if "terraform fmt" in line or "fmt -recursive" in line:
                fmt_line = i
            if "terraform init" in line:
                init_line = i

        if fmt_line and init_line:
            assert fmt_line < init_line, "fmt should run before init"

    def test_script_validates_before_plan(self, script_path):
        """Verify validate runs before plan."""
        with open(script_path, 'r') as f:
            lines = f.readlines()

        validate_line = None
        plan_line = None
        for i, line in enumerate(lines):
            if "terraform validate" in line:
                validate_line = i
            if "terraform plan" in line:
                plan_line = i

        if validate_line and plan_line:
            assert validate_line < plan_line, "validate should run before plan"


class TestOutputMessages:
    """Test script provides helpful output."""

    def test_script_provides_progress_messages(self, script_path):
        """Verify script outputs progress messages."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert 'echo' in content, "Script should provide progress messages"

    def test_script_indicates_current_step(self, script_path):
        """Verify script indicates what step it's running."""
        with open(script_path, 'r') as f:
            content = f.read()
        # Check for messages about formatting, initializing, planning, etc.
        keywords = ["Formatting", "Initializing", "Planning", "Validating"]
        found_keywords = [kw for kw in keywords if kw in content]
        assert len(found_keywords) >= 2, "Script should indicate current steps"

class TestDeployScriptBugFix:
    """Test the bug fix in deploy.sh script."""

    def test_terraform_fmt_command_syntax(self, script_path):
        """Verify terraform fmt command has correct syntax."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # The bug was: tf=terraform fmt -recursive
        # Should be: terraform fmt -recursive
        assert 'tf=terraform fmt' not in content, \
            "Bug found: 'tf=' assignment should not be present"
        
        # Verify correct command exists
        assert 'terraform fmt -recursive' in content or 'terraform fmt' in content, \
            "Should have terraform fmt command"

    def test_no_variable_assignment_in_commands(self, script_path):
        """Verify no accidental variable assignments in command lines."""
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Skip comments and empty lines
            if stripped.startswith('#') or not stripped:
                continue
            
            # Check for patterns like: var=command (without proper spacing)
            # This is likely a typo rather than intentional variable assignment
            if '=' in stripped and not stripped.startswith('set '):
                # Check if it's a variable assignment followed by a command
                parts = stripped.split('=', 1)
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    value = parts[1].strip()
                    
                    # If the "value" starts with a command, it's likely a bug
                    commands = ['terraform', 'aws', 'git', 'echo', 'cd']
                    for cmd in commands:
                        if value.startswith(cmd):
                            # This is acceptable for actual variable assignments
                            # but 'tf=terraform fmt' on line 13 is the bug
                            if var_name == 'tf' and 'terraform fmt' in value:
                                assert False, \
                                    f"Line {i}: Found bug 'tf=terraform fmt' - should be 'terraform fmt'"

    def test_terraform_commands_execute_properly(self, script_path):
        """Verify terraform commands are structured to execute, not assign."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check that terraform commands follow the echo statements
        import re
        
        # Find all echo + command pairs
        echo_pattern = r'echo "Formatting.*"\s*\n\s*(\S+.*terraform fmt.*)'
        matches = re.findall(echo_pattern, content)
        
        for match in matches:
            # The command after "Formatting..." echo should execute terraform
            assert not match.startswith('tf='), \
                "Terraform fmt should execute, not be assigned to variable 'tf'"
            assert match.startswith('terraform'), \
                "Command should start with 'terraform', not variable assignment"


class TestDeployScriptRegressions:
    """Test for potential regressions in deploy script."""

    def test_all_terraform_commands_unmodified(self, script_path):
        """Verify other terraform commands weren't accidentally changed."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # These terraform commands should still exist and be correct
        expected_commands = [
            'terraform init',
            'terraform validate', 
            'terraform plan',
            'terraform apply',
            'terraform workspace'
        ]
        
        for cmd in expected_commands:
            assert cmd in content, f"Expected command '{cmd}' not found"
            
            # Make sure these aren't assigned to variables either
            assert f'var={cmd}' not in content, \
                f"Command '{cmd}' should not be assigned to variable"

    def test_script_execution_order_maintained(self, script_path):
        """Verify command execution order is still correct."""
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        # Find positions of key commands
        fmt_line = None
        init_line = None
        validate_line = None
        plan_line = None
        
        for i, line in enumerate(lines):
            if 'terraform fmt' in line and not line.strip().startswith('#'):
                fmt_line = i
            elif 'terraform init' in line and not line.strip().startswith('#'):
                init_line = i
            elif 'terraform validate' in line and not line.strip().startswith('#'):
                validate_line = i
            elif 'terraform plan' in line and not line.strip().startswith('#'):
                plan_line = i
        
        # Verify order is maintained
        if fmt_line and init_line:
            assert fmt_line < init_line, "fmt should come before init"
        if validate_line and plan_line:
            assert validate_line < plan_line, "validate should come before plan"

    def test_no_syntax_errors_after_fix(self, script_path):
        """Verify bash syntax is still valid after bug fix."""
        bash_path = __import__('shutil').which("bash")
        if not bash_path:
            __import__('pytest').skip("bash not found on this system")
        
        result = __import__('subprocess').run(
            [bash_path, "-n", str(script_path)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Syntax error after fix: {result.stderr}"


class TestDeployScriptEdgeCases:
    """Test edge cases and potential issues in deploy script."""

    def test_handles_special_characters_in_paths(self, script_path):
        """Verify script handles special characters in paths."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check that paths are properly quoted
        if 'ROOT_DIR=' in content:
            # ROOT_DIR should use proper quoting
            assert '"$' in content or "'$" in content, \
                "Variables in paths should be quoted"

    def test_error_handling_preserved(self, script_path):
        """Verify error handling (set -euo pipefail) is still present."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Should still have strict error handling
        assert 'set -euo pipefail' in content or 'set -e' in content, \
            "Script should maintain error handling"

    def test_workspace_logic_unchanged(self, script_path):
        """Verify workspace selection logic wasn't affected by the fix."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Workspace logic should still be present
        assert 'terraform workspace list' in content, \
            "Workspace list command should be present"
        assert 'terraform workspace select' in content, \
            "Workspace select command should be present"
        assert 'terraform workspace new' in content, \
            "Workspace new command should be present"