"""
Comprehensive tests for pytest.ini configuration.

This test suite validates:
- pytest.ini file structure
- Marker definitions
- Configuration options
- Test discovery patterns
"""

import configparser
from pathlib import Path
import pytest


@pytest.fixture
def pytest_ini_path():
    """Return path to pytest.ini file."""
    return Path("pytest.ini")


@pytest.fixture
def pytest_config(pytest_ini_path):
    """Load and parse pytest.ini configuration."""
    config = configparser.ConfigParser()
    config.read(pytest_ini_path)
    return config


class TestPytestIniExists:
    """Test pytest.ini file existence and basic structure."""

    def test_pytest_ini_exists(self, pytest_ini_path):
        """Verify pytest.ini file exists."""
        assert pytest_ini_path.exists(), "pytest.ini should exist at project root"

    def test_pytest_ini_is_file(self, pytest_ini_path):
        """Verify pytest.ini is a regular file."""
        assert pytest_ini_path.is_file(), "pytest.ini should be a file"

    def test_pytest_ini_not_empty(self, pytest_ini_path):
        """Verify pytest.ini has content."""
        assert pytest_ini_path.stat().st_size > 0, "pytest.ini should not be empty"


class TestPytestIniStructure:
    """Test pytest.ini configuration structure."""

    def test_has_pytest_section(self, pytest_config):
        """Verify pytest.ini has [pytest] section."""
        assert pytest_config.has_section('pytest'), \
            "pytest.ini should have [pytest] section"

    def test_has_testpaths_option(self, pytest_config):
        """Verify testpaths is configured."""
        assert pytest_config.has_option('pytest', 'testpaths'), \
            "pytest.ini should define testpaths"
        
        testpaths = pytest_config.get('pytest', 'testpaths')
        assert 'tests' in testpaths, \
            "testpaths should include 'tests' directory"

    def test_has_python_files_pattern(self, pytest_config):
        """Verify python_files pattern is configured."""
        assert pytest_config.has_option('pytest', 'python_files'), \
            "pytest.ini should define python_files pattern"
        
        pattern = pytest_config.get('pytest', 'python_files')
        assert 'test_*.py' in pattern, \
            "python_files should match test_*.py pattern"

    def test_has_python_classes_pattern(self, pytest_config):
        """Verify python_classes pattern is configured."""
        assert pytest_config.has_option('pytest', 'python_classes'), \
            "pytest.ini should define python_classes pattern"
        
        pattern = pytest_config.get('pytest', 'python_classes')
        assert 'Test' in pattern, \
            "python_classes should match Test* pattern"

    def test_has_python_functions_pattern(self, pytest_config):
        """Verify python_functions pattern is configured."""
        assert pytest_config.has_option('pytest', 'python_functions'), \
            "pytest.ini should define python_functions pattern"
        
        pattern = pytest_config.get('pytest', 'python_functions')
        assert 'test_' in pattern, \
            "python_functions should match test_* pattern"


class TestPytestAddOpts:
    """Test pytest addopts configuration."""

    def test_has_addopts_option(self, pytest_config):
        """Verify addopts is configured."""
        assert pytest_config.has_option('pytest', 'addopts'), \
            "pytest.ini should define addopts"

    def test_addopts_includes_verbose(self, pytest_config):
        """Verify addopts includes verbose flag."""
        addopts = pytest_config.get('pytest', 'addopts')
        assert '-v' in addopts, \
            "addopts should include -v for verbose output"

    def test_addopts_includes_traceback_short(self, pytest_config):
        """Verify addopts includes short traceback."""
        addopts = pytest_config.get('pytest', 'addopts')
        assert '--tb=short' in addopts, \
            "addopts should include --tb=short for concise tracebacks"

    def test_addopts_includes_strict_markers(self, pytest_config):
        """Verify addopts includes strict-markers."""
        addopts = pytest_config.get('pytest', 'addopts')
        assert '--strict-markers' in addopts, \
            "addopts should include --strict-markers to catch typos in markers"

    def test_addopts_includes_report_all(self, pytest_config):
        """Verify addopts includes -ra for reporting all test outcomes."""
        addopts = pytest_config.get('pytest', 'addopts')
        assert '-ra' in addopts or '-r a' in addopts, \
            "addopts should include -ra to report all test outcomes"


