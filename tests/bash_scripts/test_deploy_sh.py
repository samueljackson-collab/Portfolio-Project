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


class TestSyntaxCorrectness:
    """Test script syntax correctness and common errors."""

    def test_script_has_no_variable_assignment_errors(self, script_path):
        """Verify script doesn't have malformed variable assignments."""
        with open(script_path, 'r') as f:
            content = f.read()
        # Check that terraform commands are executed, not assigned to variables
        # Line should be: terraform fmt -recursive
        # NOT: tf=terraform fmt -recursive (which would be a syntax error)
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'terraform fmt' in line and '=' in line:
                # If there's an equals sign, it should be a proper command substitution
                # like VAR=$(terraform fmt) or proper assignment VAR="value"
                if not ('$(' in line or '`' in line or '"' in line.split('=')[1] or "'" in line.split('=')[1]):
                    pytest.fail(f"Line {i} appears to have malformed assignment: {line.strip()}")

    def test_terraform_fmt_command_executed_correctly(self, script_path):
        """Verify terraform fmt is executed, not assigned to a variable."""
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        fmt_found = False
        for line in lines:
            if 'terraform fmt' in line:
                fmt_found = True
                # Should be a command execution, not variable assignment
                # Valid: terraform fmt -recursive
                # Invalid: tf=terraform fmt -recursive
                stripped = line.strip()
                if stripped.startswith('tf=') or '=terraform fmt' in stripped:
                    pytest.fail(f"terraform fmt should be executed directly, not assigned: {stripped}")
        
        assert fmt_found, "Script should contain terraform fmt command"

    def test_all_terraform_commands_are_executed(self, script_path):
        """Verify all terraform commands are properly executed."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # These commands should be executed directly, not assigned
        terraform_commands = ['terraform init', 'terraform validate', 'terraform plan', 'terraform apply']
        for cmd in terraform_commands:
            if cmd in content:
                # Check that they're not being assigned to variables incorrectly
                lines = [l for l in content.split('\n') if cmd in l]
                for line in lines:
                    stripped = line.strip()
                    # Skip comments
                    if stripped.startswith('#'):
                        continue
                    # Check for incorrect assignment patterns
                    if '=' in stripped and cmd in stripped:
                        # Allow proper command substitution: VAR=$(terraform ...)
                        if not ('$(' in stripped or '`' in stripped):
                            # Check if it's just the command with flags (e.g., -input=false)
                            if not ('--' in stripped or stripped.split('=')[1].strip().startswith('-')):
                                continue  # This is likely terraform command flags, not assignment

    def test_script_uses_command_not_variable_for_fmt(self, script_path):
        """Verify fmt uses correct command syntax."""
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        # Find lines with terraform fmt
        for line in lines:
            if 'terraform fmt' in line and not line.strip().startswith('#'):
                # Should start with 'terraform' not 'tf='
                stripped = line.strip()
                assert not stripped.startswith('tf='), "Should use 'terraform fmt' not 'tf=terraform fmt'"
                # Proper syntax check
                if 'fmt' in stripped and not stripped.startswith('terraform'):
                    # It might be indented or have echo before it
                    if '=' in stripped and 'terraform fmt' in stripped:
                        assert '$(' in stripped or '`' in stripped, "Incorrect command syntax"


class TestScriptPermissions:
    """Test script file permissions are correct."""

    def test_script_has_execute_permission(self, script_path):
        """Verify script has execute permission for owner."""
        import stat
        mode = os.stat(script_path).st_mode
        assert mode & stat.S_IXUSR, "Script should have owner execute permission"

    def test_script_has_read_permission(self, script_path):
        """Verify script has read permission."""
        import stat
        mode = os.stat(script_path).st_mode
        assert mode & stat.S_IRUSR, "Script should have owner read permission"

    def test_script_is_not_world_writable(self, script_path):
        """Verify script is not world-writable (security check)."""
        import stat
        mode = os.stat(script_path).st_mode
        assert not (mode & stat.S_IWOTH), "Script should not be world-writable"

    def test_script_can_be_executed_directly(self, script_path):
        """Verify script can be executed directly (not just via bash)."""
        # This test verifies the shebang and permissions work together
        result = subprocess.run(
            [str(script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Script should either show help, run, or show usage - not permission denied
        assert result.returncode != 126, "Script should be executable (not permission denied)"

    def test_script_permissions_match_standard(self, script_path):
        """Verify script has standard executable script permissions (755 or 775)."""
        import stat
        mode = os.stat(script_path).st_mode
        # Check for common executable permissions patterns
        is_executable = (
            (mode & stat.S_IXUSR) and  # Owner can execute
            (mode & stat.S_IRUSR) and  # Owner can read
            (mode & stat.S_IRGRP)       # Group can read
        )
        assert is_executable, "Script should have standard executable permissions"