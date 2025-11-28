from pathlib import Path

import yaml


def test_workflow_defines_security_steps():
    workflow = yaml.safe_load(Path("projects/4-devsecops/pipelines/github-actions.yaml").read_text())
    jobs = workflow.get("jobs", {})
    assert any("scan" in job_name.lower() or "security" in job_name.lower() for job_name in jobs)
