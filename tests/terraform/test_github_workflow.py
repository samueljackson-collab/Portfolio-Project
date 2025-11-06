"""
Comprehensive tests for GitHub Actions Terraform workflow.

This test suite validates:
- YAML syntax correctness
- Workflow structure
- Job definitions
- Terraform steps
- Security checks (TFLint, Checkov)
- OIDC configuration
- Environment variables
- Artifact handling
"""

import yaml
from pathlib import Path
import pytest


@pytest.fixture
def workflow_path():
    """Return path to Terraform workflow."""
    return Path(".github/workflows/terraform.yml")


@pytest.fixture
def workflow(workflow_path):
    """Load and parse workflow YAML."""
    with open(workflow_path) as f:
        return yaml.safe_load(f)


class TestWorkflowFile:
    """Test workflow file existence and syntax."""

    def test_workflow_file_exists(self, workflow_path):
        """Verify workflow file exists."""
        assert workflow_path.exists()

    def test_workflow_valid_yaml(self, workflow_path):
        """Verify workflow is valid YAML."""
        try:
            with open(workflow_path) as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML: {e}")


class TestWorkflowStructure:
    """Test basic workflow structure."""

    def test_workflow_has_name(self, workflow):
        """Verify workflow has a name."""
        assert "name" in workflow
        assert "Terraform" in workflow["name"]

    def test_workflow_has_on_triggers(self, workflow):
        """Verify workflow has trigger events."""
        assert "on" in workflow
        assert workflow["on"] is not None

    def test_workflow_on_key_uses_quoted_syntax(self, workflow_path):
        """Verify workflow uses quoted 'on' key to avoid YAML reserved word issues."""
        content = workflow_path.read_text()
        # The 'on' key should be quoted as 'on': to avoid YAML 1.1 compatibility issues
        # where 'on' could be interpreted as boolean true
        assert "'on':" in content, "Workflow should use quoted 'on': key for YAML compatibility"

    def test_workflow_on_key_parseable(self, workflow):
        """Verify the 'on' key is properly parsed by YAML parser."""
        # If YAML loads successfully and 'on' key exists, the syntax is correct
        assert "on" in workflow
        assert isinstance(workflow["on"], dict), "'on' should parse as a dictionary"
        assert len(workflow["on"]) > 0, "'on' should contain trigger definitions"

    def test_workflow_on_key_not_boolean(self, workflow):
        """Verify 'on' key is not interpreted as a boolean."""
        # In YAML 1.1, unquoted 'on' could be interpreted as boolean true
        # This test ensures it's properly parsed as a dictionary key
        assert workflow["on"] is not True
        assert workflow["on"] is not False
        assert isinstance(workflow["on"], dict)

    def test_workflow_triggers_on_push(self, workflow):
        """Verify workflow triggers on push to main."""
        assert "push" in workflow["on"]
        if isinstance(workflow["on"]["push"], dict):
            assert "branches" in workflow["on"]["push"]

    def test_workflow_yaml_version_compatibility(self, workflow_path):
        """Verify workflow YAML is compatible with both YAML 1.1 and 1.2."""
        import yaml
        content = workflow_path.read_text()
        
        # Test with safe_load (default parser)
        parsed = yaml.safe_load(content)
        assert parsed is not None
        assert "name" in parsed
        
        # Verify 'on' is properly quoted to avoid 1.1/1.2 incompatibilities
        assert "'on':" in content

    def test_workflow_no_yaml_boolean_traps(self, workflow_path):
        """Verify workflow avoids YAML boolean interpretation traps."""
        content = workflow_path.read_text()
        # In YAML 1.1, unquoted on/off/yes/no can be booleans
        # Ensure critical keys are properly quoted or not in ambiguous positions
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Check if 'on:' appears unquoted at start of line (would be a trap)
            stripped = line.lstrip()
            if stripped.startswith('on:') and not stripped.startswith("'on':"):
                pytest.fail(f"Line {i+1}: Unquoted 'on:' key could be misinterpreted as boolean")

    def test_workflow_triggers_on_pull_request(self, workflow):
        """Verify workflow triggers on pull requests."""
        assert "pull_request" in workflow["on"]

    def test_workflow_has_path_filters(self, workflow):
        """Verify workflow has path filters for terraform files."""
        on_config = workflow["on"]
        has_path_filter = False
        
        if "push" in on_config and isinstance(on_config["push"], dict):
            has_path_filter = "paths" in on_config["push"]
        
        assert has_path_filter, "Workflow should filter on terraform path changes"

    def test_workflow_has_jobs(self, workflow):
        """Verify workflow defines jobs."""
        assert "jobs" in workflow
        assert len(workflow["jobs"]) > 0


