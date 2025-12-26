"""Integration checks to ensure CI workflow aligns with factory stages."""
from pathlib import Path

import yaml


WORKFLOW_PATH = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yml"


def test_workflow_jobs_exist():
    with open(WORKFLOW_PATH) as handle:
        workflow = yaml.safe_load(handle)

    jobs = workflow.get("jobs", {})
    for job in ["lint-test", "terraform-plan", "cloudformation-changeset", "apply"]:
        assert job in jobs, f"Expected workflow job {job}"


def test_workflow_references_factory_steps():
    with open(WORKFLOW_PATH) as handle:
        workflow = yaml.safe_load(handle)

    lint_steps = workflow["jobs"]["lint-test"]["steps"]
    assert any("lint" in step.get("name", "").lower() for step in lint_steps)
    assert any("test" in step.get("name", "").lower() for step in lint_steps)

    plan_steps = workflow["jobs"]["terraform-plan"]["steps"]
    assert any("terraform" in step.get("name", "").lower() for step in plan_steps)

    change_steps = workflow["jobs"]["cloudformation-changeset"]["steps"]
    assert any("change" in step.get("name", "").lower() for step in change_steps)


def test_apply_job_is_gated():
    with open(WORKFLOW_PATH) as handle:
        workflow = yaml.safe_load(handle)

    apply_job = workflow["jobs"]["apply"]
    assert apply_job.get("environment", {}).get("name") == "production"
    assert "needs" in apply_job and "cloudformation-changeset" in apply_job["needs"]
