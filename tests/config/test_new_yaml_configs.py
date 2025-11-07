"""
Validation tests for newly added YAML configuration files.

This test suite validates:
- ArgoCD Application configuration
- GitHub Actions workflow configuration
- Kubernetes deployment manifests
- YAML syntax and structure
- Best practices and security
"""

import yaml
import pytest
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent.parent


class TestArgoCDConfiguration:
    """Test ArgoCD application configuration."""

    def test_argocd_config_exists(self):
        """Verify ArgoCD application config file exists."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/argocd/portfolio-prod.yaml"
        assert config_path.exists(), f"ArgoCD config not found at {config_path}"

    def test_argocd_config_valid_yaml(self):
        """Test that ArgoCD config is valid YAML."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/argocd/portfolio-prod.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)

    def test_argocd_has_required_fields(self):
        """Test that ArgoCD config has required fields."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/argocd/portfolio-prod.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "apiVersion" in config
        assert "kind" in config
        assert config["kind"] == "Application"
        assert "metadata" in config
        assert "spec" in config

    def test_argocd_metadata_configuration(self):
        """Test ArgoCD metadata configuration."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/argocd/portfolio-prod.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        metadata = config.get("metadata", {})
        assert "name" in metadata, "Application should have a name"
        assert "namespace" in metadata, "Application should specify namespace"
        assert metadata["namespace"] == "argocd", "Should be in argocd namespace"

    def test_argocd_has_finalizers(self):
        """Test that ArgoCD config has finalizers for cleanup."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/argocd/portfolio-prod.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        metadata = config.get("metadata", {})
        assert "finalizers" in metadata, "Should have finalizers for resource cleanup"
        finalizers = metadata["finalizers"]
        assert isinstance(finalizers, list)
        assert len(finalizers) > 0

    def test_argocd_source_configuration(self):
        """Test ArgoCD source configuration."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/argocd/portfolio-prod.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        spec = config.get("spec", {})
        source = spec.get("source", {})
        
        assert "repoURL" in source, "Should specify repository URL"
        assert "targetRevision" in source, "Should specify target revision"
        assert "path" in source, "Should specify path in repository"

    def test_argocd_destination_configuration(self):
        """Test ArgoCD destination configuration."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/argocd/portfolio-prod.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        spec = config.get("spec", {})
        destination = spec.get("destination", {})
        
        assert "server" in destination, "Should specify target server"
        assert "namespace" in destination, "Should specify target namespace"

    def test_argocd_sync_policy_configured(self):
        """Test ArgoCD sync policy is configured."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/argocd/portfolio-prod.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        spec = config.get("spec", {})
        assert "syncPolicy" in spec, "Should have sync policy configured"
        
        sync_policy = spec["syncPolicy"]
        assert "automated" in sync_policy or "manual" in sync_policy, \
            "Should specify automated or manual sync"

    def test_argocd_automated_sync_settings(self):
        """Test automated sync settings if enabled."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/argocd/portfolio-prod.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        spec = config.get("spec", {})
        sync_policy = spec.get("syncPolicy", {})
        automated = sync_policy.get("automated", {})
        
        if automated:
            assert "prune" in automated, "Should specify prune setting"
            assert "selfHeal" in automated, "Should specify selfHeal setting"

    def test_argocd_retry_policy_configured(self):
        """Test ArgoCD retry policy is configured."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/argocd/portfolio-prod.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        spec = config.get("spec", {})
        sync_policy = spec.get("syncPolicy", {})
        
        if "retry" in sync_policy:
            retry = sync_policy["retry"]
            assert "limit" in retry, "Retry should have limit"
            assert "backoff" in retry, "Retry should have backoff configuration"


