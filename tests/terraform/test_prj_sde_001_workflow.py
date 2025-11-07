"""
Comprehensive tests for PRJ-SDE-001 Terraform CI/CD GitHub Actions workflow.

This test suite validates:
- YAML syntax correctness
- Workflow structure and triggers
- Job definitions and dependencies
- Terraform automation steps
- Security scanning (tfsec)
- Cost estimation (Infracost)
- PR commenting
- Environment protection
- Artifact handling
"""

import yaml
from pathlib import Path
import pytest


BASE_PATH = Path(__file__).parent.parent.parent
WORKFLOW_PATH = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/.github/workflows/terraform-ci.yml"


@pytest.fixture
def workflow_path():
    """Return path to Terraform CI/CD workflow."""
    return WORKFLOW_PATH


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
        assert workflow_path.is_file()

    def test_workflow_valid_yaml(self, workflow_path):
        """Verify workflow is valid YAML."""
        try:
            with open(workflow_path) as f:
                content = yaml.safe_load(f)
            assert content is not None
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

    def test_workflow_triggers_on_push(self, workflow):
        """Verify workflow triggers on push to main and develop."""
        assert "push" in workflow["on"]
        push_config = workflow["on"]["push"]
        assert "branches" in push_config
        assert "main" in push_config["branches"]
        assert "develop" in push_config["branches"]

    def test_workflow_triggers_on_pull_request(self, workflow):
        """Verify workflow triggers on pull requests."""
        assert "pull_request" in workflow["on"]
        pr_config = workflow["on"]["pull_request"]
        assert "branches" in pr_config

    def test_workflow_has_path_filters(self, workflow):
        """Verify workflow filters on infrastructure path changes."""
        push_config = workflow["on"]["push"]
        assert "paths" in push_config
        paths = push_config["paths"]
        assert any("infrastructure" in p for p in paths)

    def test_workflow_supports_manual_dispatch(self, workflow):
        """Verify workflow supports manual triggering."""
        assert "workflow_dispatch" in workflow["on"]

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
        env = workflow["env"]
        assert "TF_VERSION" in env
        # Should specify 1.6.0 or compatible
        assert "1.6" in env["TF_VERSION"]

    def test_workflow_has_aws_region(self, workflow):
        """Verify workflow specifies AWS region."""
        env = workflow["env"]
        assert "AWS_REGION" in env
        assert env["AWS_REGION"] == "us-east-1"

    def test_workflow_has_working_directory(self, workflow):
        """Verify workflow specifies working directory."""
        env = workflow["env"]
        assert "WORKING_DIR" in env
        assert "infrastructure" in env["WORKING_DIR"]


