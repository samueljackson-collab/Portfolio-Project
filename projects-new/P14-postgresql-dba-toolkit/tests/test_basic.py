"""
Test suite for P14-postgresql-dba-toolkit
PostgreSQL database administration toolkit
"""

import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def test_basic():
    """Basic test to ensure test framework is working."""
    assert True


def test_project_structure():
    """Test that project structure contains required files."""
    required_files = ["README.md"]
    for filename in required_files:
        assert (PROJECT_ROOT / filename).exists(), f"Missing required file: {filename}"


def test_migrations_directory_exists():
    """Test that migrations directory exists."""
    migrations_dir = PROJECT_ROOT / "migrations"
    assert migrations_dir.exists(), "Missing migrations directory"


def test_documentation_exists():
    """Test that documentation exists."""
    docs_dir = PROJECT_ROOT / "docs"
    assert docs_dir.exists(), "Missing docs directory"


def test_scripts_directory_exists():
    """Test that scripts directory exists."""
    scripts_dir = PROJECT_ROOT / "scripts"
    assert scripts_dir.exists(), "Missing scripts directory"


def test_sql_scripts_exist():
    """Test that SQL scripts exist."""
    sql_dir = PROJECT_ROOT / "sql"
    assert sql_dir.exists(), "Missing sql directory"
