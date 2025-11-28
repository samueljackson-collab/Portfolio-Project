"""Portfolio project README validation tests.

These checks ensure that each project README references the concrete assets
that back the documented capabilities (CI workflows, IaC, manifests, tests,
and monitoring rules). The goal is to keep documentation and implementation
artifacts aligned as the portfolio evolves.
"""

from pathlib import Path

import pytest


BASE_DIR = Path(__file__).resolve().parents[2]


PROJECT_CASES = [
    {
        "name": "aws-infrastructure-automation",
        "readme": BASE_DIR / "projects/1-aws-infrastructure-automation/README.md",
        "references": [
            "terraform/main.tf",
            "pulumi/Pulumi.yaml",
            "cdk/app.py",
            ".github/workflows/ci.yml",
            "k8s/cluster-addons.yaml",
            "monitoring/eks-prometheus-rules.yaml",
            "tests/test_infrastructure.py",
        ],
        "files": [
            "terraform/main.tf",
            "pulumi/Pulumi.yaml",
            "cdk/app.py",
            ".github/workflows/ci.yml",
            "k8s/cluster-addons.yaml",
            "monitoring/eks-prometheus-rules.yaml",
            "tests/test_infrastructure.py",
        ],
    },
    {
        "name": "database-migration",
        "readme": BASE_DIR / "projects/2-database-migration/README.md",
        "references": [
            "config/debezium-postgres-connector.json",
            "src/migration_orchestrator.py",
            "Dockerfile",
            "k8s/connector-deployment.yaml",
            "monitoring/alerts.yml",
            "tests/test_migration_orchestrator.py",
            ".github/workflows/ci.yml",
        ],
        "files": [
            "config/debezium-postgres-connector.json",
            "src/migration_orchestrator.py",
            "Dockerfile",
            "k8s/connector-deployment.yaml",
            "monitoring/alerts.yml",
            "tests/test_migration_orchestrator.py",
            ".github/workflows/ci.yml",
        ],
    },
    {
        "name": "kubernetes-cicd",
        "readme": BASE_DIR / "projects/3-kubernetes-cicd/README.md",
        "references": [
            "pipelines/github-actions.yaml",
            "pipelines/argocd-app.yaml",
            "manifests/rollout.yaml",
            "monitoring/argo-alerts.yml",
            "tests/test_pipelines.py",
        ],
        "files": [
            "pipelines/github-actions.yaml",
            "pipelines/argocd-app.yaml",
            "manifests/rollout.yaml",
            "monitoring/argo-alerts.yml",
            "tests/test_pipelines.py",
        ],
    },
    {
        "name": "devsecops",
        "readme": BASE_DIR / "projects/4-devsecops/README.md",
        "references": [
            "pipelines/github-actions.yaml",
            "manifests/policy-engine.yaml",
            "monitoring/security-alerts.yml",
            "tests/test_pipeline_config.py",
        ],
        "files": [
            "pipelines/github-actions.yaml",
            "manifests/policy-engine.yaml",
            "monitoring/security-alerts.yml",
            "tests/test_pipeline_config.py",
        ],
    },
    {
        "name": "mlops-platform",
        "readme": BASE_DIR / "projects/6-mlops-platform/README.md",
        "references": [
            ".github/workflows/ci.yml",
            "docker/Dockerfile",
            "k8s/model-serving.yaml",
            "monitoring/monitoring-rules.yml",
            "tests/test_mlops_pipeline.py",
        ],
        "files": [
            ".github/workflows/ci.yml",
            "docker/Dockerfile",
            "k8s/model-serving.yaml",
            "monitoring/monitoring-rules.yml",
            "tests/test_mlops_pipeline.py",
        ],
    },
    {
        "name": "serverless-data-processing",
        "readme": BASE_DIR / "projects/7-serverless-data-processing/README.md",
        "references": [
            "infrastructure/template.yaml",
            ".github/workflows/ci.yml",
            "monitoring/alerts.yml",
            "tests/test_lambda_pipeline.py",
        ],
        "files": [
            "infrastructure/template.yaml",
            ".github/workflows/ci.yml",
            "monitoring/alerts.yml",
            "tests/test_lambda_pipeline.py",
        ],
    },
    {
        "name": "autonomous-devops-platform",
        "readme": BASE_DIR / "projects/22-autonomous-devops-platform/README.md",
        "references": [
            "src/autonomous_engine.py",
            ".github/workflows/ci.yml",
            "k8s/runbook-operator.yaml",
            "monitoring/alerts.yml",
            "tests/test_autonomous_engine.py",
        ],
        "files": [
            "src/autonomous_engine.py",
            ".github/workflows/ci.yml",
            "k8s/runbook-operator.yaml",
            "monitoring/alerts.yml",
            "tests/test_autonomous_engine.py",
        ],
    },
    {
        "name": "advanced-monitoring",
        "readme": BASE_DIR / "projects/23-advanced-monitoring/README.md",
        "references": [
            "dashboards/portfolio.json",
            "alerts/portfolio_rules.yml",
            "manifests/base/deployment.yaml",
            "manifests/overlays/production/kustomization.yaml",
            ".github/workflows/monitoring.yml",
            "tests/test_configs.py",
        ],
        "files": [
            "dashboards/portfolio.json",
            "alerts/portfolio_rules.yml",
            "manifests/base/deployment.yaml",
            "manifests/overlays/production/kustomization.yaml",
            ".github/workflows/monitoring.yml",
            "tests/test_configs.py",
        ],
    },
]


@pytest.mark.parametrize("case", PROJECT_CASES, ids=[case["name"] for case in PROJECT_CASES])
def test_readme_mentions_assets(case):
    """Ensure README files mention the implementation artifacts they rely on."""

    readme_path = case["readme"]
    assert readme_path.exists(), f"README not found for {case['name']}"

    content = readme_path.read_text()
    for reference in case["references"]:
        assert (
            reference in content
        ), f"Expected '{reference}' to be referenced in {readme_path}"


@pytest.mark.parametrize("case", PROJECT_CASES, ids=[case["name"] for case in PROJECT_CASES])
def test_referenced_assets_exist(case):
    """Validate that each referenced asset actually exists on disk."""

    project_root = case["readme"].parent
    for relative_path in case["files"]:
        asset_path = project_root / relative_path
        assert asset_path.exists(), f"Missing asset '{relative_path}' for {case['name']}"