class TestValidateJob:
    """Test terraform-validate job."""

    def test_has_validate_job(self, workflow):
        """Verify workflow has terraform-validate job."""
        assert "terraform-validate" in workflow["jobs"]

    def test_validate_job_name(self, workflow):
        """Verify validate job has descriptive name."""
        job = workflow["jobs"]["terraform-validate"]
        assert "name" in job
        assert "Validate" in job["name"]

    def test_validate_job_runs_on_ubuntu(self, workflow):
        """Verify validate job runs on Ubuntu."""
        job = workflow["jobs"]["terraform-validate"]
        assert "runs-on" in job
        assert "ubuntu" in job["runs-on"]

    def test_validate_job_checks_out_code(self, workflow):
        """Verify validate job checks out repository."""
        job = workflow["jobs"]["terraform-validate"]
        steps = job.get("steps", [])
        checkout_steps = [s for s in steps if "checkout" in s.get("uses", "").lower()]
        assert len(checkout_steps) > 0

    def test_validate_job_sets_up_terraform(self, workflow):
        """Verify validate job sets up Terraform."""
        job = workflow["jobs"]["terraform-validate"]
        steps = job.get("steps", [])
        tf_steps = [s for s in steps if "setup-terraform" in s.get("uses", "").lower()]
        assert len(tf_steps) > 0
        # Verify version is set
        tf_step = tf_steps[0]
        assert "with" in tf_step
        assert "terraform_version" in tf_step["with"]

    def test_validate_job_runs_terraform_fmt(self, workflow):
        """Verify validate job runs terraform fmt."""
        job = workflow["jobs"]["terraform-validate"]
        steps = job.get("steps", [])
        fmt_steps = [s for s in steps if "fmt" in s.get("name", "").lower() or "format" in s.get("name", "").lower()]
        assert len(fmt_steps) > 0
        # Verify fmt check is recursive
        fmt_step = fmt_steps[0]
        assert "run" in fmt_step
        assert "fmt" in fmt_step["run"]

    def test_validate_job_fmt_continues_on_error(self, workflow):
        """Verify fmt step continues on error (for reporting)."""
        job = workflow["jobs"]["terraform-validate"]
        steps = job.get("steps", [])
        fmt_steps = [s for s in steps if "fmt" in s.get("name", "").lower()]
        if fmt_steps:
            assert "continue-on-error" in fmt_steps[0]
            assert fmt_steps[0]["continue-on-error"] == True

    def test_validate_job_runs_terraform_init(self, workflow):
        """Verify validate job runs terraform init."""
        job = workflow["jobs"]["terraform-validate"]
        steps = job.get("steps", [])
        init_steps = [s for s in steps if "init" in s.get("name", "").lower() and "validation" in s.get("name", "").lower()]
        assert len(init_steps) > 0
        # Verify init uses -backend=false for validation
        init_step = init_steps[0]
        assert "backend=false" in init_step["run"]

    def test_validate_job_runs_terraform_validate(self, workflow):
        """Verify validate job runs terraform validate."""
        job = workflow["jobs"]["terraform-validate"]
        steps = job.get("steps", [])
        validate_steps = [s for s in steps if "validate" in s.get("name", "").lower() and s.get("id") == "validate"]
        assert len(validate_steps) > 0

    def test_validate_job_comments_on_pr(self, workflow):
        """Verify validate job comments results on PR."""
        job = workflow["jobs"]["terraform-validate"]
        steps = job.get("steps", [])
        comment_steps = [s for s in steps if "comment" in s.get("name", "").lower() and "pr" in s.get("name", "").lower()]
        assert len(comment_steps) > 0
        # Verify it only runs on PRs
        comment_step = comment_steps[0]
        assert "if" in comment_step
        assert "pull_request" in comment_step["if"]

    def test_validate_job_uses_github_script(self, workflow):
        """Verify PR comment uses github-script action."""
        job = workflow["jobs"]["terraform-validate"]
        steps = job.get("steps", [])
        script_steps = [s for s in steps if "github-script" in s.get("uses", "")]
        assert len(script_steps) > 0


class TestSecurityScanJob:
    """Test terraform-security-scan job."""

    def test_has_security_scan_job(self, workflow):
        """Verify workflow has security scan job."""
        assert "terraform-security-scan" in workflow["jobs"]

    def test_security_scan_needs_validate(self, workflow):
        """Verify security scan depends on validate job."""
        job = workflow["jobs"]["terraform-security-scan"]
        assert "needs" in job
        assert "terraform-validate" in job["needs"]

    def test_security_scan_runs_tfsec(self, workflow):
        """Verify security scan runs tfsec."""
        job = workflow["jobs"]["terraform-security-scan"]
        steps = job.get("steps", [])
        tfsec_steps = [s for s in steps if "tfsec" in s.get("uses", "").lower()]
        assert len(tfsec_steps) > 0

    def test_tfsec_uses_working_directory(self, workflow):
        """Verify tfsec scans correct directory."""
        job = workflow["jobs"]["terraform-security-scan"]
        steps = job.get("steps", [])
        tfsec_steps = [s for s in steps if "tfsec" in s.get("uses", "").lower()]
        if tfsec_steps:
            tfsec_step = tfsec_steps[0]
            assert "with" in tfsec_step
            assert "working_directory" in tfsec_step["with"]

    def test_tfsec_soft_fail(self, workflow):
        """Verify tfsec doesn't fail build but reports issues."""
        job = workflow["jobs"]["terraform-security-scan"]
        steps = job.get("steps", [])
        tfsec_steps = [s for s in steps if "tfsec" in s.get("uses", "").lower()]
        if tfsec_steps:
            tfsec_step = tfsec_steps[0]
            assert "with" in tfsec_step
            # Should have soft_fail enabled
            assert "soft_fail" in tfsec_step["with"]