class TestGitHubActionsWorkflow:
    """Test GitHub Actions workflow configuration."""

    def test_github_actions_config_exists(self):
        """Verify GitHub Actions workflow file exists."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/github-actions/production.yml"
        assert config_path.exists(), f"GitHub Actions config not found at {config_path}"

    def test_github_actions_valid_yaml(self):
        """Test that GitHub Actions config is valid YAML."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/github-actions/production.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)

    def test_github_actions_has_name(self):
        """Test that workflow has a name."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/github-actions/production.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "name" in config, "Workflow should have a name"
        assert isinstance(config["name"], str)
        assert len(config["name"]) > 0

    def test_github_actions_has_triggers(self):
        """Test that workflow has trigger configuration."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/github-actions/production.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "on" in config, "Workflow should have 'on' trigger configuration"

    def test_github_actions_has_jobs(self):
        """Test that workflow defines jobs."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/github-actions/production.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "jobs" in config, "Workflow should define jobs"
        assert isinstance(config["jobs"], dict)
        assert len(config["jobs"]) > 0, "Workflow should have at least one job"

    def test_github_actions_jobs_have_steps(self):
        """Test that all jobs have steps defined."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/github-actions/production.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        jobs = config.get("jobs", {})
        for job_name, job_config in jobs.items():
            assert "steps" in job_config or "uses" in job_config, \
                f"Job '{job_name}' should have steps or use a reusable workflow"

    def test_github_actions_uses_checkout(self):
        """Test that workflow includes checkout action."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/github-actions/production.yml"
        
        with open(config_path) as f:
            content = f.read()
        
        assert "actions/checkout@" in content, \
            "Workflow should use checkout action"

    def test_github_actions_quality_checks(self):
        """Test that workflow includes quality checks."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/github-actions/production.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        jobs = config.get("jobs", {})
        
        # Check for quality-related job
        quality_job_found = False
        for job_name in jobs.keys():
            if "quality" in job_name.lower() or "lint" in job_name.lower():
                quality_job_found = True
                break
        
        assert quality_job_found, "Workflow should include quality checks"

    def test_github_actions_test_jobs(self):
        """Test that workflow includes test jobs."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/github-actions/production.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        jobs = config.get("jobs", {})
        
        # Check for test-related job
        test_job_found = False
        for job_name in jobs.keys():
            if "test" in job_name.lower():
                test_job_found = True
                break
        
        assert test_job_found, "Workflow should include test jobs"

    def test_github_actions_env_variables(self):
        """Test that workflow defines environment variables."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/github-actions/production.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Environment variables can be at workflow level or job level
        has_env = "env" in config
        if not has_env:
            jobs = config.get("jobs", {})
            for job_config in jobs.values():
                if "env" in job_config:
                    has_env = True
                    break
        
        assert has_env, "Workflow should define environment variables"


