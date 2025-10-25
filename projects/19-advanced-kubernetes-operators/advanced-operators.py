# Developer overview:
#   The classes in this module provide a working reference implementation
#   of the portfolio's Kubernetes operators along with the shared
#   auto-healing routines.  The accompanying `.internal_notes.md` file keeps
#   the long-form narrative that inspired this code.  What remains here are
#   succinct comments so the module reads like production-ready Python.

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple

from kubernetes import client, config
from kubernetes.client import ApiException


LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


@dataclass
class CustomResource:
    """Simple container representing a Kubernetes custom resource."""

    api_version: str
    kind: str
    metadata: Dict
    spec: Dict
    status: Optional[Dict] = None

    @property
    def name(self) -> str:
        return self.metadata["name"]

    @property
    def namespace(self) -> Optional[str]:
        return self.metadata.get("namespace")


class AdvancedKubernetesOperator:
    """Base class implementing the common operator reconciliation logic."""

    poll_interval_seconds = 20

    def __init__(self, group: str, version: str, plural: str, kind: str):
        self.group = group
        self.version = version
        self.plural = plural
        self.kind = kind

        # Attempt to load in-cluster config first, fall back to kubeconfig.
        try:
            config.load_incluster_config()
            LOGGER.info("Loaded in-cluster Kubernetes configuration")
        except config.ConfigException:
            config.load_kube_config()
            LOGGER.info("Loaded local kubeconfig")

        self.custom_api = client.CustomObjectsApi()
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.batch_v1 = client.BatchV1Api()

        self.watched_resources: Dict[str, CustomResource] = {}
        self.resource_versions: Dict[str, str] = {}
        self.reconciliation_queue: "asyncio.Queue[Tuple[str, str]]" = asyncio.Queue()
        self._stop_event = asyncio.Event()

        LOGGER.info("Initialised operator for %s/%s %s", group, version, plural)

    # ------------------------------------------------------------------
    # Public orchestration helpers
    # ------------------------------------------------------------------
    async def start_operator(self) -> None:
        """Start the operator event loops."""

        LOGGER.info("Starting operator %s", self.kind)
        await asyncio.gather(
            self._resource_polling_loop(),
            self._reconciliation_loop(),
            self._health_monitoring_loop(),
        )

    async def stop_operator(self) -> None:
        """Signal all tasks to stop."""

        self._stop_event.set()

    # ------------------------------------------------------------------
    # Core reconciliation logic
    # ------------------------------------------------------------------
    async def _resource_polling_loop(self) -> None:
        """Poll the API server for changes to the custom resources."""

        while not self._stop_event.is_set():
            try:
                response = await asyncio.to_thread(
                    self.custom_api.list_cluster_custom_object,
                    self.group,
                    self.version,
                    self.plural,
                )

                seen_resources = set()

                for item in response.get("items", []):
                    name = item["metadata"]["name"]
                    resource_version = item["metadata"].get("resourceVersion", "")
                    seen_resources.add(name)

                    event_type = self._determine_event_type(name, resource_version)
                    if event_type is None:
                        continue

                    custom_resource = CustomResource(
                        api_version=item.get("apiVersion", f"{self.group}/{self.version}"),
                        kind=item.get("kind", self.kind),
                        metadata=item["metadata"],
                        spec=item.get("spec", {}),
                        status=item.get("status"),
                    )

                    self.watched_resources[name] = custom_resource
                    self.resource_versions[name] = resource_version

                    await self._handle_resource_event(event_type, custom_resource)

                # Detect deletions by comparing with cached resources.
                removed = set(self.resource_versions) - seen_resources
                for name in removed:
                    resource = self.watched_resources.pop(name, None)
                    self.resource_versions.pop(name, None)
                    if resource:
                        await self._handle_resource_event("DELETED", resource)

            except ApiException as exc:
                LOGGER.error("Error polling custom resources: %s", exc)
            except Exception:  # pragma: no cover - defensive logging
                LOGGER.exception("Unexpected error while polling resources")

            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=self.poll_interval_seconds,
                )
            except asyncio.TimeoutError:
                pass

    def _determine_event_type(self, name: str, new_rv: str) -> Optional[str]:
        """Return the event type (ADDED/MODIFIED/None) for a resource version."""

        old_rv = self.resource_versions.get(name)
        if old_rv is None:
            return "ADDED"
        if new_rv != old_rv:
            return "MODIFIED"
        return None

    async def _handle_resource_event(self, event_type: str, resource: CustomResource) -> None:
        LOGGER.info("Event %s received for %s", event_type, resource.name)
        if event_type in {"ADDED", "MODIFIED"}:
            await self.reconciliation_queue.put(("RECONCILE", resource.name))
        elif event_type == "DELETED":
            await self.reconciliation_queue.put(("CLEANUP", resource.name))

    async def _reconciliation_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                action, resource_name = await asyncio.wait_for(
                    self.reconciliation_queue.get(), timeout=1.0
                )
            except asyncio.TimeoutError:
                continue

            resource = self.watched_resources.get(resource_name)

            try:
                if action == "RECONCILE" and resource is not None:
                    await self.reconcile_resource(resource)
                elif action == "CLEANUP":
                    await self.cleanup_resource(resource_name, resource)
            finally:
                self.reconciliation_queue.task_done()

    async def reconcile_resource(self, resource: CustomResource) -> None:
        """Drive the resource towards its desired state."""

        LOGGER.info("Reconciling %s/%s", resource.kind, resource.name)
        try:
            desired_state = resource.spec
            current_state = await self.get_current_state(resource)
            await self.sync_desired_state(resource, desired_state, current_state)
            await self.update_resource_status(
                resource,
                phase="Healthy",
                message="Reconciliation successful",
                extra_status={"lastApplied": datetime.utcnow().isoformat()},
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            LOGGER.exception("Failed to reconcile %s", resource.name)
            await self.update_resource_status(
                resource,
                phase="Error",
                message=str(exc),
            )

    async def cleanup_resource(self, resource_name: str, resource: Optional[CustomResource]) -> None:
        LOGGER.info("Cleaning up resource %s", resource_name)
        if resource is None:
            return
        try:
            await self.delete_associated_resources(resource)
        except Exception:  # pragma: no cover - defensive logging
            LOGGER.exception("Cleanup failed for %s", resource.name)

    async def _health_monitoring_loop(self) -> None:
        while not self._stop_event.is_set():
            for resource in list(self.watched_resources.values()):
                status = resource.status or {}
                if status.get("phase") == "Error":
                    LOGGER.warning("Resource %s in error phase; re-queueing", resource.name)
                    await self.reconciliation_queue.put(("RECONCILE", resource.name))
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=max(60, self.poll_interval_seconds * 2),
                )
            except asyncio.TimeoutError:
                pass

    # ------------------------------------------------------------------
    # Hooks for subclasses
    # ------------------------------------------------------------------
    async def sync_desired_state(
        self,
        resource: CustomResource,
        desired_state: Dict,
        current_state: Dict,
    ) -> None:
        raise NotImplementedError

    async def get_current_state(self, resource: CustomResource) -> Dict:
        """Return a minimal dictionary describing the current observed state."""

        status = resource.status or {}
        return {
            "phase": status.get("phase"),
            "conditions": status.get("conditions", []),
        }

    async def update_resource_status(
        self,
        resource: CustomResource,
        *,
        phase: str,
        message: str,
        extra_status: Optional[Dict] = None,
    ) -> None:
        namespace = resource.namespace
        body = {
            "status": {
                "phase": phase,
                "message": message,
                "lastUpdated": datetime.utcnow().isoformat(),
            }
        }
        if extra_status:
            body["status"].update(extra_status)

        try:
            if namespace:
                await asyncio.to_thread(
                    self.custom_api.patch_namespaced_custom_object_status,
                    self.group,
                    self.version,
                    namespace,
                    self.plural,
                    resource.name,
                    body,
                )
            else:
                await asyncio.to_thread(
                    self.custom_api.patch_cluster_custom_object_status,
                    self.group,
                    self.version,
                    self.plural,
                    resource.name,
                    body,
                )
        except ApiException as exc:
            LOGGER.error("Failed to patch status for %s: %s", resource.name, exc)

    async def delete_associated_resources(self, resource: CustomResource) -> None:
        """Delete Kubernetes primitives listed in the resource status."""

        managed_resources: Iterable[Dict] = []
        status = resource.status or {}
        if "managedResources" in status:
            managed_resources = status["managedResources"]
        elif "managedResources" in resource.spec:
            managed_resources = resource.spec["managedResources"]

        for managed in managed_resources:
            res_kind = managed.get("kind")
            name = managed.get("name")
            namespace = managed.get("namespace", resource.namespace)
            try:
                if res_kind == "StatefulSet":
                    await asyncio.to_thread(
                        self.apps_v1.delete_namespaced_stateful_set, name, namespace
                    )
                elif res_kind == "Service":
                    await asyncio.to_thread(
                        self.core_v1.delete_namespaced_service, name, namespace
                    )
                elif res_kind == "CronJob":
                    await asyncio.to_thread(
                        self.batch_v1.delete_namespaced_cron_job, name, namespace
                    )
                elif res_kind == "Job":
                    await asyncio.to_thread(
                        self.batch_v1.delete_namespaced_job,
                        name,
                        namespace,
                        propagation_policy="Foreground",
                    )
            except ApiException as exc:
                if exc.status != 404:
                    LOGGER.error("Failed to delete %s/%s: %s", res_kind, name, exc)

    # ------------------------------------------------------------------
    # Utility helpers for subclasses
    # ------------------------------------------------------------------
    async def apply_statefulset(self, manifest: Dict) -> None:
        namespace = manifest["metadata"]["namespace"]
        name = manifest["metadata"]["name"]

        def _apply() -> None:
            try:
                self.apps_v1.patch_namespaced_stateful_set(name, namespace, manifest)
                LOGGER.info("Patched StatefulSet %s/%s", namespace, name)
            except ApiException as exc:
                if exc.status == 404:
                    self.apps_v1.create_namespaced_stateful_set(namespace, manifest)
                    LOGGER.info("Created StatefulSet %s/%s", namespace, name)
                else:
                    raise

        await asyncio.to_thread(_apply)

    async def apply_service(self, manifest: Dict) -> None:
        namespace = manifest["metadata"]["namespace"]
        name = manifest["metadata"]["name"]

        def _apply() -> None:
            try:
                self.core_v1.patch_namespaced_service(name, namespace, manifest)
                LOGGER.info("Patched Service %s/%s", namespace, name)
            except ApiException as exc:
                if exc.status == 404:
                    self.core_v1.create_namespaced_service(namespace, manifest)
                    LOGGER.info("Created Service %s/%s", namespace, name)
                else:
                    raise

        await asyncio.to_thread(_apply)

    async def apply_cronjob(self, manifest: Dict) -> None:
        namespace = manifest["metadata"]["namespace"]
        name = manifest["metadata"]["name"]

        def _apply() -> None:
            try:
                self.batch_v1.patch_namespaced_cron_job(name, namespace, manifest)
                LOGGER.info("Patched CronJob %s/%s", namespace, name)
            except ApiException as exc:
                if exc.status == 404:
                    self.batch_v1.create_namespaced_cron_job(namespace, manifest)
                    LOGGER.info("Created CronJob %s/%s", namespace, name)
                else:
                    raise

        await asyncio.to_thread(_apply)

    async def apply_job(self, manifest: Dict) -> None:
        namespace = manifest["metadata"]["namespace"]
        name = manifest["metadata"]["name"]

        def _apply() -> None:
            try:
                self.batch_v1.patch_namespaced_job(name, namespace, manifest)
                LOGGER.info("Patched Job %s/%s", namespace, name)
            except ApiException as exc:
                if exc.status == 404:
                    self.batch_v1.create_namespaced_job(namespace, manifest)
                    LOGGER.info("Created Job %s/%s", namespace, name)
                else:
                    raise

        await asyncio.to_thread(_apply)


