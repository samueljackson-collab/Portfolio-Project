"""Utilities for advanced Kubernetes operator examples.

This module provides a small facade around the Kubernetes dynamic client
used in the portfolio project write-ups.  Only the behaviour that is
required by the tests in this kata is implemented here – it is not
intended to be a fully-fledged operator implementation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional


class AdvancedOperator:
    """Tiny helper that mirrors the snippets described in the article.

    Parameters
    ----------
    custom_api:
        Object exposing the Kubernetes CustomObjectsApi interface used for
        cluster-scoped resources.
    logger:
        Optional logger used to emit diagnostic messages.  When omitted the
        module level logger is used.
    """

    def __init__(self, custom_api: Any, logger: Optional[logging.Logger] = None) -> None:
        self.custom_api = custom_api
        self.logger = logger or logging.getLogger(__name__)

    def update_resource_status(
        self,
        group: str,
        version: str,
        plural: str,
        name: str,
        status: Dict[str, Any],
    ) -> Any:
        """Update the status subresource for a cluster-scoped custom object.

        The method mirrors the behaviour described in the accompanying blog
        post.  Previously it called :meth:`patch_cluster_custom_object`, which
        meant the status subresource was not updated at the cluster level.
        Kubernetes exposes a dedicated ``patch_cluster_custom_object_status``
        helper for this purpose – this method now routes the call through to it
        while keeping the body of the request unchanged.
        """

        body = {"status": status}
        response = self.custom_api.patch_cluster_custom_object_status(
            group=group,
            version=version,
            plural=plural,
            name=name,
            body=body,
        )

        self.logger.info(
            "Cluster-level status for %s/%s patched successfully: %s",
            plural,
            name,
            status,
        )

        return response


__all__ = ["AdvancedOperator"]
