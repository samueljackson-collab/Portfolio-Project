"""Tests for the advanced Kubernetes operator helpers."""

from __future__ import annotations

import importlib.util
import logging
import unittest
from pathlib import Path


def _load_module():
    module_path = (
        Path(__file__).resolve().parents[1]
        / "projects"
        / "19-advanced-kubernetes-operators"
        / "advanced-operators.py"
    )
    spec = importlib.util.spec_from_file_location("advanced_operators", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class DummyCustomObjectsApi:
    """A tiny stub that records calls made to the CustomObjectsApi."""

    def __init__(self):
        self.calls = []

    def patch_cluster_custom_object_status(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return {"patched": True}


class AdvancedOperatorTests(unittest.TestCase):
    """Behavioural tests for :class:`AdvancedOperator`."""

    def setUp(self) -> None:
        module = _load_module()
        self.operator = module.AdvancedOperator(DummyCustomObjectsApi())

    def test_cluster_status_updates_use_status_endpoint(self) -> None:
        with self.assertLogs(level=logging.INFO) as captured:
            result = self.operator.update_resource_status(
                group="example.com",
                version="v1alpha1",
                plural="widgets",
                name="global-widget",
                status={"healthy": True},
            )

        self.assertEqual(result, {"patched": True})
        self.assertEqual(
            self.operator.custom_api.calls,
            [
                (
                    (),
                    {
                        "group": "example.com",
                        "version": "v1alpha1",
                        "plural": "widgets",
                        "name": "global-widget",
                        "body": {"status": {"healthy": True}},
                    },
                )
            ],
        )
        self.assertTrue(
            any(
                "Cluster-level status for widgets/global-widget patched successfully"
                in message
                for message in captured.output
            )
        )


if __name__ == "__main__":
    unittest.main()
