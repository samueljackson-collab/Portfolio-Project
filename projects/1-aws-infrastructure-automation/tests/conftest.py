"""
Pytest configuration and shared fixtures for infrastructure tests.
"""

import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def project_root_dir():
    """Provide the project root directory path."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def terraform_root():
    """Provide the Terraform directory path."""
    return Path(__file__).parent.parent / "terraform"


@pytest.fixture(scope="session")
def cdk_root():
    """Provide the CDK directory path."""
    return Path(__file__).parent.parent / "cdk"


@pytest.fixture(scope="session")
def pulumi_root():
    """Provide the Pulumi directory path."""
    return Path(__file__).parent.parent / "pulumi"
