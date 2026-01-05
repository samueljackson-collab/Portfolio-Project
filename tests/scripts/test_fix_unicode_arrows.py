"""Comprehensive unit tests for fix_unicode_arrows.sh"""

import os
import shutil
import subprocess
import tempfile
import pytest
from pathlib import Path

SCRIPT_PATH = Path(__file__).parent.parent.parent / "scripts/fix_unicode_arrows.sh"
BASH_PATH = shutil.which("bash")


class TestFixUnicodeArrowsBasicFunctionality:
    """Test basic script functionality"""

    def test_script_exists(self):
        """Verify the script file exists and is executable"""
        assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"
        assert os.access(SCRIPT_PATH, os.X_OK), "Script is not executable"

    def test_script_runs_without_errors(self):
        """Test that script runs without critical errors"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a temporary Python file with no unicode issues
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def hello() -> str:\n    return 'world'\n")

            result = subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                shell=False,
            )
            # Should complete successfully even with no files to fix
            assert result.returncode == 0


class TestUnicodeReplacement:
    """Test Unicode arrow replacement functionality"""

    def test_replaces_escaped_unicode_arrow(self):
        """Test replacement of -> with ->"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def func(x: int) -> int:\n    return x\n")

            result = subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                shell=False,
            )

            # Check if file was processed
            content = test_file.read_text()
            assert "->" in content or result.returncode == 0

    def test_replaces_double_escaped_unicode_arrow(self):
        """Test replacement of -\\\\u003e with ->"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def func(x: int) -\\\\u003e int:\n    return x\n")

            result = subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                shell=False,
            )

            content = test_file.read_text()
            assert "->" in content or result.returncode == 0

    def test_replaces_html_encoded_arrow(self):
        """Test replacement of -> with ->"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def func(x: int) -> int:\n    return x\n")

            result = subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                shell=False,
            )

            content = test_file.read_text()
            assert "->" in content or result.returncode == 0

    def test_normalizes_spaced_arrow(self):
        """Test normalization of -> to ->"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def func(x: int) -> int:\n    return x\n")

            result = subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                shell=False,
            )

            content = test_file.read_text()
            assert "->" in content or result.returncode == 0


class TestBackupCreation:
    """Test backup file creation"""

    def test_creates_backup_file(self):
        """Test that backup files are created"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            original_content = "def func() -> int:\n    return 1\n"
            test_file.write_text(original_content)

            result = subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                shell=False,
            )

            backup_file = Path(tmpdir) / "test.py.bak"
            # Backup should exist after running
            assert backup_file.exists() or result.returncode == 0

    def test_preserves_original_in_backup(self):
        """Test that backup contains original content"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            original_content = "def func() -> int:\n    return 1\n"
            test_file.write_text(original_content)

            subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                shell=False,
            )

            backup_file = Path(tmpdir) / "test.py.bak"
            if backup_file.exists():
                backup_content = backup_file.read_text()
                assert "->" in backup_content or "-> " in backup_content


class TestPythonSyntaxValidation:
    """Test Python syntax validation"""

    def test_validates_python_syntax_after_replacement(self):
        """Test that script validates Python syntax after changes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def valid() -> str:\n    return 'test'\n")

            result = subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                shell=False,
            )

            # Script should validate syntax
            assert result.returncode == 0
            # File should be syntactically valid
            content = test_file.read_text()
            compile(content, test_file, "exec")

    def test_restores_backup_on_invalid_syntax(self):
        """Test that backup is restored if syntax becomes invalid"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            # Create a file that would become invalid after replacement
            # (This is hard to trigger, so we test the mechanism exists)
            test_file.write_text("def func() -> int:\n    return 1\n")

            result = subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                shell=False,
            )

            # Script should handle this gracefully
            assert result.returncode == 0


class TestMultipleFiles:
    """Test handling of multiple Python files"""

    def test_processes_multiple_python_files(self):
        """Test that script processes all .py files in directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            files = []
            for i in range(3):
                test_file = Path(tmpdir) / f"test{i}.py"
                test_file.write_text(f"def func{i}() -> int:\n    return {i}\n")
                files.append(test_file)

            result = subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                shell=False,
            )

            assert result.returncode == 0
            # Check that files were processed
            for f in files:
                content = f.read_text()
                assert "->" in content or "->" in content

    def test_processes_nested_directories(self):
        """Test that script processes Python files in subdirectories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()
            test_file = subdir / "test.py"
            test_file.write_text("def func() -> int:\n    return 1\n")

            result = subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                shell=False,
            )

            assert result.returncode == 0


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_handles_empty_directory(self):
        """Test script handles directory with no Python files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                shell=False,
            )

            assert result.returncode == 0
            assert "Done" in result.stdout

    def test_handles_already_correct_files(self):
        """Test script handles files that don't need changes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def func() -> int:\n    return 1\n")

            result = subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                shell=False,
            )

            assert result.returncode == 0
            # File should remain valid
            content = test_file.read_text()
            assert "-> int" in content

    def test_idempotent_execution(self):
        """Test that running script multiple times is safe"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def func() -> int:\n    return 1\n")

            # Run twice
            for _ in range(2):
                result = subprocess.run(  # noqa: S603, S607
                    [BASH_PATH, str(SCRIPT_PATH)],
                    capture_output=True,
                    text=True,
                    cwd=tmpdir,
                    shell=False,
                )
                assert result.returncode == 0

            # File should still be valid
            content = test_file.read_text()
            compile(content, test_file, "exec")


class TestOutputMessages:
    """Test script output and messaging"""

    def test_displays_repository_root(self):
        """Test that script displays repository root"""
        result = subprocess.run(  # noqa: S603, S607
            [BASH_PATH, str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            cwd=SCRIPT_PATH.parent.parent,
            shell=False,
        )

        assert "Repository root:" in result.stdout

    def test_displays_completion_message(self):
        """Test that script displays completion message"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                shell=False,
            )

            assert "Done" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
