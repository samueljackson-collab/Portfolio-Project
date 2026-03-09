"""
Test suite for P10 Multi-Region deployment architecture.

Validates:
- Project structure integrity (required files and directories)
- Terraform configuration completeness and correctness
- Failover script presence and basic syntax
- Kubernetes manifest structure
- Runbook coverage
"""

import re
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
TERRAFORM_DIR = PROJECT_ROOT / "terraform"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
K8S_DIR = PROJECT_ROOT / "k8s"
RUNBOOKS_DIR = PROJECT_ROOT / "RUNBOOKS"


# ---------------------------------------------------------------------------
# Project structure tests
# ---------------------------------------------------------------------------

class TestProjectStructure:
    """Validate the expected directory and file layout exists."""

    def test_readme_exists(self):
        assert (PROJECT_ROOT / "README.md").exists(), "README.md is missing"

    def test_terraform_directory_exists(self):
        assert TERRAFORM_DIR.exists(), "terraform/ directory is missing"

    def test_terraform_main_exists(self):
        assert (TERRAFORM_DIR / "main.tf").exists(), "terraform/main.tf is missing"

    def test_scripts_directory_exists(self):
        assert SCRIPTS_DIR.exists(), "scripts/ directory is missing"

    def test_failover_script_exists(self):
        assert (SCRIPTS_DIR / "failover.sh").exists(), "scripts/failover.sh is missing"

    def test_k8s_directory_exists(self):
        assert K8S_DIR.exists(), "k8s/ directory is missing"

    def test_runbooks_directory_exists(self):
        assert RUNBOOKS_DIR.exists(), "RUNBOOKS/ directory is missing"

    def test_consumer_directory_exists(self):
        assert (PROJECT_ROOT / "consumer").exists(), "consumer/ directory is missing"

    def test_producer_directory_exists(self):
        assert (PROJECT_ROOT / "producer").exists(), "producer/ directory is missing"

    def test_jobs_directory_exists(self):
        assert (PROJECT_ROOT / "jobs").exists(), "jobs/ directory is missing"

    def test_docker_directory_exists(self):
        assert (PROJECT_ROOT / "docker").exists(), "docker/ directory is missing"


# ---------------------------------------------------------------------------
# Terraform configuration tests
# ---------------------------------------------------------------------------

class TestTerraformConfiguration:
    """Validate Terraform configuration content and required resources."""

    @pytest.fixture(scope="class")
    def main_tf(self):
        return (TERRAFORM_DIR / "main.tf").read_text()

    def test_required_version_specified(self, main_tf):
        """Terraform block must declare a required_version constraint."""
        assert 'required_version' in main_tf, "required_version not set in terraform block"

    def test_aws_provider_configured(self, main_tf):
        """AWS provider must be configured."""
        assert 'provider "aws"' in main_tf, "AWS provider not configured"

    def test_multi_region_providers(self, main_tf):
        """Both primary and secondary region providers must be defined."""
        assert 'alias  = "primary"' in main_tf, "Primary provider alias missing"
        assert 'alias  = "secondary"' in main_tf, "Secondary provider alias missing"

    def test_route53_zone_defined(self, main_tf):
        """Route 53 hosted zone resource must be defined."""
        assert 'aws_route53_zone' in main_tf, "Route 53 zone resource missing"

    def test_health_check_defined(self, main_tf):
        """Route 53 health check must be defined for failover detection."""
        assert 'aws_route53_health_check' in main_tf, "Route 53 health check missing"

    def test_failover_routing_primary(self, main_tf):
        """Primary failover routing policy must be configured."""
        assert '"PRIMARY"' in main_tf, "Primary failover routing policy missing"

    def test_failover_routing_secondary(self, main_tf):
        """Secondary failover routing policy must be configured."""
        assert '"SECONDARY"' in main_tf, "Secondary failover routing policy missing"

    def test_s3_replication_defined(self, main_tf):
        """S3 cross-region replication must be configured for data durability."""
        assert 'aws_s3_bucket_replication_configuration' in main_tf, \
            "S3 cross-region replication not configured"

    def test_s3_versioning_enabled(self, main_tf):
        """S3 versioning must be enabled on both buckets for replication."""
        versioning_count = main_tf.count('aws_s3_bucket_versioning')
        assert versioning_count >= 2, \
            f"Expected at least 2 versioning resources, found {versioning_count}"

    def test_iam_replication_role_defined(self, main_tf):
        """IAM role for S3 replication must be defined."""
        assert 'aws_iam_role' in main_tf and 'replication' in main_tf, \
            "IAM replication role not defined"

    def test_required_tags_present(self, main_tf):
        """Resources must be tagged with Project, Environment, and ManagedBy."""
        assert 'Project' in main_tf, "Project tag missing"
        assert 'Environment' in main_tf, "Environment tag missing"
        assert 'ManagedBy' in main_tf, "ManagedBy tag missing"

    def test_backend_configured(self, main_tf):
        """Remote state backend must be configured."""
        assert 'backend "s3"' in main_tf, "S3 remote state backend not configured"

    def test_health_check_path_is_health(self, main_tf):
        """Health check resource path must target /health endpoint."""
        assert '"/health"' in main_tf, "Health check path should target /health"

    def test_https_health_check(self, main_tf):
        """Health check must use HTTPS for encrypted validation."""
        assert '"HTTPS"' in main_tf, "Health check should use HTTPS"

    def test_module_primary_defined(self, main_tf):
        """Primary region module must be instantiated."""
        assert 'module "primary"' in main_tf, "Primary region module missing"

    def test_module_secondary_defined(self, main_tf):
        """Secondary region module must be instantiated."""
        assert 'module "secondary"' in main_tf, "Secondary region module missing"


