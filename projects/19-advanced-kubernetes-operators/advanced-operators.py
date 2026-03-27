"""Utilities for managing advanced Kubernetes operators."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def update_resource_status(
    custom_objects_api: Any,
    *,
    group: str,
    version: str,
    plural: str,
    name: str,
    status: Dict[str, Any],
    namespace: Optional[str] = None,
    namespaced: bool = True,
) -> Dict[str, Any]:
    """Patch the status block for a custom resource.

    Parameters
    ----------
    custom_objects_api:
        Instance of ``kubernetes.client.CustomObjectsApi`` (or a compatible
        object in tests).
    group, version, plural, name:
        Identify the custom resource definition and instance to update.
    status:
        The desired ``status`` payload for the resource.
    namespace:
        Namespace containing the resource.  Ignored for cluster-scoped
        resources.
    namespaced:
        ``True`` if the resource is namespace-scoped, otherwise cluster-scoped.
    """

    patch_body = {"status": status}

    if namespaced:
        logger.debug(
            "Patching namespaced custom resource status",
            extra={
                "k8s_group": group,
                "k8s_version": version,
                "k8s_plural": plural,
                "k8s_name": name,
                "k8s_namespace": namespace,
            },
        )
        return custom_objects_api.patch_namespaced_custom_object_status(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            name=name,
            body=patch_body,
        )

    logger.debug(
        "Patching cluster-scoped custom resource status",
        extra={
            "k8s_group": group,
            "k8s_version": version,
            "k8s_plural": plural,
            "k8s_name": name,
        },
    )
    return custom_objects_api.patch_cluster_custom_object_status(
        group=group,
        version=version,
        plural=plural,
        name=name,
        body=patch_body,
    )