class DatabaseOperator(AdvancedKubernetesOperator):
    """Operator managing PostgreSQL database clusters."""

    def __init__(self) -> None:
        super().__init__(
            group="database.example.com",
            version="v1alpha1",
            plural="databases",
            kind="Database",
        )

    async def sync_desired_state(
        self,
        resource: CustomResource,
        desired_state: Dict,
        current_state: Dict,
    ) -> None:
        db_name = resource.name
        namespace = resource.namespace or "default"

        db_type = desired_state.get("type", "postgres")
        replicas = int(desired_state.get("replicas", 3))
        storage_size = desired_state.get("storageSize", "10Gi")
        version = desired_state.get("version", "14")

        statefulset_manifest = self._create_database_statefulset(
            db_name, namespace, db_type, replicas, storage_size, version
        )
        await self.apply_statefulset(statefulset_manifest)

        service_manifest = self._create_database_service(db_name, namespace, db_type)
        await self.apply_service(service_manifest)

        backup_cfg = desired_state.get("backup", {})
        if backup_cfg.get("enabled", False):
            await self._configure_backups(resource, backup_cfg)

        await self._setup_database_monitoring(resource)

    def _create_database_statefulset(
        self,
        name: str,
        namespace: str,
        db_type: str,
        replicas: int,
        storage_size: str,
        version: str,
    ) -> Dict:
        container_image = f"{db_type}:{version}"
        container_name = f"{db_type}-primary"

        return {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {"name": f"{name}-cluster", "namespace": namespace},
            "spec": {
                "serviceName": f"{name}-svc",
                "replicas": replicas,
                "selector": {"matchLabels": {"app": name, "component": "database"}},
                "template": {
                    "metadata": {"labels": {"app": name, "component": "database"}},
                    "spec": {
                        "containers": [
                            {
                                "name": container_name,
                                "image": container_image,
                                "ports": [{"containerPort": 5432}],
                                "env": [
                                    {
                                        "name": "POSTGRES_DB",
                                        "value": name,
                                    },
                                    {
                                        "name": "POSTGRES_USER",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": f"{name}-credentials",
                                                "key": "username",
                                            }
                                        },
                                    },
                                    {
                                        "name": "POSTGRES_PASSWORD",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": f"{name}-credentials",
                                                "key": "password",
                                            }
                                        },
                                    },
                                ],
                                "volumeMounts": [
                                    {
                                        "name": "data",
                                        "mountPath": "/var/lib/postgresql/data",
                                    }
                                ],
                                "livenessProbe": {
                                    "exec": {"command": ["pg_isready", "-U", "postgres"]},
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10,
                                },
                                "readinessProbe": {
                                    "exec": {"command": ["pg_isready", "-U", "postgres"]},
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5,
                                },
                            }
                        ],
                    },
                },
                "volumeClaimTemplates": [
                    {
                        "metadata": {"name": "data"},
                        "spec": {
                            "accessModes": ["ReadWriteOnce"],
                            "resources": {"requests": {"storage": storage_size}},
                        },
                    }
                ],
            },
        }

    def _create_database_service(self, name: str, namespace: str, db_type: str) -> Dict:
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": f"{name}-svc", "namespace": namespace},
            "spec": {
                "type": "ClusterIP",
                "ports": [
                    {
                        "name": "postgresql",
                        "port": 5432,
                        "targetPort": 5432,
                    }
                ],
                "selector": {"app": name, "component": "database"},
            },
        }

    async def _configure_backups(self, resource: CustomResource, backup_cfg: Dict) -> None:
        namespace = resource.namespace or "default"
        cronjob = {
            "apiVersion": "batch/v1",
            "kind": "CronJob",
            "metadata": {"name": f"{resource.name}-backup", "namespace": namespace},
            "spec": {
                "schedule": backup_cfg.get("schedule", "0 2 * * *"),
                "successfulJobsHistoryLimit": 3,
                "failedJobsHistoryLimit": 1,
                "jobTemplate": {
                    "spec": {
                        "template": {
                            "spec": {
                                "restartPolicy": "OnFailure",
                                "containers": [
                                    {
                                        "name": "backup",
                                        "image": "postgres:14",
                                        "command": [
                                            "/bin/sh",
                                            "-c",
                                            "pg_dump -h {svc} -U $POSTGRES_USER -F c {db} > /backup/backup_$(date +%Y%m%d%H%M%S).dump".format(
                                                svc=f"{resource.name}-svc",
                                                db=resource.name,
                                            ),
                                        ],
                                        "env": [
                                            {
                                                "name": "POSTGRES_USER",
                                                "valueFrom": {
                                                    "secretKeyRef": {
                                                        "name": f"{resource.name}-credentials",
                                                        "key": "username",
                                                    }
                                                },
                                            },
                                            {
                                                "name": "PGPASSWORD",
                                                "valueFrom": {
                                                    "secretKeyRef": {
                                                        "name": f"{resource.name}-credentials",
                                                        "key": "password",
                                                    }
                                                },
                                            },
                                        ],
                                        "volumeMounts": [
                                            {"name": "backup", "mountPath": "/backup"}
                                        ],
                                    }
                                ],
                                "volumes": [
                                    {
                                        "name": "backup",
                                        "persistentVolumeClaim": {
                                            "claimName": backup_cfg.get(
                                                "pvcName", f"{resource.name}-backup"
                                            )
                                        },
                                    }
                                ],
                            }
                        }
                    }
                },
            },
        }

        await self.apply_cronjob(cronjob)

    async def _setup_database_monitoring(self, resource: CustomResource) -> None:
        namespace = resource.namespace or "default"
        config_map_manifest = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{resource.name}-monitoring",
                "namespace": namespace,
                "labels": {"app": resource.name, "component": "database"},
            },
            "data": {
                "alerts.yaml": """
rules:
- alert: DatabaseReplicationLag
  expr: pg_replication_lag_seconds > 30
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: Replication lag for {name} is above threshold
""".format(
                    name=resource.name
                ),
            },
        }

        def _apply() -> None:
            try:
                self.core_v1.patch_namespaced_config_map(
                    config_map_manifest["metadata"]["name"],
                    namespace,
                    config_map_manifest,
                )
            except ApiException as exc:
                if exc.status == 404:
                    self.core_v1.create_namespaced_config_map(namespace, config_map_manifest)
                else:
                    raise

        await asyncio.to_thread(_apply)


