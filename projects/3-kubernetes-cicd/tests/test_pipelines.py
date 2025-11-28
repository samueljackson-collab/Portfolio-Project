from pathlib import Path

import yaml


def test_github_actions_pipeline_parses():
    workflow = yaml.safe_load(Path("projects/3-kubernetes-cicd/pipelines/github-actions.yaml").read_text())
    assert workflow["name"].lower().startswith("kubernetes")
    assert "jobs" in workflow


def test_argocd_manifest_targets_app():
    manifest = yaml.safe_load(Path("projects/3-kubernetes-cicd/pipelines/argocd-app.yaml").read_text())
    assert manifest["kind"] == "Application"
    assert manifest["spec"]["destination"]["namespace"]
