"""Unit tests for Terraform module composition."""
from pathlib import Path


def _read(path: Path) -> str:
    return path.read_text()


def test_state_module_creates_backing_services():
    """State module should provision an S3 bucket and DynamoDB table when enabled."""
    module = _read(Path("terraform/modules/state/main.tf"))
    assert "aws_s3_bucket" in module
    assert "aws_dynamodb_table" in module


def test_network_module_provisions_core_network():
    module = _read(Path("terraform/modules/network/main.tf"))
    for resource in ["aws_vpc", "aws_internet_gateway", "aws_subnet", "aws_route_table"]:
        assert resource in module


def test_root_module_wires_child_modules():
    root = _read(Path("terraform/main.tf"))
    assert "module \"state\"" in root
    assert "module \"network\"" in root
