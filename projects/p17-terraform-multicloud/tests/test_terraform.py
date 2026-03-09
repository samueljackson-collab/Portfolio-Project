"""Test Terraform configuration."""

import pytest
from pathlib import Path


def test_aws_module_exists():
    """Test AWS module exists."""
    module_path = Path(__file__).parent.parent / "modules" / "aws" / "main.tf"
    assert module_path.exists()


def test_terraform_files_valid():
    """Test Terraform files have .tf extension."""
    modules_dir = Path(__file__).parent.parent / "modules"
    tf_files = list(modules_dir.rglob("*.tf"))
    assert len(tf_files) > 0
