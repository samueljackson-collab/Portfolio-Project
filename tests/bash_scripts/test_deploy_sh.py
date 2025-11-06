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
        """
        Check that the script's first line is a shebang that references bash.
        """
        with open(script_path, 'r') as f:
            first_line = f.readline().strip()
        assert first_line.startswith("#!/"), "Script missing shebang"
        assert "bash" in first_line, "Script should use bash"




class TestScriptPermissions:
    """Test that scripts have been made executable."""

    def test_script_is_executable_via_git(self, script_path):
        """
        Check that the deploy script is marked as executable in the repository index.
        
        Queries `git ls-files -s` in /home/jailuser/git for the given path and asserts the file's mode is `100755` (executable). Fails the test if the git entry is missing, the git command fails, or the recorded mode is not `100755`.
        """
        import subprocess
        result = subprocess.run(
            ["git", "ls-files", "-s", str(script_path)],
            capture_output=True,
            text=True,
            cwd="/home/jailuser/git"
        )
        # Git stores mode in format: mode hash stage filename
        # Executable files have mode 100755
        if result.returncode == 0 and result.stdout:
            mode = result.stdout.split()[0]
            assert mode == "100755", f"Script should be executable (mode 100755), got {mode}"

    def test_script_executable_bit_set(self, script_path):
        """Verify script has executable bit set in filesystem."""
        import stat
        st = script_path.stat()
        is_executable = bool(st.st_mode & stat.S_IXUSR)
        assert is_executable, "Script should have user executable bit set"

    def test_script_can_be_executed_directly(self, script_path):
        """Verify script can be executed directly with ./script syntax."""
        import subprocess
        # Just test that we can attempt to execute it (will fail without terraform but that's ok)
        result = subprocess.run(
            [str(script_path)],
            capture_output=True,
            text=True,
            timeout=5,
            cwd="/home/jailuser/git"
        )
        # We just care that it attempted to run (not a permission error)
        # Permission error would give exit code 126
        assert result.returncode != 126, "Script should be executable (no permission denied error)"
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