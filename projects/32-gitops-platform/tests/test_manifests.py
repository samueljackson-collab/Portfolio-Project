"""
Tests for GitOps Platform YAML manifests and configuration files.
Validates that all YAML files are well-formed and contain required fields.

Run with: pytest tests/test_manifests.py -v
"""

import os
import yaml
import pytest
import glob

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def project_path(*parts: str) -> str:
    """Return an absolute path relative to the project root."""
    return os.path.join(PROJECT_ROOT, *parts)


def load_yaml(path: str):
    """Load and return a YAML file, raising on parse errors."""
    with open(path, "r") as fh:
        return yaml.safe_load(fh)


def collect_yaml_files(directory: str) -> list:
    """Return all .yaml and .yml files under directory, recursively."""
    pattern_yaml = os.path.join(directory, "**", "*.yaml")
    pattern_yml = os.path.join(directory, "**", "*.yml")
    files = glob.glob(pattern_yaml, recursive=True) + glob.glob(pattern_yml, recursive=True)
    return sorted(files)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def argocd_app_of_apps():
    path = project_path("argocd", "app-of-apps.yaml")
    return load_yaml(path)


@pytest.fixture(scope="session")
def frontend_app():
    path = project_path("argocd", "apps", "frontend-app.yaml")
    return load_yaml(path)


@pytest.fixture(scope="session")
def backend_app():
    path = project_path("argocd", "apps", "backend-app.yaml")
    return load_yaml(path)


@pytest.fixture(scope="session")
def monitoring_app():
    path = project_path("argocd", "apps", "monitoring-app.yaml")
    return load_yaml(path)


@pytest.fixture(scope="session")
def dev_values():
    path = project_path("environments", "dev", "values.yaml")
    return load_yaml(path)


@pytest.fixture(scope="session")
def staging_values():
    path = project_path("environments", "staging", "values.yaml")
    return load_yaml(path)


@pytest.fixture(scope="session")
def prod_values():
    path = project_path("environments", "prod", "values.yaml")
    return load_yaml(path)


# ---------------------------------------------------------------------------
# Test: all YAML files parse without errors
# ---------------------------------------------------------------------------

class TestYamlWellFormed:
    """All YAML files in the project must parse without errors."""

    def test_argocd_directory_yamls_parse(self):
        argocd_dir = project_path("argocd")
        yaml_files = collect_yaml_files(argocd_dir)
        assert len(yaml_files) > 0, "No YAML files found in argocd/"
        for path in yaml_files:
            with open(path, "r") as fh:
                data = yaml.safe_load(fh)
            assert data is not None, f"Empty or null YAML: {path}"

    def test_environments_directory_yamls_parse(self):
        envs_dir = project_path("environments")
        yaml_files = collect_yaml_files(envs_dir)
        assert len(yaml_files) >= 3, "Expected at least 3 values.yaml files (dev/staging/prod)"
        for path in yaml_files:
            with open(path, "r") as fh:
                data = yaml.safe_load(fh)
            assert data is not None, f"Empty or null YAML: {path}"

    def test_all_yaml_files_are_dicts(self):
        all_dirs = [project_path("argocd"), project_path("environments")]
        for d in all_dirs:
            for path in collect_yaml_files(d):
                data = load_yaml(path)
                assert isinstance(data, dict), (
                    f"Expected dict at top level in {path}, got {type(data).__name__}"
                )


# ---------------------------------------------------------------------------
# Test: app-of-apps manifest
# ---------------------------------------------------------------------------

class TestAppOfApps:
    """app-of-apps.yaml must be a valid ArgoCD Application with correct spec."""

    def test_api_version(self, argocd_app_of_apps):
        assert argocd_app_of_apps["apiVersion"] == "argoproj.io/v1alpha1"

    def test_kind(self, argocd_app_of_apps):
        assert argocd_app_of_apps["kind"] == "Application"

    def test_metadata_name(self, argocd_app_of_apps):
        assert argocd_app_of_apps["metadata"]["name"] == "app-of-apps"

    def test_metadata_namespace(self, argocd_app_of_apps):
        assert argocd_app_of_apps["metadata"]["namespace"] == "argocd"

    def test_has_finalizers(self, argocd_app_of_apps):
        finalizers = argocd_app_of_apps["metadata"].get("finalizers", [])
        assert "resources-finalizer.argocd.argoproj.io" in finalizers

    def test_spec_project(self, argocd_app_of_apps):
        assert argocd_app_of_apps["spec"]["project"] == "default"

    def test_spec_source_repo_url(self, argocd_app_of_apps):
        repo = argocd_app_of_apps["spec"]["source"]["repoURL"]
        assert repo.startswith("https://github.com/"), f"Unexpected repoURL: {repo}"

    def test_spec_source_path(self, argocd_app_of_apps):
        path = argocd_app_of_apps["spec"]["source"]["path"]
        assert "argocd/apps" in path, f"Expected apps path, got: {path}"

    def test_spec_destination_server(self, argocd_app_of_apps):
        server = argocd_app_of_apps["spec"]["destination"]["server"]
        assert server == "https://kubernetes.default.svc"

    def test_spec_sync_policy_automated(self, argocd_app_of_apps):
        sync = argocd_app_of_apps["spec"]["syncPolicy"]
        assert "automated" in sync
        assert sync["automated"]["prune"] is True
        assert sync["automated"]["selfHeal"] is True

    def test_spec_sync_options(self, argocd_app_of_apps):
        sync_options = argocd_app_of_apps["spec"]["syncPolicy"].get("syncOptions", [])
        assert "CreateNamespace=true" in sync_options