class TestPlanJob:
    """Test terraform-plan job."""

    def test_has_plan_job(self, workflow):
        """Verify workflow has terraform-plan job."""
        assert "terraform-plan" in workflow["jobs"]

    def test_plan_job_needs_validate_and_scan(self, workflow):
        """Verify plan job depends on validate and security scan."""
        job = workflow["jobs"]["terraform-plan"]
        assert "needs" in job
        needs = job["needs"]
        assert "terraform-validate" in needs
        assert "terraform-security-scan" in needs

    def test_plan_job_only_runs_on_pr(self, workflow):
        """Verify plan job only runs on pull requests."""
        job = workflow["jobs"]["terraform-plan"]
        assert "if" in job
        assert "pull_request" in job["if"]

    def test_plan_job_has_pr_write_permission(self, workflow):
        """Verify plan job can write to pull requests."""
        job = workflow["jobs"]["terraform-plan"]
        if "permissions" in job:
            assert "pull-requests" in job["permissions"]
            assert job["permissions"]["pull-requests"] == "write"

    def test_plan_job_configures_aws_credentials(self, workflow):
        """Verify plan job configures AWS credentials."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        aws_steps = [s for s in steps if "aws" in s.get("name", "").lower() and "credentials" in s.get("name", "").lower()]
        assert len(aws_steps) > 0
        # Verify it uses secrets
        aws_step = aws_steps[0]
        assert "with" in aws_step
        assert any("secrets" in str(v).lower() for v in aws_step["with"].values())

    def test_plan_job_runs_terraform_init(self, workflow):
        """Verify plan job runs terraform init."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        init_steps = [s for s in steps if "init" in s.get("name", "").lower() and s.get("id") != "init"]
        # Should have init step (not the validation one)
        assert len(init_steps) > 0

    def test_plan_job_runs_terraform_plan(self, workflow):
        """Verify plan job runs terraform plan."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        plan_steps = [s for s in steps if s.get("id") == "plan"]
        assert len(plan_steps) > 0
        plan_step = plan_steps[0]
        assert "run" in plan_step
        assert "terraform plan" in plan_step["run"]

    def test_plan_uses_db_password_secret(self, workflow):
        """Verify plan step uses DB_PASSWORD secret."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        plan_steps = [s for s in steps if s.get("id") == "plan"]
        if plan_steps:
            plan_step = plan_steps[0]
            if "env" in plan_step:
                assert "TF_VAR_db_password" in plan_step["env"]

    def test_plan_continues_on_error(self, workflow):
        """Verify plan continues on error for reporting."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        plan_steps = [s for s in steps if s.get("id") == "plan"]
        if plan_steps:
            assert "continue-on-error" in plan_steps[0]

    def test_plan_job_comments_on_pr(self, workflow):
        """Verify plan job comments plan on PR."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        comment_steps = [s for s in steps if "comment" in s.get("name", "").lower() and "plan" in s.get("name", "").lower()]
        assert len(comment_steps) > 0

    def test_plan_job_uploads_artifact(self, workflow):
        """Verify plan job uploads plan as artifact."""
        job = workflow["jobs"]["terraform-plan"]
        steps = job.get("steps", [])
        upload_steps = [s for s in steps if "upload" in s.get("name", "").lower() and "artifact" in s.get("name", "").lower()]
        assert len(upload_steps) > 0
        upload_step = upload_steps[0]
        assert "with" in upload_step
        assert "name" in upload_step["with"]
        assert "path" in upload_step["with"]