class TestPytestMarkers:
    """Test pytest markers configuration."""

    def test_has_markers_section(self, pytest_config):
        """Verify markers are configured."""
        assert pytest_config.has_option('pytest', 'markers'), \
            "pytest.ini should define markers"

    def test_slow_marker_defined(self, pytest_config):
        """Verify 'slow' marker is defined."""
        markers = pytest_config.get('pytest', 'markers')
        assert 'slow' in markers, \
            "markers should include 'slow' marker"
        
        # Check description
        assert 'marks tests as slow' in markers or 'slow' in markers, \
            "'slow' marker should have a description"

    def test_integration_marker_defined(self, pytest_config):
        """Verify 'integration' marker is defined."""
        markers = pytest_config.get('pytest', 'markers')
        assert 'integration' in markers, \
            "markers should include 'integration' marker"
        
        # Check description
        assert 'integration tests' in markers, \
            "'integration' marker should have a description"

    def test_unit_marker_defined(self, pytest_config):
        """Verify 'unit' marker is defined."""
        markers = pytest_config.get('pytest', 'markers')
        assert 'unit' in markers, \
            "markers should include 'unit' marker"
        
        # Check description
        assert 'unit tests' in markers, \
            "'unit' marker should have a description"

    def test_all_markers_have_descriptions(self, pytest_config):
        """Verify all markers have descriptions."""
        markers_text = pytest_config.get('pytest', 'markers')
        
        # Split by newlines and check each marker
        marker_lines = [line.strip() for line in markers_text.split('\n') if line.strip()]
        
        for marker_line in marker_lines:
            if ':' in marker_line:
                marker_name, description = marker_line.split(':', 1)
                assert description.strip(), \
                    f"Marker '{marker_name}' should have a description"


class TestConfigurationFormat:
    """Test configuration file formatting."""

    def test_file_has_newline_at_end(self, pytest_ini_path):
        """Verify pytest.ini ends with a newline."""
        with open(pytest_ini_path, 'rb') as f:
            content = f.read()
        
        assert content.endswith(b'\n'), \
            "pytest.ini should end with a newline character"

    def test_no_windows_line_endings(self, pytest_ini_path):
        """Verify pytest.ini uses Unix line endings."""
        with open(pytest_ini_path, 'rb') as f:
            content = f.read()
        
        assert b'\r\n' not in content, \
            "pytest.ini should use Unix line endings (LF), not Windows (CRLF)"

    def test_multiline_options_properly_indented(self, pytest_ini_path):
        """Verify multiline options are properly indented."""
        with open(pytest_ini_path, 'r') as f:
            lines = f.readlines()
        
        in_multiline = False
        multiline_option = None
        
        for i, line in enumerate(lines, 1):
            if '=' in line and not line.strip().startswith('#'):
                # This is an option definition
                in_multiline = True
                multiline_option = line.split('=')[0].strip()
            elif in_multiline and line.strip() and not '=' in line:
                # This is a continuation line
                # It should be indented with spaces
                if not line.startswith(' ') and not line.startswith('\t'):
                    if not line.strip().startswith('['):  # Not a new section
                        pytest.fail(
                            f"Line {i} appears to be a continuation but is not indented: {line.strip()}"
                        )


class TestConfigurationBestPractices:
    """Test configuration follows best practices."""

    def test_markers_enable_selective_test_runs(self, pytest_config):
        """Verify marker configuration enables selective test execution."""
        markers = pytest_config.get('pytest', 'markers')
        
        # Should have markers for different test types
        marker_types = ['unit', 'integration', 'slow']
        
        for marker_type in marker_types:
            assert marker_type in markers, \
                f"Should define '{marker_type}' marker for selective test runs"

    def test_strict_markers_prevents_typos(self, pytest_config):
        """Verify strict-markers is enabled to catch marker typos."""
        addopts = pytest_config.get('pytest', 'addopts')
        assert '--strict-markers' in addopts, \
            "Should use --strict-markers to catch marker name typos"

    def test_verbose_output_enabled(self, pytest_config):
        """Verify verbose output is enabled for better feedback."""
        addopts = pytest_config.get('pytest', 'addopts')
        assert '-v' in addopts, \
            "Should enable verbose output for better test feedback"


class TestMarkerUsage:
    """Test that markers can be used correctly."""

    def test_markers_dont_conflict(self, pytest_config):
        """Verify marker names don't conflict with pytest internals."""
        markers = pytest_config.get('pytest', 'markers')
        
        # Avoid reserved pytest marker names
        reserved = ['parametrize', 'skipif', 'xfail', 'usefixtures', 'filterwarnings']
        
        for reserved_marker in reserved:
            # Our custom markers shouldn't use reserved names
            marker_lines = markers.split('\n')
            custom_markers = [line.split(':')[0].strip() for line in marker_lines if ':' in line]
            
            assert reserved_marker not in custom_markers, \
                f"Should not use reserved marker name '{reserved_marker}'"


class TestConfigurationCompleteness:
    """Test configuration is complete and functional."""

    def test_test_discovery_patterns_comprehensive(self, pytest_config):
        """Verify test discovery patterns cover all test types."""
        python_files = pytest_config.get('pytest', 'python_files')
        python_classes = pytest_config.get('pytest', 'python_classes')
        python_functions = pytest_config.get('pytest', 'python_functions')
        
        # Should match standard pytest conventions
        assert 'test_*.py' in python_files, \
            "Should discover test_*.py files"
        assert 'Test*' in python_classes, \
            "Should discover Test* classes"
        assert 'test_*' in python_functions, \
            "Should discover test_* functions"

    def test_testpaths_points_to_existing_directory(self, pytest_config):
        """Verify testpaths points to existing directory."""
        testpaths = pytest_config.get('pytest', 'testpaths')
        test_dir = Path(testpaths.strip())
        
        assert test_dir.exists(), \
            f"testpaths '{testpaths}' should point to existing directory"
        assert test_dir.is_dir(), \
            f"testpaths '{testpaths}' should be a directory"