# ---------------------------------------------------------------------------
# Test: individual ArgoCD Application manifests
# ---------------------------------------------------------------------------

REQUIRED_APP_FIELDS = [
    ("apiVersion", "argoproj.io/v1alpha1"),
    ("kind", "Application"),
]


def assert_valid_argocd_app(data: dict, expected_namespace: str = None):
    """Shared assertions for any ArgoCD Application manifest."""
    for field, expected in REQUIRED_APP_FIELDS:
        assert data.get(field) == expected, (
            f"Expected {field}={expected!r}, got {data.get(field)!r}"
        )
    spec = data["spec"]
    assert "project" in spec
    assert "source" in spec
    assert "repoURL" in spec["source"]
    assert "destination" in spec
    assert "server" in spec["destination"]
    if expected_namespace:
        assert spec["destination"]["namespace"] == expected_namespace


class TestFrontendApp:
    def test_is_valid_argocd_application(self, frontend_app):
        assert_valid_argocd_app(frontend_app, expected_namespace="frontend")

    def test_name_is_frontend(self, frontend_app):
        assert frontend_app["metadata"]["name"] == "frontend"

    def test_has_automated_sync(self, frontend_app):
        assert "automated" in frontend_app["spec"]["syncPolicy"]

    def test_has_finalizer(self, frontend_app):
        finalizers = frontend_app["metadata"].get("finalizers", [])
        assert "resources-finalizer.argocd.argoproj.io" in finalizers

    def test_source_has_helm(self, frontend_app):
        source = frontend_app["spec"]["source"]
        assert "helm" in source, "frontend-app.yaml should have helm source configuration"


class TestBackendApp:
    def test_is_valid_argocd_application(self, backend_app):
        assert_valid_argocd_app(backend_app, expected_namespace="backend")

    def test_name_is_backend(self, backend_app):
        assert backend_app["metadata"]["name"] == "backend"

    def test_has_automated_sync(self, backend_app):
        assert "automated" in backend_app["spec"]["syncPolicy"]

    def test_has_finalizer(self, backend_app):
        finalizers = backend_app["metadata"].get("finalizers", [])
        assert "resources-finalizer.argocd.argoproj.io" in finalizers

    def test_source_has_helm(self, backend_app):
        source = backend_app["spec"]["source"]
        assert "helm" in source, "backend-app.yaml should have helm source configuration"


class TestMonitoringApp:
    def test_is_valid_argocd_application(self, monitoring_app):
        assert_valid_argocd_app(monitoring_app, expected_namespace="monitoring")

    def test_name_is_monitoring(self, monitoring_app):
        assert monitoring_app["metadata"]["name"] == "monitoring"

    def test_has_automated_sync(self, monitoring_app):
        assert "automated" in monitoring_app["spec"]["syncPolicy"]

    def test_has_finalizer(self, monitoring_app):
        finalizers = monitoring_app["metadata"].get("finalizers", [])
        assert "resources-finalizer.argocd.argoproj.io" in finalizers

    def test_uses_prometheus_chart(self, monitoring_app):
        source = monitoring_app["spec"]["source"]
        # Monitoring app uses a Helm chart directly, not a path
        assert "chart" in source or "path" in source


# ---------------------------------------------------------------------------
# Test: environment values files
# ---------------------------------------------------------------------------

class TestDevValues:
    def test_replica_count_is_one(self, dev_values):
        assert dev_values["replicaCount"] == 1

    def test_autoscaling_disabled(self, dev_values):
        assert dev_values["autoscaling"]["enabled"] is False

    def test_has_image_config(self, dev_values):
        assert "image" in dev_values
        assert "repository" in dev_values["image"]
        assert "tag" in dev_values["image"]

    def test_has_resources(self, dev_values):
        assert "resources" in dev_values
        assert "requests" in dev_values["resources"]
        assert "limits" in dev_values["resources"]

    def test_environment_is_dev(self, dev_values):
        assert dev_values["global"]["environment"] == "dev"

    def test_pdb_disabled(self, dev_values):
        assert dev_values["podDisruptionBudget"]["enabled"] is False


