"""
Test suite for 3-kubernetes-cicd
"""

import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def test_basic():
    """Basic test to ensure test framework is working."""
    assert True


def test_project_structure():
    """Test that project structure contains required files."""
    required_files = ["README.md", "Dockerfile", "requirements.txt"]
    for filename in required_files:
        assert (PROJECT_ROOT / filename).exists(), f"Missing required file: {filename}"


def test_kubernetes_manifests_exist():
    """Test that Kubernetes manifests directory exists and contains files."""
    k8s_dir = PROJECT_ROOT / "k8s"
    assert k8s_dir.exists(), "Missing k8s directory"
    yaml_files = list(k8s_dir.glob("**/*.yaml")) + list(k8s_dir.glob("**/*.yml"))
    assert len(yaml_files) > 0, "No Kubernetes manifest files found"


def test_argocd_config_exists():
    """Test that ArgoCD configuration exists."""
    argocd_dir = PROJECT_ROOT / "argocd"
    assert argocd_dir.exists(), "Missing argocd directory"


def test_monitoring_config_exists():
    """Test that monitoring configurations exist."""
    assert (PROJECT_ROOT / "prometheus").exists(), "Missing prometheus directory"
    assert (PROJECT_ROOT / "grafana").exists(), "Missing grafana directory"


def test_documentation_exists():
    """Test that documentation is complete."""
    assert (PROJECT_ROOT / "RUNBOOK.md").exists(), "Missing RUNBOOK.md"
    assert (PROJECT_ROOT / "docs").exists(), "Missing docs directory"
