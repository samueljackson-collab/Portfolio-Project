"""Test Kubernetes manifests."""
import pytest
import yaml
from pathlib import Path

def test_deployment_manifest_exists():
    """Test deployment manifest exists."""
    manifest = Path(__file__).parent.parent / "manifests" / "deployment.yaml"
    assert manifest.exists()

def test_deployment_manifest_valid():
    """Test deployment manifest is valid YAML."""
    manifest = Path(__file__).parent.parent / "manifests" / "deployment.yaml"
    with open(manifest) as f:
        data = yaml.safe_load(f)
    assert data['kind'] == 'Deployment'
    assert 'spec' in data

def test_service_manifest_exists():
    """Test service manifest exists."""
    manifest = Path(__file__).parent.parent / "manifests" / "service.yaml"
    assert manifest.exists()

def test_replicas_count():
    """Test deployment has appropriate replica count."""
    manifest = Path(__file__).parent.parent / "manifests" / "deployment.yaml"
    with open(manifest) as f:
        data = yaml.safe_load(f)
    replicas = data['spec']['replicas']
    assert replicas >= 1
    assert replicas <= 10
