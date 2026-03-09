"""Kubernetes resource reconciliation logic for PortfolioStack operator."""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import kopf
import kubernetes
from kubernetes import client
from kubernetes.client.rest import ApiException

LOGGER = logging.getLogger(__name__)


class ReconcileAction(Enum):
    """Actions taken during reconciliation."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    NOOP = "noop"


@dataclass
class ReconcileResult:
    """Result of a reconciliation operation."""
    action: ReconcileAction
    resource_type: str
    resource_name: str
    success: bool
    message: str = ""
    error: Optional[str] = None


@dataclass
class PortfolioStackSpec:
    """Parsed specification for PortfolioStack."""
    image: str
    version: str
    replicas: int = 1
    port: int = 8080
    env: Dict[str, str] = field(default_factory=dict)
    resources: Dict[str, Dict[str, str]] = field(default_factory=dict)
    ingress_enabled: bool = False
    ingress_host: Optional[str] = None
    config_data: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, spec: Dict[str, Any]) -> "PortfolioStackSpec":
        return cls(
            image=spec.get("image", "nginx:latest"),
            version=spec.get("version", "latest"),
            replicas=spec.get("replicas", 1),
            port=spec.get("port", 8080),
            env=spec.get("env", {}),
            resources=spec.get("resources", {}),
            ingress_enabled=spec.get("ingress", {}).get("enabled", False),
            ingress_host=spec.get("ingress", {}).get("host"),
            config_data=spec.get("config", {}),
        )


class ResourceReconciler:
    """Handles reconciliation of Kubernetes resources for PortfolioStack."""

    def __init__(self):
        try:
            kubernetes.config.load_incluster_config()
        except kubernetes.config.ConfigException:
            kubernetes.config.load_kube_config()

        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
        self.networking_v1 = client.NetworkingV1Api()

    async def reconcile(
        self,
        name: str,
        namespace: str,
        spec: PortfolioStackSpec,
        owner_reference: Dict[str, Any],
    ) -> List[ReconcileResult]:
        """Reconcile all resources for a PortfolioStack."""
        results = []

        # Reconcile ConfigMap
        if spec.config_data:
            result = await self._reconcile_configmap(name, namespace, spec, owner_reference)
            results.append(result)

        # Reconcile Deployment
        result = await self._reconcile_deployment(name, namespace, spec, owner_reference)
        results.append(result)

        # Reconcile Service
        result = await self._reconcile_service(name, namespace, spec, owner_reference)
        results.append(result)

        # Reconcile Ingress if enabled
        if spec.ingress_enabled and spec.ingress_host:
            result = await self._reconcile_ingress(name, namespace, spec, owner_reference)
            results.append(result)

        return results

    async def _reconcile_configmap(
        self,
        name: str,
        namespace: str,
        spec: PortfolioStackSpec,
        owner_reference: Dict[str, Any],
    ) -> ReconcileResult:
        """Reconcile ConfigMap resource."""
        configmap_name = f"{name}-config"

        configmap = client.V1ConfigMap(
            metadata=client.V1ObjectMeta(
                name=configmap_name,
                namespace=namespace,
                labels=self._get_labels(name),
                owner_references=[self._make_owner_ref(owner_reference)],
            ),
            data=spec.config_data,
        )

        try:
            existing = self.core_v1.read_namespaced_config_map(configmap_name, namespace)

            # Check if update needed
            if existing.data != spec.config_data:
                self.core_v1.replace_namespaced_config_map(configmap_name, namespace, configmap)
                return ReconcileResult(
                    action=ReconcileAction.UPDATE,
                    resource_type="ConfigMap",
                    resource_name=configmap_name,
                    success=True,
                    message="ConfigMap updated",
                )
            return ReconcileResult(
                action=ReconcileAction.NOOP,
                resource_type="ConfigMap",
                resource_name=configmap_name,
                success=True,
            )

        except ApiException as e:
            if e.status == 404:
                self.core_v1.create_namespaced_config_map(namespace, configmap)
                return ReconcileResult(
                    action=ReconcileAction.CREATE,
                    resource_type="ConfigMap",
                    resource_name=configmap_name,
                    success=True,
                    message="ConfigMap created",
                )
            return ReconcileResult(
                action=ReconcileAction.NOOP,
                resource_type="ConfigMap",
                resource_name=configmap_name,
                success=False,
                error=str(e),
            )

    async def _reconcile_deployment(
        self,
        name: str,
        namespace: str,
        spec: PortfolioStackSpec,
        owner_reference: Dict[str, Any],
    ) -> ReconcileResult:
        """Reconcile Deployment resource."""
        deployment_name = f"{name}-deployment"

        # Build container spec
        container = client.V1Container(
            name=name,
            image=f"{spec.image}:{spec.version}",
            ports=[client.V1ContainerPort(container_port=spec.port)],
            env=[
                client.V1EnvVar(name=k, value=v)
                for k, v in spec.env.items()
            ],
            resources=client.V1ResourceRequirements(
                requests=spec.resources.get("requests", {"cpu": "100m", "memory": "128Mi"}),
                limits=spec.resources.get("limits", {"cpu": "500m", "memory": "512Mi"}),
            ),
            liveness_probe=client.V1Probe(
                http_get=client.V1HTTPGetAction(path="/health", port=spec.port),
                initial_delay_seconds=10,
                period_seconds=10,
            ),
            readiness_probe=client.V1Probe(
                http_get=client.V1HTTPGetAction(path="/ready", port=spec.port),
                initial_delay_seconds=5,
                period_seconds=5,
            ),
        )

        # Add config volume if configmap exists
        volumes = []
        volume_mounts = []
        if spec.config_data:
            volumes.append(client.V1Volume(
                name="config",
                config_map=client.V1ConfigMapVolumeSource(name=f"{name}-config"),
            ))
            volume_mounts.append(client.V1VolumeMount(
                name="config",
                mount_path="/app/config",
            ))
            container.volume_mounts = volume_mounts

        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(
                name=deployment_name,
                namespace=namespace,
                labels=self._get_labels(name),
                owner_references=[self._make_owner_ref(owner_reference)],
            ),
            spec=client.V1DeploymentSpec(
                replicas=spec.replicas,
                selector=client.V1LabelSelector(
                    match_labels={"app": name},
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={"app": name, "version": spec.version},
                    ),
                    spec=client.V1PodSpec(
                        containers=[container],
                        volumes=volumes if volumes else None,
                    ),
                ),
                strategy=client.V1DeploymentStrategy(
                    type="RollingUpdate",
                    rolling_update=client.V1RollingUpdateDeployment(
                        max_surge=1,
                        max_unavailable=0,
                    ),
                ),
            ),
        )

        try:
            existing = self.apps_v1.read_namespaced_deployment(deployment_name, namespace)

            # Check if update needed
            current_image = existing.spec.template.spec.containers[0].image
            desired_image = f"{spec.image}:{spec.version}"

            if current_image != desired_image or existing.spec.replicas != spec.replicas:
                self.apps_v1.replace_namespaced_deployment(deployment_name, namespace, deployment)
                return ReconcileResult(
                    action=ReconcileAction.UPDATE,
                    resource_type="Deployment",
                    resource_name=deployment_name,
                    success=True,
                    message=f"Deployment updated to {spec.version}",
                )
            return ReconcileResult(
                action=ReconcileAction.NOOP,
                resource_type="Deployment",
                resource_name=deployment_name,
                success=True,
            )

        except ApiException as e:
            if e.status == 404:
                self.apps_v1.create_namespaced_deployment(namespace, deployment)
                return ReconcileResult(
                    action=ReconcileAction.CREATE,
                    resource_type="Deployment",
                    resource_name=deployment_name,
                    success=True,
                    message="Deployment created",
                )
            return ReconcileResult(
                action=ReconcileAction.NOOP,
                resource_type="Deployment",
                resource_name=deployment_name,
                success=False,
                error=str(e),
            )

    async def _reconcile_service(
        self,
        name: str,
        namespace: str,
        spec: PortfolioStackSpec,
        owner_reference: Dict[str, Any],
    ) -> ReconcileResult:
        """Reconcile Service resource."""
        service_name = f"{name}-service"

        service = client.V1Service(
            metadata=client.V1ObjectMeta(
                name=service_name,
                namespace=namespace,
                labels=self._get_labels(name),
                owner_references=[self._make_owner_ref(owner_reference)],
            ),
            spec=client.V1ServiceSpec(
                selector={"app": name},
                ports=[
                    client.V1ServicePort(
                        port=80,
                        target_port=spec.port,
                        protocol="TCP",
                    )
                ],
                type="ClusterIP",
            ),
        )

        try:
            self.core_v1.read_namespaced_service(service_name, namespace)
            return ReconcileResult(
                action=ReconcileAction.NOOP,
                resource_type="Service",
                resource_name=service_name,
                success=True,
            )

        except ApiException as e:
            if e.status == 404:
                self.core_v1.create_namespaced_service(namespace, service)
                return ReconcileResult(
                    action=ReconcileAction.CREATE,
                    resource_type="Service",
                    resource_name=service_name,
                    success=True,
                    message="Service created",
                )
            return ReconcileResult(
                action=ReconcileAction.NOOP,
                resource_type="Service",
                resource_name=service_name,
                success=False,
                error=str(e),
            )

    async def _reconcile_ingress(
        self,
        name: str,
        namespace: str,
        spec: PortfolioStackSpec,
        owner_reference: Dict[str, Any],
    ) -> ReconcileResult:
        """Reconcile Ingress resource."""
        ingress_name = f"{name}-ingress"

        ingress = client.V1Ingress(
            metadata=client.V1ObjectMeta(
                name=ingress_name,
                namespace=namespace,
                labels=self._get_labels(name),
                owner_references=[self._make_owner_ref(owner_reference)],
                annotations={
                    "kubernetes.io/ingress.class": "nginx",
                },
            ),
            spec=client.V1IngressSpec(
                rules=[
                    client.V1IngressRule(
                        host=spec.ingress_host,
                        http=client.V1HTTPIngressRuleValue(
                            paths=[
                                client.V1HTTPIngressPath(
                                    path="/",
                                    path_type="Prefix",
                                    backend=client.V1IngressBackend(
                                        service=client.V1IngressServiceBackend(
                                            name=f"{name}-service",
                                            port=client.V1ServiceBackendPort(number=80),
                                        ),
                                    ),
                                )
                            ],
                        ),
                    )
                ],
            ),
        )

        try:
            self.networking_v1.read_namespaced_ingress(ingress_name, namespace)
            return ReconcileResult(
                action=ReconcileAction.NOOP,
                resource_type="Ingress",
                resource_name=ingress_name,
                success=True,
            )

        except ApiException as e:
            if e.status == 404:
                self.networking_v1.create_namespaced_ingress(namespace, ingress)
                return ReconcileResult(
                    action=ReconcileAction.CREATE,
                    resource_type="Ingress",
                    resource_name=ingress_name,
                    success=True,
                    message="Ingress created",
                )
            return ReconcileResult(
                action=ReconcileAction.NOOP,
                resource_type="Ingress",
                resource_name=ingress_name,
                success=False,
                error=str(e),
            )

    async def cleanup(
        self,
        name: str,
        namespace: str,
    ) -> List[ReconcileResult]:
        """Cleanup resources when PortfolioStack is deleted."""
        results = []
        # Kubernetes garbage collection handles cleanup via ownerReferences
        LOGGER.info(f"Cleanup triggered for {name} in {namespace}")
        return results

    def _get_labels(self, name: str) -> Dict[str, str]:
        """Get standard labels for resources."""
        return {
            "app.kubernetes.io/name": name,
            "app.kubernetes.io/managed-by": "portfolio-operator",
            "app.kubernetes.io/component": "stack",
        }

    def _make_owner_ref(self, owner: Dict[str, Any]) -> client.V1OwnerReference:
        """Create owner reference for garbage collection."""
        return client.V1OwnerReference(
            api_version=owner.get("apiVersion", "portfolio.example.com/v1alpha1"),
            kind=owner.get("kind", "PortfolioStack"),
            name=owner.get("name"),
            uid=owner.get("uid"),
            controller=True,
            block_owner_deletion=True,
        )