class MLTrainingOperator(AdvancedKubernetesOperator):
    """Operator orchestrating machine-learning training workloads."""

    def __init__(self) -> None:
        super().__init__(
            group="ml.example.com",
            version="v1alpha1",
            plural="mltrainings",
            kind="MLTraining",
        )

    async def sync_desired_state(
        self,
        resource: CustomResource,
        desired_state: Dict,
        current_state: Dict,
    ) -> None:
        namespace = resource.namespace or "default"
        model_type = desired_state.get("modelType", "pytorch")
        gpu_count = int(desired_state.get("gpuCount", 1))
        dataset = desired_state.get("dataset", "s3://datasets/default")
        hyperparams = desired_state.get("hyperparameters", {})

        job_manifest = self._create_training_job(
            name=resource.name,
            namespace=namespace,
            model_type=model_type,
            gpu_count=gpu_count,
            dataset=dataset,
            hyperparameters=hyperparams,
        )

        await self.apply_job(job_manifest)
        await self._setup_model_registry(resource)

    def _create_training_job(
        self,
        name: str,
        namespace: str,
        model_type: str,
        gpu_count: int,
        dataset: str,
        hyperparameters: Dict,
    ) -> Dict:
        command = [
            "python",
            "train.py",
            "--dataset",
            dataset,
            "--epochs",
            str(hyperparameters.get("epochs", 50)),
            "--batch-size",
            str(hyperparameters.get("batchSize", 32)),
            "--learning-rate",
            str(hyperparameters.get("learningRate", 0.001)),
        ]

        return {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {"name": f"{name}-training", "namespace": namespace},
            "spec": {
                "template": {
                    "spec": {
                        "containers": [
                            {
                                "name": "trainer",
                                "image": f"ml-platform/{model_type}-training:latest",
                                "command": command,
                                "resources": {"limits": {"nvidia.com/gpu": gpu_count}},
                                "volumeMounts": [
                                    {"name": "dataset", "mountPath": "/data"},
                                    {"name": "model", "mountPath": "/models"},
                                ],
                            }
                        ],
                        "restartPolicy": "Never",
                        "volumes": [
                            {
                                "name": "dataset",
                                "persistentVolumeClaim": {"claimName": "dataset-pvc"},
                            },
                            {
                                "name": "model",
                                "persistentVolumeClaim": {"claimName": "model-registry"},
                            },
                        ],
                    }
                },
                "backoffLimit": 2,
            },
        }

    async def _setup_model_registry(self, resource: CustomResource) -> None:
        namespace = resource.namespace or "default"
        config_map_manifest = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{resource.name}-model-registry",
                "namespace": namespace,
                "labels": {"ml.example.com/registry": resource.name},
            },
            "data": {
                "registry.yaml": """
registry:
  modelName: {name}
  storage: s3://ml-registry/{name}
  trackingServer: http://mlflow.ml-system.svc.cluster.local
""".format(
                    name=resource.name
                ),
            },
        }

        def _apply() -> None:
            try:
                self.core_v1.patch_namespaced_config_map(
                    config_map_manifest["metadata"]["name"],
                    namespace,
                    config_map_manifest,
                )
            except ApiException as exc:
                if exc.status == 404:
                    self.core_v1.create_namespaced_config_map(namespace, config_map_manifest)
                else:
                    raise

        await asyncio.to_thread(_apply)