class TestApplyJob:
    """Test terraform-apply job."""

    def test_has_apply_job(self, workflow):
        """Verify workflow has terraform-apply job."""
        assert "terraform-apply" in workflow["jobs"]

    def test_apply_job_needs_validate(self, workflow):
        """Verify apply job depends on validate job."""
        job = workflow["jobs"]["terraform-apply"]
        assert "needs" in job
        assert "terraform-validate" in job["needs"]

    def test_apply_job_only_runs_on_main(self, workflow):
        """Verify apply job only runs on main branch."""
        job = workflow["jobs"]["terraform-apply"]
        assert "if" in job
        job_if = job["if"]
        assert "push" in job_if
        assert "main" in job_if

    def test_apply_job_requires_environment(self, workflow):
        """Verify apply job uses environment for protection."""
        job = workflow["jobs"]["terraform-apply"]
        assert "environment" in job
        assert job["environment"]["name"] == "production"

    def test_apply_job_configures_aws_credentials(self, workflow):
        """Verify apply job configures AWS credentials."""
        job = workflow["jobs"]["terraform-apply"]
        steps = job.get("steps", [])
        aws_steps = [s for s in steps if "aws" in s.get("name", "").lower() and "credentials" in s.get("name", "").lower()]
        assert len(aws_steps) > 0

    def test_apply_job_runs_terraform_init(self, workflow):
        """Verify apply job runs terraform init."""
        job = workflow["jobs"]["terraform-apply"]
        steps = job.get("steps", [])
        init_steps = [s for s in steps if "init" in s.get("name", "").lower()]
        assert len(init_steps) > 0

    def test_apply_job_runs_terraform_plan(self, workflow):
        """Verify apply job runs plan before apply."""
        job = workflow["jobs"]["terraform-apply"]
        steps = job.get("steps", [])
        plan_steps = [s for s in steps if s.get("id") == "plan"]
        assert len(plan_steps) > 0

    def test_apply_job_runs_terraform_apply(self, workflow):
        """Verify apply job runs terraform apply."""
        job = workflow["jobs"]["terraform-apply"]
        steps = job.get("steps", [])
        apply_steps = [s for s in steps if s.get("id") == "apply"]
        assert len(apply_steps) > 0
        apply_step = apply_steps[0]
        assert "run" in apply_step
        assert "terraform apply" in apply_step["run"]
        # Verify auto-approve
        assert "auto-approve" in apply_step["run"]

    def test_apply_uses_db_password_secret(self, workflow):
        """Verify apply steps use DB_PASSWORD secret."""
        job = workflow["jobs"]["terraform-apply"]
        steps = job.get("steps", [])
        plan_steps = [s for s in steps if s.get("id") == "plan"]
        apply_steps = [s for s in steps if s.get("id") == "apply"]
        
        # Both plan and apply should have the secret
        for step in plan_steps + apply_steps:
            if "env" in step:
                assert "TF_VAR_db_password" in step["env"]

    def test_apply_job_outputs_database_endpoint(self, workflow):
        """Verify apply job outputs database endpoint."""
        job = workflow["jobs"]["terraform-apply"]
        steps = job.get("steps", [])
        output_steps = [s for s in steps if "output" in s.get("name", "").lower() and "endpoint" in s.get("name", "").lower()]
        assert len(output_steps) > 0

    def test_apply_job_creates_deployment_summary(self, workflow):
        """Verify apply job creates deployment summary."""
        job = workflow["jobs"]["terraform-apply"]
        steps = job.get("steps", [])
        summary_steps = [s for s in steps if "summary" in s.get("name", "").lower()]
        assert len(summary_steps) > 0
        summary_step = summary_steps[0]
        assert "run" in summary_step
        assert "GITHUB_STEP_SUMMARY" in summary_step["run"]


class TestCostEstimationJob:
    """Test cost-estimation job."""

    def test_has_cost_estimation_job(self, workflow):
        """Verify workflow has cost estimation job."""
        assert "cost-estimation" in workflow["jobs"]

    def test_cost_job_needs_validate(self, workflow):
        """Verify cost job depends on validate."""
        job = workflow["jobs"]["cost-estimation"]
        assert "needs" in job
        assert "terraform-validate" in job["needs"]

    def test_cost_job_only_runs_on_pr(self, workflow):
        """Verify cost job only runs on pull requests."""
        job = workflow["jobs"]["cost-estimation"]
        assert "if" in job
        assert "pull_request" in job["if"]

    def test_cost_job_sets_up_infracost(self, workflow):
        """Verify cost job sets up Infracost."""
        job = workflow["jobs"]["cost-estimation"]
        steps = job.get("steps", [])
        infracost_steps = [s for s in steps if "infracost" in s.get("uses", "").lower() and "setup" in s.get("uses", "").lower()]
        assert len(infracost_steps) > 0
        infracost_step = infracost_steps[0]
        assert "with" in infracost_step
        assert "api-key" in infracost_step["with"]

    def test_cost_job_generates_breakdown(self, workflow):
        """Verify cost job generates Infracost breakdown."""
        job = workflow["jobs"]["cost-estimation"]
        steps = job.get("steps", [])
        breakdown_steps = [s for s in steps if "breakdown" in s.get("name", "").lower()]
        assert len(breakdown_steps) > 0
        breakdown_step = breakdown_steps[0]
        assert "run" in breakdown_step
        assert "infracost breakdown" in breakdown_step["run"]

    def test_cost_job_posts_comment(self, workflow):
        """Verify cost job posts comment to PR."""
        job = workflow["jobs"]["cost-estimation"]
        steps = job.get("steps", [])
        comment_steps = [s for s in steps if "comment" in s.get("uses", "").lower() and "infracost" in s.get("uses", "").lower()]
        assert len(comment_steps) > 0


