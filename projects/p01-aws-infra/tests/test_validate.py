"""Unit tests for CloudFormation template validation."""
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def vpc_template(project_root):
    """Get VPC CloudFormation template path."""
    return project_root / "infra" / "vpc-rds.yaml"


def test_vpc_template_exists(vpc_template):
    """Verify VPC template file exists."""
    assert vpc_template.exists(), f"Template not found: {vpc_template}"


def test_vpc_template_valid_yaml(vpc_template):
    """Verify VPC template is valid YAML."""
    import yaml
    with open(vpc_template) as f:
        data = yaml.safe_load(f)
    assert data is not None
    assert "AWSTemplateFormatVersion" in data
    assert "Resources" in data


def test_vpc_template_has_required_resources(vpc_template):
    """Verify VPC template contains expected resources."""
    import yaml
    with open(vpc_template) as f:
        data = yaml.safe_load(f)

    resources = data.get("Resources", {})
    required_resources = [
        "VPC",
        "InternetGateway",
        "PublicSubnet1",
        "PublicSubnet2",
        "PublicSubnet3",
        "PrivateSubnet1",
        "PrivateSubnet2",
        "PrivateSubnet3",
        "DBInstance",
        "DBSecurityGroup",
    ]

    for resource in required_resources:
        assert resource in resources, f"Missing resource: {resource}"


def test_vpc_template_has_outputs(vpc_template):
    """Verify VPC template defines outputs for downstream use."""
    import yaml
    with open(vpc_template) as f:
        data = yaml.safe_load(f)

    outputs = data.get("Outputs", {})
    required_outputs = ["VPCId", "DBInstanceIdentifier", "DBEndpoint"]

    for output in required_outputs:
        assert output in outputs, f"Missing output: {output}"


def test_rds_multi_az_enabled(vpc_template):
    """Verify RDS instance has Multi-AZ enabled."""
    import yaml
    with open(vpc_template) as f:
        data = yaml.safe_load(f)

    rds_props = data["Resources"]["DBInstance"]["Properties"]
    assert rds_props.get("MultiAZ") is True, "RDS Multi-AZ should be enabled"


def test_rds_backup_retention(vpc_template):
    """Verify RDS has backup retention configured."""
    import yaml
    with open(vpc_template) as f:
        data = yaml.safe_load(f)

    rds_props = data["Resources"]["DBInstance"]["Properties"]
    retention = rds_props.get("BackupRetentionPeriod", 0)
    assert retention >= 7, "RDS backup retention should be at least 7 days"


def test_validate_script_exists(project_root):
    """Verify validation script exists."""
    script = project_root / "src" / "validate_template.py"
    assert script.exists(), f"Validation script not found: {script}"


@pytest.mark.skipif(
    subprocess.run(["which", "aws"], capture_output=True).returncode != 0,
    reason="AWS CLI not installed"
)
def test_aws_cli_validation(vpc_template):
    """Run AWS CloudFormation validate-template (requires AWS CLI)."""
    result = subprocess.run(
        ["aws", "cloudformation", "validate-template", "--template-body", f"file://{vpc_template}"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"AWS validation failed: {result.stderr}"
