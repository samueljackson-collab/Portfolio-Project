"""Tests for advanced Kubernetes operator utilities."""

from importlib import util
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "projects"
    / "19-advanced-kubernetes-operators"
    / "advanced-operators.py"
)


def load_module() -> ModuleType:
    spec = util.spec_from_file_location("advanced_operators", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {MODULE_PATH}")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cluster_scoped_status_uses_status_endpoint():
    module = load_module()
    api = MagicMock()
    status_payload = {"phase": "Ready"}

    module.update_resource_status(
        api,
        group="example.com",
        version="v1",
        plural="widgets",
        name="demo",
        status=status_payload,
        namespaced=False,
    )

    api.patch_cluster_custom_object_status.assert_called_once_with(
        group="example.com",
        version="v1",
        plural="widgets",
        name="demo",
        body={"status": status_payload},
    )