class TestStagingValues:
    def test_replica_count_is_two(self, staging_values):
        assert staging_values["replicaCount"] == 2

    def test_autoscaling_enabled(self, staging_values):
        assert staging_values["autoscaling"]["enabled"] is True

    def test_has_image_config(self, staging_values):
        assert "image" in staging_values
        assert "repository" in staging_values["image"]
        assert "tag" in staging_values["image"]

    def test_has_resources(self, staging_values):
        assert "resources" in staging_values

    def test_environment_is_staging(self, staging_values):
        assert staging_values["global"]["environment"] == "staging"

    def test_pdb_enabled(self, staging_values):
        assert staging_values["podDisruptionBudget"]["enabled"] is True

    def test_ingress_enabled(self, staging_values):
        assert staging_values["ingress"]["enabled"] is True


class TestProdValues:
    def test_replica_count_is_three(self, prod_values):
        assert prod_values["replicaCount"] == 3

    def test_autoscaling_enabled(self, prod_values):
        assert prod_values["autoscaling"]["enabled"] is True

    def test_autoscaling_min_replicas(self, prod_values):
        assert prod_values["autoscaling"]["minReplicas"] >= 3

    def test_autoscaling_max_replicas(self, prod_values):
        assert prod_values["autoscaling"]["maxReplicas"] >= 5

    def test_pdb_enabled(self, prod_values):
        assert prod_values["podDisruptionBudget"]["enabled"] is True

    def test_pdb_min_available(self, prod_values):
        assert prod_values["podDisruptionBudget"]["minAvailable"] >= 2

    def test_has_image_config(self, prod_values):
        assert "image" in prod_values
        assert "repository" in prod_values["image"]
        assert "tag" in prod_values["image"]

    def test_environment_is_prod(self, prod_values):
        assert prod_values["global"]["environment"] == "prod"

    def test_ingress_enabled(self, prod_values):
        assert prod_values["ingress"]["enabled"] is True

    def test_ingress_tls_configured(self, prod_values):
        assert len(prod_values["ingress"]["tls"]) > 0

    def test_network_policy_enabled(self, prod_values):
        assert prod_values["networkPolicy"]["enabled"] is True

    def test_stricter_resources_than_dev(self, prod_values, dev_values):
        """Production should have higher CPU/memory limits than dev."""
        dev_cpu_limit = dev_values["resources"]["limits"]["cpu"]
        prod_cpu_limit = prod_values["resources"]["limits"]["cpu"]
        # Compare numerically: strip 'm' suffix
        dev_cpu_m = int(dev_cpu_limit.rstrip("m"))
        prod_cpu_m = int(prod_cpu_limit.rstrip("m"))
        assert prod_cpu_m > dev_cpu_m, (
            f"Prod CPU limit ({prod_cpu_limit}) should exceed dev ({dev_cpu_limit})"
        )


# ---------------------------------------------------------------------------
# Test: required files exist
# ---------------------------------------------------------------------------

class TestRequiredFilesExist:
    """All required project files must exist on disk."""

    REQUIRED_FILES = [
        "terraform/main.tf",
        "terraform/variables.tf",
        "terraform/outputs.tf",
        "argocd/app-of-apps.yaml",
        "argocd/apps/frontend-app.yaml",
        "argocd/apps/backend-app.yaml",
        "argocd/apps/monitoring-app.yaml",
        "environments/dev/values.yaml",
        "environments/staging/values.yaml",
        "environments/prod/values.yaml",
        "scripts/bootstrap.sh",
        "scripts/promote.sh",
        "demo_output/argocd_app_list.txt",
        "demo_output/terraform_apply.txt",
    ]

    @pytest.mark.parametrize("relative_path", REQUIRED_FILES)
    def test_file_exists(self, relative_path):
        full_path = project_path(relative_path)
        assert os.path.isfile(full_path), f"Required file missing: {full_path}"

    def test_scripts_are_executable(self):
        for script in ["scripts/bootstrap.sh", "scripts/promote.sh"]:
            path = project_path(script)
            assert os.access(path, os.X_OK), f"Script not executable: {path}"

    def test_terraform_main_has_required_resources(self):
        main_tf = project_path("terraform", "main.tf")
        with open(main_tf, "r") as fh:
            content = fh.read()
        assert "kind_cluster" in content
        assert "helm_release" in content
        assert "argocd" in content

    def test_argocd_apps_count(self):
        apps_dir = project_path("argocd", "apps")
        yaml_files = collect_yaml_files(apps_dir)
        assert len(yaml_files) >= 3, (
            f"Expected at least 3 app manifests in argocd/apps/, found {len(yaml_files)}"
        )