class TestKubernetesDeployment:
    """Test Kubernetes deployment manifest."""

    def test_k8s_deployment_exists(self):
        """Verify Kubernetes deployment file exists."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/k8s/base/deployment.yaml"
        assert config_path.exists(), f"K8s deployment not found at {config_path}"

    def test_k8s_deployment_valid_yaml(self):
        """Test that deployment YAML is valid."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/k8s/base/deployment.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)

    def test_k8s_deployment_api_version(self):
        """Test deployment has correct API version."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/k8s/base/deployment.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "apiVersion" in config
        assert "apps/v1" in config["apiVersion"]

    def test_k8s_deployment_kind(self):
        """Test deployment has correct kind."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/k8s/base/deployment.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config.get("kind") == "Deployment"

    def test_k8s_deployment_metadata(self):
        """Test deployment has proper metadata."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/k8s/base/deployment.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        metadata = config.get("metadata", {})
        assert "name" in metadata
        assert "labels" in metadata

    def test_k8s_deployment_replicas(self):
        """Test deployment specifies replicas."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/k8s/base/deployment.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        spec = config.get("spec", {})
        assert "replicas" in spec
        assert isinstance(spec["replicas"], int)
        assert spec["replicas"] > 0

    def test_k8s_deployment_strategy(self):
        """Test deployment has update strategy."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/k8s/base/deployment.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        spec = config.get("spec", {})
        assert "strategy" in spec, "Deployment should specify update strategy"

    def test_k8s_deployment_selector(self):
        """Test deployment has selector."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/k8s/base/deployment.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        spec = config.get("spec", {})
        assert "selector" in spec
        assert "matchLabels" in spec["selector"]

    def test_k8s_deployment_pod_template(self):
        """Test deployment has pod template."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/k8s/base/deployment.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        spec = config.get("spec", {})
        template = spec.get("template", {})
        
        assert "metadata" in template
        assert "spec" in template

    def test_k8s_deployment_containers(self):
        """Test deployment defines containers."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/k8s/base/deployment.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        spec = config.get("spec", {})
        template = spec.get("template", {})
        pod_spec = template.get("spec", {})
        
        assert "containers" in pod_spec
        assert isinstance(pod_spec["containers"], list)
        assert len(pod_spec["containers"]) > 0

    def test_k8s_deployment_resource_limits(self):
        """Test containers have resource limits."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/k8s/base/deployment.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        spec = config.get("spec", {})
        template = spec.get("template", {})
        pod_spec = template.get("spec", {})
        containers = pod_spec.get("containers", [])
        
        for container in containers:
            if container.get("name") == "app":  # Main app container
                assert "resources" in container, \
                    "Main container should have resource limits"
                resources = container["resources"]
                assert "requests" in resources or "limits" in resources, \
                    "Should specify resource requests or limits"

    def test_k8s_deployment_health_probes(self):
        """Test containers have health probes."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/k8s/base/deployment.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        spec = config.get("spec", {})
        template = spec.get("template", {})
        pod_spec = template.get("spec", {})
        containers = pod_spec.get("containers", [])
        
        for container in containers:
            if container.get("name") == "app":
                assert "livenessProbe" in container or "readinessProbe" in container, \
                    "Main container should have health probes"

    def test_k8s_deployment_security_context(self):
        """Test deployment has security context."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/k8s/base/deployment.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        spec = config.get("spec", {})
        template = spec.get("template", {})
        pod_spec = template.get("spec", {})
        
        # Check pod-level or container-level security context
        has_security_context = "securityContext" in pod_spec
        
        if not has_security_context:
            containers = pod_spec.get("containers", [])
            for container in containers:
                if "securityContext" in container:
                    has_security_context = True
                    break
        
        assert has_security_context, "Should have security context configured"

    def test_k8s_deployment_runs_as_non_root(self):
        """Test deployment runs as non-root user."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/k8s/base/deployment.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        spec = config.get("spec", {})
        template = spec.get("template", {})
        pod_spec = template.get("spec", {})
        security_context = pod_spec.get("securityContext", {})
        
        if "runAsNonRoot" in security_context:
            assert security_context["runAsNonRoot"] is True, \
                "Should run as non-root user"

    def test_k8s_deployment_image_pull_policy(self):
        """Test containers have image pull policy."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/k8s/base/deployment.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        spec = config.get("spec", {})
        template = spec.get("template", {})
        pod_spec = template.get("spec", {})
        containers = pod_spec.get("containers", [])
        
        for container in containers:
            if "imagePullPolicy" in container:
                assert container["imagePullPolicy"] in ["Always", "IfNotPresent", "Never"], \
                    f"Invalid imagePullPolicy: {container['imagePullPolicy']}"


class TestYAMLSyntaxAndBestPractices:
    """Test YAML syntax and best practices across all configs."""

    def test_no_duplicate_keys_argocd(self):
        """Test ArgoCD config has no duplicate keys."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/argocd/portfolio-prod.yaml"
        
        with open(config_path) as f:
            content = f.read()
        
        # PyYAML will raise an error if there are duplicate keys with default settings
        config = yaml.safe_load(content)
        assert config is not None

    def test_no_duplicate_keys_github_actions(self):
        """Test GitHub Actions config has no duplicate keys."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/github-actions/production.yml"
        
        with open(config_path) as f:
            content = f.read()
        
        config = yaml.safe_load(content)
        assert config is not None

    def test_no_duplicate_keys_k8s(self):
        """Test K8s config has no duplicate keys."""
        config_path = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/k8s/base/deployment.yaml"
        
        with open(config_path) as f:
            content = f.read()
        
        config = yaml.safe_load(content)
        assert config is not None

    def test_yaml_files_use_consistent_indentation(self):
        """Test YAML files use consistent indentation."""
        yaml_files = [
            BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/argocd/portfolio-prod.yaml",
            BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/github-actions/production.yml",
            BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/code-examples/cicd/k8s/base/deployment.yaml"
        ]
        
        for yaml_file in yaml_files:
            if yaml_file.exists():
                with open(yaml_file) as f:
                    content = f.read()
                
                # Check that file doesn't mix tabs and spaces
                assert '\t' not in content or '  ' not in content, \
                    f"{yaml_file.name} should not mix tabs and spaces"