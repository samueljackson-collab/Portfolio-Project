#!/usr/bin/env python
"""
Backend setup verification script.

This script verifies that all required components are in place
and the backend is properly configured.
"""

import os
import sys
from pathlib import Path


def check_file_exists(file_path: str, description: str) -> bool:
    """
    Determine whether a file exists at the given path and print a status line.
    
    Parameters:
        file_path (str): Path to the file to check.
        description (str): Human-readable label included in the printed status message.
    
    Returns:
        exists (bool): True if the file exists, False otherwise.
    """
    if Path(file_path).exists():
        print(f"✓ {description}: {file_path}")
        return True
    else:
        print(f"✗ {description}: {file_path} - NOT FOUND")
        return False


def check_directory_exists(dir_path: str, description: str) -> bool:
    """
    Determine whether a filesystem path exists and is a directory, printing a success or failure line.
    
    Parameters:
        dir_path (str): Path to check.
        description (str): Human-readable label used in the printed message.
    
    Returns:
        bool: `True` if `dir_path` exists and is a directory, `False` otherwise.
    """
    if Path(dir_path).is_dir():
        print(f"✓ {description}: {dir_path}")
        return True
    else:
        print(f"✗ {description}: {dir_path} - NOT FOUND")
        return False


def verify_backend_setup() -> bool:
    """
    Verify that the repository contains the expected backend files, directories, and migration/test artifacts.
    
    Performs structured checks for configuration files, Docker files, application modules, API routers, Alembic migrations, test suite files, and documentation, printing a summary of results.
    
    Returns:
        True if all checks passed, False otherwise.
    """
    print("=" * 60)
    print("Backend Setup Verification")
    print("=" * 60)

    all_checks_passed = True

    # Check configuration files
    print("\n📝 Configuration Files:")
    all_checks_passed &= check_file_exists("requirements.txt", "Dependencies file")
    all_checks_passed &= check_file_exists(".env.example", "Environment template")
    all_checks_passed &= check_file_exists("pytest.ini", "Pytest configuration")
    all_checks_passed &= check_file_exists(".coveragerc", "Coverage configuration")
    all_checks_passed &= check_file_exists("alembic.ini", "Alembic configuration")

    # Check Docker files
    print("\n🐳 Docker Files:")
    all_checks_passed &= check_file_exists("Dockerfile", "Docker image definition")
    all_checks_passed &= check_file_exists("docker-compose.yml", "Docker Compose config")

    # Check application structure
    print("\n📦 Application Structure:")
    all_checks_passed &= check_directory_exists("app", "Application directory")
    all_checks_passed &= check_file_exists("app/__init__.py", "App init")
    all_checks_passed &= check_file_exists("app/main.py", "Main FastAPI app")
    all_checks_passed &= check_file_exists("app/config.py", "Configuration module")
    all_checks_passed &= check_file_exists("app/database.py", "Database module")
    all_checks_passed &= check_file_exists("app/models.py", "ORM models")
    all_checks_passed &= check_file_exists("app/schemas.py", "Pydantic schemas")
    all_checks_passed &= check_file_exists("app/auth.py", "Authentication module")
    all_checks_passed &= check_file_exists("app/dependencies.py", "Dependencies module")

    # Check routers
    print("\n🛣️  API Routers:")
    all_checks_passed &= check_directory_exists("app/routers", "Routers directory")
    all_checks_passed &= check_file_exists("app/routers/__init__.py", "Routers init")
    all_checks_passed &= check_file_exists("app/routers/health.py", "Health router")
    all_checks_passed &= check_file_exists("app/routers/auth.py", "Auth router")
    all_checks_passed &= check_file_exists("app/routers/content.py", "Content router")

    # Check Alembic migrations
    print("\n🗄️  Database Migrations:")
    all_checks_passed &= check_directory_exists("alembic", "Alembic directory")
    all_checks_passed &= check_file_exists("alembic/env.py", "Alembic environment")
    all_checks_passed &= check_file_exists("alembic/script.py.mako", "Migration template")
    all_checks_passed &= check_directory_exists("alembic/versions", "Migrations directory")

    # Check if there are any migration files
    versions_dir = Path("alembic/versions")
    migration_files = list(versions_dir.glob("*.py")) if versions_dir.exists() else []
    if migration_files:
        print(f"✓ Migration files found: {len(migration_files)}")
    else:
        print("⚠ Warning: No migration files found")

    # Check tests
    print("\n🧪 Test Suite:")
    all_checks_passed &= check_directory_exists("tests", "Tests directory")
    all_checks_passed &= check_file_exists("tests/__init__.py", "Tests init")
    all_checks_passed &= check_file_exists("tests/conftest.py", "Test configuration")
    all_checks_passed &= check_file_exists("tests/test_health.py", "Health tests")
    all_checks_passed &= check_file_exists("tests/test_auth.py", "Auth tests")
    all_checks_passed &= check_file_exists("tests/test_content.py", "Content tests")

    # Check documentation
    print("\n📚 Documentation:")
    all_checks_passed &= check_file_exists("README.md", "Backend documentation")

    # Summary
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("✅ All checks passed! Backend is properly configured.")
        print("=" * 60)
        return True
    else:
        print("❌ Some checks failed. Please review the setup.")
        print("=" * 60)
        return False


def verify_python_syntax() -> bool:
    """
    Check syntax of a set of critical Python source files used by the project.
    
    Attempts to compile each file in the script's predefined list and prints per-file status to stdout.
    Returns:
        bool: `True` if all files compiled without syntax errors and were present, `False` otherwise.
    """
    print("\n🔍 Verifying Python syntax...")

    python_files = [
        "app/main.py",
        "app/config.py",
        "app/database.py",
        "app/models.py",
        "app/schemas.py",
        "app/auth.py",
        "app/dependencies.py",
        "app/routers/health.py",
        "app/routers/auth.py",
        "app/routers/content.py",
        "alembic/env.py",
        "tests/conftest.py",
        "tests/test_health.py",
        "tests/test_auth.py",
        "tests/test_content.py",
    ]

    all_valid = True
    for py_file in python_files:
        try:
            with open(py_file, 'r') as f:
                compile(f.read(), py_file, 'exec')
            print(f"✓ {py_file}")
        except SyntaxError as e:
            print(f"✗ {py_file}: {e}")
            all_valid = False
        except FileNotFoundError:
            print(f"⚠ {py_file}: File not found")
            all_valid = False

    return all_valid


if __name__ == "__main__":
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Run verifications
    setup_ok = verify_backend_setup()
    syntax_ok = verify_python_syntax()

    # Exit with appropriate code
    if setup_ok and syntax_ok:
        print("\n🎉 Backend verification complete - all systems go!")
        sys.exit(0)
    else:
        print("\n⚠️  Backend verification found issues - please review")
        sys.exit(1)