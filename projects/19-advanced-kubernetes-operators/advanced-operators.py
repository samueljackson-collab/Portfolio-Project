"""Utilities for working with advanced Kubernetes operators.

This module includes helpers used by several project write-ups.  The
``AdvancedOperator`` class intentionally mirrors the interactions from the
original operator prototypes so that the documentation snippets stay
executable inside tests.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional


class AdvancedOperator:
    """Helper wrapper around the dynamic Kubernetes custom objects API."""

    def __init__(self, custom_api: Any, logger: Optional[logging.Logger] = None) -> None:
        self.custom_api = custom_api
        self.log = logger or logging.getLogger(__name__)

    def update_resource_status(
        self,
        group: str,
        version: str,
        plural: str,
        name: str,
        status: Dict[str, Any],
        namespace: Optional[str] = None,
    ) -> Any:
        """Patch the status subresource for a custom object.

        Args:
            group: API group of the custom resource definition.
            version: API version of the resource.
            plural: Plural name of the resource.
            name: Name of the custom resource instance.
            status: JSON merge patch describing the status document.
            namespace: When provided, indicates the resource is namespaced.

        Returns:
            Whatever the underlying Kubernetes client returns.
        """

        if namespace:
            self.log.debug(
                "Patching status for namespaced custom object %s/%s", namespace, name
            )
            return self.custom_api.patch_namespaced_custom_object_status(
                group=group,
                version=version,
                namespace=namespace,
                plural=plural,
                name=name,
                body=status,
            )

        self.log.debug(
            "Patching status for cluster-scoped custom object %s", name
        )
        response = self.custom_api.patch_cluster_custom_object_status(
            group=group,
            version=version,
            plural=plural,
            name=name,
            body=status,
        )
        self.log.info(
            "Successfully patched status for cluster-scoped CR %s.%s/%s",
            plural,
            version,
            name,
        )
        return response