class AutoHealingOperator:
    """Background monitors providing automated remediation."""

    def __init__(self) -> None:
        try:
            config.load_incluster_config()
        except config.ConfigException:
            config.load_kube_config()

        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.metrics_api = client.CustomObjectsApi()
        self._metrics_available = True

    async def start_auto_healing(self) -> None:
        await asyncio.gather(
            self._monitor_pod_health(),
            self._monitor_node_health(),
            self._monitor_resource_usage(),
        )

    async def _monitor_pod_health(self) -> None:
        while True:
            try:
                pods = await asyncio.to_thread(self.core_v1.list_pod_for_all_namespaces)
                for pod in pods.items:
                    if self._is_pod_unhealthy(pod):
                        LOGGER.warning("Pod %s/%s unhealthy", pod.metadata.namespace, pod.metadata.name)
                        await self._heal_pod(pod)
            except ApiException as exc:
                LOGGER.error("Pod health monitoring failed: %s", exc)
            await asyncio.sleep(30)

    def _is_pod_unhealthy(self, pod) -> bool:
        phase = pod.status.phase
        if phase in {"Failed", "Unknown"}:
            return True
        for container_status in pod.status.container_statuses or []:
            waiting = container_status.state.waiting
            if waiting and waiting.reason == "CrashLoopBackOff":
                return True
            if container_status.restart_count and container_status.restart_count > 5:
                return True
        return False

    async def _heal_pod(self, pod) -> None:
        namespace, name = pod.metadata.namespace, pod.metadata.name
        try:
            await asyncio.to_thread(self.core_v1.delete_namespaced_pod, name, namespace)
            LOGGER.info("Deleted pod %s/%s for healing", namespace, name)
        except ApiException as exc:
            if exc.status != 404:
                LOGGER.error("Failed to delete pod %s/%s: %s", namespace, name, exc)

    async def _monitor_node_health(self) -> None:
        while True:
            try:
                nodes = await asyncio.to_thread(self.core_v1.list_node)
                for node in nodes.items:
                    for condition in node.status.conditions or []:
                        if condition.type == "Ready" and condition.status != "True":
                            LOGGER.warning("Node %s not ready: %s", node.metadata.name, condition.message)
            except ApiException as exc:
                LOGGER.error("Node monitoring failed: %s", exc)
            await asyncio.sleep(60)

    async def _monitor_resource_usage(self) -> None:
        while True:
            try:
                metrics = await asyncio.to_thread(
                    self.metrics_api.list_cluster_custom_object,
                    "metrics.k8s.io",
                    "v1beta1",
                    "nodes",
                )
                node_list = await asyncio.to_thread(self.core_v1.list_node)
                capacity_lookup = {
                    node.metadata.name: node.status.capacity or {}
                    for node in node_list.items
                }

                cpu_percentages: List[float] = []
                memory_percentages: List[float] = []

                for item in metrics.get("items", []):
                    node_name = item.get("metadata", {}).get("name")
                    if not node_name:
                        continue

                    usage = item.get("usage", {})
                    cpu_mcores = self._parse_cpu_millicores(usage.get("cpu", "0"))
                    mem_mib = self._parse_memory_mebibytes(usage.get("memory", "0"))

                    capacity = capacity_lookup.get(node_name, {})
                    cpu_capacity = self._parse_cpu_millicores(capacity.get("cpu", "0"))
                    mem_capacity = self._parse_memory_mebibytes(capacity.get("memory", "0"))

                    cpu_pct = cpu_mcores / cpu_capacity if cpu_capacity else 0.0
                    mem_pct = mem_mib / mem_capacity if mem_capacity else 0.0

                    cpu_percentages.append(cpu_pct)
                    memory_percentages.append(mem_pct)

                    if cpu_pct >= 0.9 or mem_pct >= 0.9:
                        LOGGER.warning(
                            "Node %s under resource pressure (cpu=%.0f%%, memory=%.0f%%)",
                            node_name,
                            cpu_pct * 100,
                            mem_pct * 100,
                        )
                    else:
                        LOGGER.debug(
                            "Node %s usage cpu=%.0f%% memory=%.0f%%",
                            node_name,
                            cpu_pct * 100,
                            mem_pct * 100,
                        )

                if cpu_percentages:
                    LOGGER.info(
                        "Cluster resource usage cpu=%.0f%% memory=%.0f%%",
                        (sum(cpu_percentages) / len(cpu_percentages)) * 100,
                        (sum(memory_percentages) / len(memory_percentages)) * 100,
                    )

                self._metrics_available = True
            except ApiException as exc:
                if exc.status in {404, 503}:
                    if self._metrics_available:
                        LOGGER.warning("Metrics API unavailable: %s", exc)
                    self._metrics_available = False
                else:
                    LOGGER.error("Failed to query metrics API: %s", exc)
            except Exception:  # pragma: no cover - defensive logging
                LOGGER.exception("Unexpected error while monitoring resource usage")

            await asyncio.sleep(120 if self._metrics_available else 300)

    @staticmethod
    def _parse_cpu_millicores(value: str) -> float:
        value = value.strip()
        if not value:
            return 0.0
        try:
            if value.endswith("n"):
                return float(value[:-1]) / 1_000_000
            if value.endswith("u"):
                return float(value[:-1]) / 1_000
            if value.endswith("m"):
                return float(value[:-1])
            return float(value) * 1000.0
        except ValueError:
            LOGGER.debug("Unable to parse cpu quantity '%s'", value)
            return 0.0

    @staticmethod
    def _parse_memory_mebibytes(value: str) -> float:
        value = value.strip()
        if not value:
            return 0.0

        suffixes = {
            "Ki": 1 / 1024,
            "Mi": 1,
            "Gi": 1024,
            "Ti": 1024 * 1024,
            "Pi": 1024 * 1024 * 1024,
            "Ei": 1024 * 1024 * 1024 * 1024,
            "K": 1 / 1024,
            "M": 1,
            "G": 1024,
            "T": 1024 * 1024,
        }

        for suffix, multiplier in suffixes.items():
            if value.endswith(suffix):
                try:
                    return float(value[: -len(suffix)]) * multiplier
                except ValueError:
                    LOGGER.debug("Unable to parse memory quantity '%s'", value)
                    return 0.0

        try:
            return float(value) / (1024 * 1024)
        except ValueError:
            LOGGER.debug("Unable to parse raw memory quantity '%s'", value)
            return 0.0


class OperatorManager:
    """Helper that starts multiple operators and the auto-healing engine."""

    def __init__(self) -> None:
        self.operators: List[AdvancedKubernetesOperator] = []
        self.auto_healing = AutoHealingOperator()

    def register_operator(self, operator: AdvancedKubernetesOperator) -> None:
        LOGGER.info("Registering operator %s", operator.kind)
        self.operators.append(operator)

    async def start_all(self) -> None:
        tasks = [operator.start_operator() for operator in self.operators]
        tasks.append(self.auto_healing.start_auto_healing())
        await asyncio.gather(*tasks)


async def main() -> None:
    manager = OperatorManager()
    manager.register_operator(DatabaseOperator())
    manager.register_operator(MLTrainingOperator())

    await manager.start_all()


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("Operator manager interrupted by user")