class TestEnvironmentVariables:
    """Test workflow environment variables."""

    def test_workflow_has_env_section(self, workflow):
        """Verify workflow defines environment variables."""
        assert "env" in workflow

    def test_workflow_has_terraform_version(self, workflow):
        """Verify workflow specifies Terraform version."""
        assert "env" in workflow
        assert "TF_VERSION" in workflow["env"]

    def test_workflow_has_aws_region(self, workflow):
        """Verify workflow specifies AWS region."""
        assert "env" in workflow
        env = workflow["env"]
        assert "AWS_REGION" in env or any("region" in k.lower() for k in env.keys())

    def test_workflow_has_tfstate_bucket(self, workflow):
        """Verify workflow references tfstate bucket."""
        assert "env" in workflow
        assert "TFSTATE_BUCKET" in workflow["env"]


class TestPermissions:
    """Test workflow permissions."""

    def test_workflow_has_permissions(self, workflow):
        """Verify workflow specifies permissions."""
        assert "permissions" in workflow

    def test_workflow_has_id_token_write(self, workflow):
        """Verify workflow can write id-token for OIDC."""
        perms = workflow.get("permissions", {})
        assert "id-token" in perms
        assert perms["id-token"] == "write"

    def test_workflow_has_contents_read(self, workflow):
        """Verify workflow can read repository contents."""
        perms = workflow.get("permissions", {})
        assert "contents" in perms
        assert perms["contents"] == "read"

    def test_workflow_has_pr_write(self, workflow):
        """Verify workflow can write to pull requests."""
        perms = workflow.get("permissions", {})
        assert "pull-requests" in perms
        assert perms["pull-requests"] == "write"


class TestTerraformPlanJob:
    """Test terraform-plan job."""

    def test_has_terraform_plan_job(self, workflow):
        """Verify workflow has terraform-plan job."""
        assert "terraform-plan" in workflow["jobs"]

    def test_plan_job_runs_on_ubuntu(self, workflow):
        """Verify plan job runs on Ubuntu."""
        job = workflow["jobs"]["terraform-plan"]
        assert "runs-on" in job
        assert "ubuntu" in job["runs-on"]

    def test_plan_job_has_working_directory(self, workflow):
        """Verify plan job sets working directory."""
        job = workflow["jobs"]["terraform-plan"]
        if "defaults" in job:
            assert "working-directory" in job["defaults"]["run"]

    def test_plan_job_checks_out_code(self, workflow):
        """Verify plan job checks out repository."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        checkout_steps = [s for s in steps if "checkout" in s.get("uses", "").lower()]
        assert len(checkout_steps) > 0

    def test_plan_job_configures_aws_credentials(self, workflow):
        """Verify plan job configures AWS credentials."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        aws_steps = [s for s in steps if "aws" in s.get("name", "").lower()]
        assert len(aws_steps) > 0

    def test_plan_job_sets_up_terraform(self, workflow):
        """Verify plan job sets up Terraform."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        tf_steps = [s for s in steps if "setup-terraform" in s.get("uses", "").lower()]
        assert len(tf_steps) > 0

    def test_plan_job_runs_terraform_fmt(self, workflow):
        """Verify plan job runs terraform fmt."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        fmt_steps = [s for s in steps if "fmt" in s.get("name", "").lower() or "format" in s.get("name", "").lower()]
        assert len(fmt_steps) > 0

    def test_plan_job_runs_terraform_init(self, workflow):
        """Verify plan job runs terraform init."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        init_steps = [s for s in steps if "init" in s.get("name", "").lower()]
        assert len(init_steps) > 0

    def test_plan_job_runs_terraform_validate(self, workflow):
        """Verify plan job runs terraform validate."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        validate_steps = [s for s in steps if "validate" in s.get("name", "").lower()]
        assert len(validate_steps) > 0

    def test_plan_job_runs_terraform_plan(self, workflow):
        """Verify plan job runs terraform plan."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        plan_steps = [s for s in steps if "plan" in s.get("name", "").lower() and "terraform plan" in str(s.get("run", "")).lower()]
        assert len(plan_steps) > 0


class TestSecurityChecks:
    """Test security scanning steps."""

    def test_plan_job_runs_tflint(self, workflow):
        """Verify plan job runs TFLint."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        tflint_steps = [s for s in steps if "tflint" in s.get("name", "").lower()]
        assert len(tflint_steps) > 0

    def test_plan_job_runs_checkov(self, workflow):
        """Verify plan job runs Checkov."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        checkov_steps = [s for s in steps if "checkov" in s.get("name", "").lower()]
        assert len(checkov_steps) > 0


class TestPullRequestComment:
    """Test PR comment functionality."""

    def test_plan_job_comments_on_pr(self, workflow):
        """Verify plan job comments plan results on PR."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        comment_steps = [s for s in steps if "comment" in s.get("name", "").lower()]
        assert len(comment_steps) > 0

    def test_pr_comment_uses_github_script(self, workflow):
        """Verify PR comment uses github-script action."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        script_steps = [s for s in steps if "github-script" in s.get("uses", "")]
        assert len(script_steps) > 0

    def test_pr_comment_conditional_on_pr_event(self, workflow):
        """Verify PR comment only runs on pull request events."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        for step in steps:
            if "comment" in step.get("name", "").lower() and "pr" in step.get("name", "").lower():
                assert "if" in step
                assert "pull_request" in step["if"]


