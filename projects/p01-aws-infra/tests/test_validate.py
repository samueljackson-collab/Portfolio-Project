"""Validation tests for CloudFormation templates and governance docs."""

from pathlib import Path

import pytest
import yaml


class IntrinsicSafeLoader(yaml.SafeLoader):
    """YAML loader that tolerates CloudFormation intrinsic functions."""


def _intrinsic_constructor(loader: yaml.SafeLoader, tag_suffix: str, node):
    if isinstance(node, yaml.ScalarNode):
        value = loader.construct_scalar(node)
    elif isinstance(node, yaml.SequenceNode):
        value = loader.construct_sequence(node)
    else:
        value = loader.construct_mapping(node)
    return {tag_suffix: value}


IntrinsicSafeLoader.add_multi_constructor("!", _intrinsic_constructor)


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_template(root: Path, name: str) -> dict:
    template_path = root / "infra" / name
    with open(template_path) as handle:
        return yaml.load(handle, Loader=IntrinsicSafeLoader)


def test_master_factory_document_exists(project_root: Path):
    """Ensure the master factory document anchors CI/IaC stages."""
    doc = project_root / "master-factory" / "MASTER_FACTORY.md"
    assert doc.exists(), "MASTER_FACTORY.md should describe the pipeline contract"

    content = doc.read_text()
    for stage in [
        "Lint",
        "Terraform Plan",
        "CloudFormation Change Sets",
        "Gated Apply",
    ]:
        assert stage in content, f"Missing stage reference: {stage}"


def test_templates_are_present(project_root: Path):
    """Both VPC and dedicated RDS templates should exist for validation runs."""
    vpc_template = project_root / "infra" / "vpc-rds.yaml"
    rds_template = project_root / "infra" / "rds.yaml"
    assert vpc_template.exists()
    assert rds_template.exists()


@pytest.mark.parametrize("template_name", ["vpc-rds.yaml", "rds.yaml"])
def test_templates_have_required_sections(project_root: Path, template_name: str):
    """Templates must include version, resources, and outputs."""
    data = _load_template(project_root, template_name)

    assert data.get("AWSTemplateFormatVersion")
    assert "Resources" in data
    assert "Outputs" in data


def test_rds_template_hardens_database(project_root: Path):
    """RDS template should enable Multi-AZ, encryption, and private access."""
    data = _load_template(project_root, "rds.yaml")

    db_props = data["Resources"]["DBInstance"]["Properties"]
    assert db_props["MultiAZ"] is True
    assert db_props["StorageEncrypted"] is True
    assert db_props["PubliclyAccessible"] is False
    retention = db_props["BackupRetentionPeriod"]
    if isinstance(retention, dict) and "Ref" in retention:
        param_default = data["Parameters"]["BackupRetentionDays"]["Default"]
        assert param_default >= 7
    else:
        assert retention >= 7


def test_rds_template_outputs_surface_identifiers(project_root: Path):
    data = _load_template(project_root, "rds.yaml")

    outputs = data.get("Outputs", {})
    for key in [
        "DBInstanceIdentifier",
        "DBEndpoint",
        "RdsSecurityGroupId",
        "DbSubnetGroupName",
    ]:
        assert key in outputs, f"Expected output {key}"