class TestWorkflowSecurity:
    """Test workflow security practices."""

    def test_secrets_not_hardcoded(self, workflow_path):
        """Verify no secrets are hardcoded in workflow."""
        content = workflow_path.read_text()
        # Should use secrets. prefix, not actual values
        assert "secrets.AWS_ACCESS_KEY_ID" in content
        assert "secrets.AWS_SECRET_ACCESS_KEY" in content
        assert "secrets.DB_PASSWORD" in content
        # Should not contain actual secret values (basic check)
        suspicious_patterns = ["AKIA", "aws_secret_access_key", "password="]
        for pattern in suspicious_patterns:
            # Allow references to secrets but not values
            if pattern in content.lower() and "secrets." not in content.lower():
                pytest.fail(f"Potentially hardcoded secret pattern: {pattern}")

    def test_uses_environment_protection(self, workflow):
        """Verify apply job uses environment protection."""
        apply_job = workflow["jobs"]["terraform-apply"]
        assert "environment" in apply_job
        assert apply_job["environment"]["name"] == "production"

    def test_terraform_version_pinned(self, workflow):
        """Verify Terraform version is pinned."""
        env = workflow["env"]
        assert "TF_VERSION" in env
        # Should be specific version, not latest
        assert env["TF_VERSION"] != "latest"


class TestWorkflowPaths:
    """Test workflow path configurations."""

    def test_workflow_filters_correct_paths(self, workflow):
        """Verify workflow filters on correct infrastructure paths."""
        push_config = workflow["on"]["push"]
        pr_config = workflow["on"]["pull_request"]
        
        for config in [push_config, pr_config]:
            assert "paths" in config
            paths = config["paths"]
            # Should filter on project infrastructure
            assert any("PRJ-SDE-001/infrastructure" in p for p in paths)

    def test_working_directory_is_correct(self, workflow):
        """Verify WORKING_DIR points to correct location."""
        env = workflow["env"]
        assert "WORKING_DIR" in env
        working_dir = env["WORKING_DIR"]
        assert "projects/01-sde-devops/PRJ-SDE-001/infrastructure" in working_dir


class TestWorkflowCompleteness:
    """Test workflow completeness and best practices."""

    def test_all_jobs_have_names(self, workflow):
        """Verify all jobs have descriptive names."""
        jobs = workflow["jobs"]
        for job_id, job_config in jobs.items():
            assert "name" in job_config, f"Job {job_id} should have a name"

    def test_all_jobs_specify_runner(self, workflow):
        """Verify all jobs specify runner."""
        jobs = workflow["jobs"]
        for job_id, job_config in jobs.items():
            assert "runs-on" in job_config, f"Job {job_id} should specify runs-on"

    def test_critical_steps_have_ids(self, workflow):
        """Verify critical steps have IDs for referencing."""
        jobs = workflow["jobs"]
        critical_step_names = ["fmt", "init", "validate", "plan", "apply"]
        
        for job_id, job_config in jobs.items():
            steps = job_config.get("steps", [])
            for step in steps:
                step_name = step.get("name", "").lower()
                if any(critical in step_name for critical in critical_step_names):
                    # Critical steps should have IDs
                    if "terraform" in step_name:
                        assert "id" in step, f"Critical step '{step.get('name')}' in job '{job_id}' should have an ID"

    def test_workflow_uses_recent_action_versions(self, workflow):
        """Verify workflow uses recent action versions."""
        jobs = workflow["jobs"]
        for job_id, job_config in jobs.items():
            steps = job_config.get("steps", [])
            for step in steps:
                if "uses" in step:
                    uses = step["uses"]
                    # Check checkout action version
                    if "checkout" in uses:
                        assert "v4" in uses or "v3" in uses
                    # Check setup-terraform version
                    if "setup-terraform" in uses:
                        assert "v3" in uses or "v2" in uses


class TestJobDependencies:
    """Test job dependencies and workflow."""

    def test_validate_has_no_dependencies(self, workflow):
        """Verify validate job has no dependencies (runs first)."""
        job = workflow["jobs"]["terraform-validate"]
        assert "needs" not in job or len(job.get("needs", [])) == 0

    def test_security_scan_depends_on_validate(self, workflow):
        """Verify security scan depends on validate."""
        job = workflow["jobs"]["terraform-security-scan"]
        assert "needs" in job
        assert "terraform-validate" in job["needs"]

    def test_plan_depends_on_validate_and_scan(self, workflow):
        """Verify plan depends on both validate and scan."""
        job = workflow["jobs"]["terraform-plan"]
        assert "needs" in job
        needs = job["needs"] if isinstance(job["needs"], list) else [job["needs"]]
        assert "terraform-validate" in needs
        assert "terraform-security-scan" in needs

    def test_apply_depends_on_validate(self, workflow):
        """Verify apply depends on validate."""
        job = workflow["jobs"]["terraform-apply"]
        assert "needs" in job
        assert "terraform-validate" in job["needs"]

    def test_cost_depends_on_validate(self, workflow):
        """Verify cost estimation depends on validate."""
        job = workflow["jobs"]["cost-estimation"]
        assert "needs" in job
        assert "terraform-validate" in job["needs"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])