class TestTerraformApplyJob:
    """Test terraform-apply job."""

    def test_has_terraform_apply_job(self, workflow):
        """Verify workflow has terraform-apply job."""
        assert "terraform-apply" in workflow["jobs"]

    def test_apply_job_needs_plan(self, workflow):
        """Verify apply job depends on plan job."""
        job = workflow["jobs"]["terraform-apply"]
        assert "needs" in job
        assert "terraform-plan" in job["needs"]

    def test_apply_job_only_runs_on_main(self, workflow):
        """Verify apply job only runs on main branch."""
        job = workflow["jobs"]["terraform-apply"]
        assert "if" in job
        assert "main" in job["if"]

    def test_apply_job_requires_environment(self, workflow):
        """Verify apply job uses environment for protection."""
        job = workflow["jobs"]["terraform-apply"]
        assert "environment" in job

    def test_apply_job_downloads_plan_artifact(self, workflow):
        """Verify apply job downloads plan artifact."""
        job = workflow["jobs"]["terraform-apply"]
        steps = job.get("steps", [])
        download_steps = [s for s in steps if "download" in s.get("name", "").lower() and "artifact" in s.get("name", "").lower()]
        assert len(download_steps) > 0

    def test_apply_job_runs_terraform_apply(self, workflow):
        """Verify apply job runs terraform apply."""
        job = workflow["jobs"]["terraform-apply"]
        steps = job.get("steps", [])
        apply_steps = [s for s in steps if "apply" in s.get("name", "").lower() and "terraform apply" in str(s.get("run", "")).lower()]
        assert len(apply_steps) > 0


class TestArtifacts:
    """Test artifact handling."""

    def test_plan_job_uploads_plan_artifact(self, workflow):
        """Verify plan job uploads plan as artifact."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        upload_steps = [s for s in steps if "upload" in s.get("name", "").lower() and "artifact" in s.get("name", "").lower()]
        assert len(upload_steps) > 0


class TestOIDCConfiguration:
    """Test OIDC configuration."""

    def test_workflow_documents_oidc_setup(self, workflow_path):
        """Verify workflow includes OIDC setup documentation."""
        content = workflow_path.read_text()
        assert "OIDC" in content

    def test_workflow_has_oidc_authentication_steps(self, workflow_path):
        """Verify workflow has commented OIDC auth steps."""
        content = workflow_path.read_text()
        # Should have commented or active OIDC configuration
        assert "role-to-assume" in content or "OIDC" in content


class TestWorkflowDispatch:
    """Test manual workflow dispatch."""

    def test_workflow_supports_manual_dispatch(self, workflow):
        """Verify workflow can be manually triggered."""
        assert "workflow_dispatch" in workflow["on"]


class TestBackendWorkflowIntegration:
    """Test integration between backend.tf and GitHub workflow."""

    def test_workflow_provides_backend_config_values(self, workflow):
        """Verify workflow provides all backend configuration values."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        
        # Find the terraform init step
        init_steps = [s for s in steps if "init" in s.get("name", "").lower()]
        assert len(init_steps) > 0, "Workflow should have terraform init step"
        
        # Check that init step uses backend-config
        init_step = init_steps[0]
        run_command = init_step.get("run", "")
        assert "-backend-config" in run_command, "Init should use -backend-config flags"

    def test_backend_config_values_match_env_vars(self, workflow):
        """Verify backend-config references match environment variables."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        
        init_steps = [s for s in steps if "init" in s.get("name", "").lower()]
        if init_steps:
            run_command = init_steps[0].get("run", "")
            # Should reference TFSTATE_BUCKET and AWS_REGION
            assert "TFSTATE_BUCKET" in run_command or "tfstate_bucket" in run_command.lower()
            assert "AWS_REGION" in run_command or "region" in run_command.lower()

    def test_backend_placeholder_values_not_in_workflow(self, workflow, workflow_path):
        """Verify workflow doesn't use REPLACE_ME placeholder values."""
        content = workflow_path.read_text()
        assert "REPLACE_ME" not in content, \
            "Workflow should use environment variables, not placeholder values"

    def test_workflow_init_provides_bucket_config(self, workflow):
        """Verify workflow init step provides bucket configuration."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        
        init_steps = [s for s in steps if "init" in s.get("name", "").lower()]
        assert len(init_steps) > 0
        
        run_command = init_steps[0].get("run", "")
        assert 'backend-config="bucket=' in run_command or \
               "backend-config='bucket=" in run_command, \
               "Init should configure backend bucket"

    def test_workflow_init_provides_region_config(self, workflow):
        """Verify workflow init step provides region configuration."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        
        init_steps = [s for s in steps if "init" in s.get("name", "").lower()]
        assert len(init_steps) > 0
        
        run_command = init_steps[0].get("run", "")
        assert 'backend-config="region=' in run_command or \
               "backend-config='region=" in run_command, \
               "Init should configure backend region"