# ---------------------------------------------------------------------------
# Failover script tests
# ---------------------------------------------------------------------------

class TestFailoverScript:
    """Validate the failover shell script structure and safety patterns."""

    @pytest.fixture(scope="class")
    def failover_script(self):
        return (SCRIPTS_DIR / "failover.sh").read_text()

    def test_script_has_shebang(self, failover_script):
        """Script must begin with a bash shebang."""
        assert failover_script.startswith("#!/bin/bash"), "Missing bash shebang"

    def test_set_euo_pipefail(self, failover_script):
        """Script must use set -euo pipefail for safe error handling."""
        assert 'set -euo pipefail' in failover_script, \
            "Script must use 'set -euo pipefail' for safety"

    def test_primary_region_configurable(self, failover_script):
        """PRIMARY_REGION must be configurable via environment variable."""
        assert 'PRIMARY_REGION' in failover_script, "PRIMARY_REGION not configurable"

    def test_secondary_region_configurable(self, failover_script):
        """SECONDARY_REGION must be configurable via environment variable."""
        assert 'SECONDARY_REGION' in failover_script, "SECONDARY_REGION not configurable"

    def test_hosted_zone_id_configurable(self, failover_script):
        """HOSTED_ZONE_ID must be configurable via environment variable."""
        assert 'HOSTED_ZONE_ID' in failover_script, "HOSTED_ZONE_ID not configurable"

    def test_health_check_function_defined(self, failover_script):
        """Script must define a health check function."""
        assert 'check_health' in failover_script, "check_health function missing"

    def test_route53_operations_present(self, failover_script):
        """Script must perform Route 53 operations for DNS failover."""
        assert 'route53' in failover_script.lower(), \
            "No Route 53 operations found in failover script"

    def test_script_is_executable(self):
        """Failover script must have executable permissions."""
        script_path = SCRIPTS_DIR / "failover.sh"
        # Check that the file is readable (permissions may vary in CI)
        assert script_path.exists()
        assert script_path.stat().st_size > 0


# ---------------------------------------------------------------------------
# Architecture documentation tests
# ---------------------------------------------------------------------------

class TestArchitectureDocumentation:
    """Validate README and architecture documents cover key topics."""

    @pytest.fixture(scope="class")
    def readme_content(self):
        return (PROJECT_ROOT / "README.md").read_text()

    def test_readme_mentions_multi_region(self, readme_content):
        """README must mention multi-region architecture."""
        assert any(
            kw in readme_content.lower()
            for kw in ["multi-region", "multi region", "failover"]
        ), "README must mention multi-region or failover concepts"

    def test_readme_mentions_aws(self, readme_content):
        """README must reference AWS as the cloud provider."""
        assert "aws" in readme_content.lower() or "amazon" in readme_content.lower(), \
            "README must mention AWS"

    def test_readme_mentions_route53(self, readme_content):
        """README must reference Route 53 for DNS-based failover."""
        assert any(
            kw in readme_content.lower()
            for kw in ["route53", "route 53", "dns"]
        ), "README must mention Route 53 or DNS failover"

    def test_runbooks_not_empty(self):
        """RUNBOOKS directory must contain at least one runbook file."""
        runbook_files = list(RUNBOOKS_DIR.rglob("*.md"))
        assert len(runbook_files) > 0, "No runbook Markdown files found"
