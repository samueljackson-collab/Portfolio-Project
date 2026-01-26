#!/usr/bin/env python3
"""
Multi-Cloud Service Mesh Management CLI

Production-grade CLI tool for managing Istio service mesh across
multiple cloud providers (AWS EKS, GCP GKE, Azure AKS).

Features:
- Multi-cluster mesh configuration and deployment
- Traffic policy management (VirtualServices, DestinationRules)
- Security policy enforcement (AuthorizationPolicies, PeerAuthentication)
- Cross-cluster service discovery
- Observability stack integration (Jaeger, Kiali, Prometheus)
- Certificate management with automatic rotation
"""

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging
import yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('service-mesh-manager')


class CloudProvider(Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


class MeshComponent(Enum):
    ISTIOD = "istiod"
    INGRESS_GATEWAY = "istio-ingressgateway"
    EGRESS_GATEWAY = "istio-egressgateway"
    EAST_WEST_GATEWAY = "istio-eastwestgateway"


@dataclass
class ClusterConfig:
    """Configuration for a Kubernetes cluster in the mesh."""
    name: str
    provider: CloudProvider
    region: str
    context: str
    network: str
    is_primary: bool = False
    mesh_id: str = "multi-cloud-mesh"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "provider": self.provider.value,
            "region": self.region,
            "context": self.context,
            "network": self.network,
            "is_primary": self.is_primary,
            "mesh_id": self.mesh_id
        }


@dataclass
class TrafficPolicy:
    """Traffic routing policy configuration."""
    name: str
    namespace: str
    hosts: List[str]
    http_routes: List[Dict[str, Any]] = field(default_factory=list)
    timeout: str = "30s"
    retries: Optional[Dict[str, Any]] = None


@dataclass
class SecurityPolicy:
    """Security policy configuration for mTLS and authorization."""
    name: str
    namespace: str
    mtls_mode: str = "STRICT"
    rules: List[Dict[str, Any]] = field(default_factory=list)


class ServiceMeshManager:
    """
    Manages multi-cloud Istio service mesh operations.

    Supports:
    - AWS EKS
    - GCP GKE
    - Azure AKS
    """

    def __init__(self, config_path: Optional[str] = None):
        self.clusters: Dict[str, ClusterConfig] = {}
        self.istio_version = "1.20.0"
        self.config_path = Path(config_path) if config_path else Path("mesh-config.yaml")

        if self.config_path.exists():
            self._load_config()

    def _load_config(self) -> None:
        """Load mesh configuration from YAML file."""
        with open(self.config_path) as f:
            config = yaml.safe_load(f)

        for cluster_cfg in config.get("clusters", []):
            cluster = ClusterConfig(
                name=cluster_cfg["name"],
                provider=CloudProvider(cluster_cfg["provider"]),
                region=cluster_cfg["region"],
                context=cluster_cfg["context"],
                network=cluster_cfg["network"],
                is_primary=cluster_cfg.get("is_primary", False),
                mesh_id=cluster_cfg.get("mesh_id", "multi-cloud-mesh")
            )
            self.clusters[cluster.name] = cluster

    def _run_command(self, cmd: List[str], context: Optional[str] = None,
                     check: bool = True) -> subprocess.CompletedProcess:
        """Execute a command with optional kubectl context."""
        if context:
            cmd = ["kubectl", "--context", context] + cmd[1:] if cmd[0] == "kubectl" else cmd

        logger.debug(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if check and result.returncode != 0:
            logger.error(f"Command failed: {result.stderr}")
            raise RuntimeError(f"Command failed: {' '.join(cmd)}")

        return result

    def _run_istioctl(self, args: List[str], context: Optional[str] = None) -> str:
        """Execute istioctl command."""
        cmd = ["istioctl"] + args
        if context:
            cmd.extend(["--context", context])

        result = self._run_command(cmd)
        return result.stdout

    def add_cluster(self, cluster: ClusterConfig) -> None:
        """Add a cluster to the mesh configuration."""
        self.clusters[cluster.name] = cluster
        logger.info(f"Added cluster {cluster.name} to mesh configuration")

    def validate_cluster_connectivity(self, cluster_name: str) -> bool:
        """Validate connectivity to a cluster."""
        if cluster_name not in self.clusters:
            logger.error(f"Cluster {cluster_name} not found in configuration")
            return False

        cluster = self.clusters[cluster_name]
        try:
            result = self._run_command(
                ["kubectl", "cluster-info"],
                context=cluster.context,
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to connect to cluster {cluster_name}: {e}")
            return False

    def install_istio(self, cluster_name: str, profile: str = "default") -> None:
        """
        Install Istio on a cluster with multi-cluster configuration.

        Args:
            cluster_name: Name of the cluster
            profile: Istio installation profile (default, demo, minimal, etc.)
        """
        if cluster_name not in self.clusters:
            raise ValueError(f"Cluster {cluster_name} not in configuration")

        cluster = self.clusters[cluster_name]
        logger.info(f"Installing Istio on cluster {cluster_name} with profile {profile}")

        # Generate IstioOperator configuration
        istio_config = self._generate_istio_operator(cluster, profile)

        # Write config to temp file
        config_file = Path(f"/tmp/istio-{cluster_name}.yaml")
        with open(config_file, 'w') as f:
            yaml.dump(istio_config, f)

        # Install using istioctl
        self._run_istioctl(
            ["install", "-y", "-f", str(config_file)],
            context=cluster.context
        )

        logger.info(f"Istio installed successfully on {cluster_name}")

    def _generate_istio_operator(self, cluster: ClusterConfig,
                                  profile: str) -> Dict[str, Any]:
        """Generate IstioOperator configuration for multi-cluster setup."""
        config = {
            "apiVersion": "install.istio.io/v1alpha1",
            "kind": "IstioOperator",
            "spec": {
                "profile": profile,
                "meshConfig": {
                    "accessLogFile": "/dev/stdout",
                    "enableTracing": True,
                    "defaultConfig": {
                        "proxyMetadata": {
                            "ISTIO_META_DNS_CAPTURE": "true",
                            "ISTIO_META_DNS_AUTO_ALLOCATE": "true"
                        }
                    }
                },
                "values": {
                    "global": {
                        "meshID": cluster.mesh_id,
                        "multiCluster": {
                            "clusterName": cluster.name
                        },
                        "network": cluster.network
                    }
                },
                "components": {
                    "ingressGateways": [
                        {
                            "name": "istio-ingressgateway",
                            "enabled": True
                        }
                    ],
                    "egressGateways": [
                        {
                            "name": "istio-egressgateway",
                            "enabled": True
                        }
                    ]
                }
            }
        }

        # Add east-west gateway for primary clusters
        if cluster.is_primary:
            config["spec"]["components"]["ingressGateways"].append({
                "name": "istio-eastwestgateway",
                "label": {"istio": "eastwestgateway", "app": "istio-eastwestgateway"},
                "enabled": True,
                "k8s": {
                    "env": [
                        {"name": "ISTIO_META_ROUTER_MODE", "value": "sni-dnat"},
                        {"name": "ISTIO_META_REQUESTED_NETWORK_VIEW", "value": cluster.network}
                    ],
                    "service": {
                        "ports": [
                            {"name": "status-port", "port": 15021, "targetPort": 15021},
                            {"name": "tls", "port": 15443, "targetPort": 15443},
                            {"name": "tls-istiod", "port": 15012, "targetPort": 15012},
                            {"name": "tls-webhook", "port": 15017, "targetPort": 15017}
                        ]
                    }
                }
            })

        return config

    def setup_cross_cluster_discovery(self, primary: str, remote: str) -> None:
        """
        Configure cross-cluster service discovery between two clusters.

        Args:
            primary: Name of the primary cluster
            remote: Name of the remote cluster
        """
        if primary not in self.clusters or remote not in self.clusters:
            raise ValueError("Both clusters must be in configuration")

        primary_cluster = self.clusters[primary]
        remote_cluster = self.clusters[remote]

        logger.info(f"Setting up cross-cluster discovery: {primary} <-> {remote}")

        # Create remote secret for the remote cluster
        secret_cmd = [
            "istioctl", "create-remote-secret",
            "--context", remote_cluster.context,
            "--name", remote_cluster.name
        ]

        result = subprocess.run(secret_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to create remote secret: {result.stderr}")

        # Apply the secret to the primary cluster
        apply_cmd = ["kubectl", "--context", primary_cluster.context, "apply", "-f", "-"]
        subprocess.run(apply_cmd, input=result.stdout, text=True, check=True)

        logger.info(f"Cross-cluster discovery configured successfully")

    def apply_traffic_policy(self, policy: TrafficPolicy, cluster_name: str) -> None:
        """
        Apply a traffic routing policy (VirtualService).

        Args:
            policy: Traffic policy configuration
            cluster_name: Target cluster name
        """
        if cluster_name not in self.clusters:
            raise ValueError(f"Cluster {cluster_name} not in configuration")

        cluster = self.clusters[cluster_name]

        virtual_service = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": policy.name,
                "namespace": policy.namespace
            },
            "spec": {
                "hosts": policy.hosts,
                "http": policy.http_routes or [
                    {
                        "timeout": policy.timeout,
                        "route": [
                            {"destination": {"host": policy.hosts[0]}}
                        ]
                    }
                ]
            }
        }

        if policy.retries:
            virtual_service["spec"]["http"][0]["retries"] = policy.retries

        # Apply the VirtualService
        self._apply_manifest(virtual_service, cluster.context)
        logger.info(f"Applied traffic policy {policy.name} to {cluster_name}")

    def apply_security_policy(self, policy: SecurityPolicy, cluster_name: str) -> None:
        """
        Apply security policies (PeerAuthentication and AuthorizationPolicy).

        Args:
            policy: Security policy configuration
            cluster_name: Target cluster name
        """
        if cluster_name not in self.clusters:
            raise ValueError(f"Cluster {cluster_name} not in configuration")

        cluster = self.clusters[cluster_name]

        # Create PeerAuthentication for mTLS
        peer_auth = {
            "apiVersion": "security.istio.io/v1beta1",
            "kind": "PeerAuthentication",
            "metadata": {
                "name": f"{policy.name}-mtls",
                "namespace": policy.namespace
            },
            "spec": {
                "mtls": {
                    "mode": policy.mtls_mode
                }
            }
        }

        self._apply_manifest(peer_auth, cluster.context)

        # Create AuthorizationPolicy if rules are defined
        if policy.rules:
            auth_policy = {
                "apiVersion": "security.istio.io/v1beta1",
                "kind": "AuthorizationPolicy",
                "metadata": {
                    "name": policy.name,
                    "namespace": policy.namespace
                },
                "spec": {
                    "rules": policy.rules
                }
            }
            self._apply_manifest(auth_policy, cluster.context)

        logger.info(f"Applied security policy {policy.name} to {cluster_name}")

    def _apply_manifest(self, manifest: Dict[str, Any], context: str) -> None:
        """Apply a Kubernetes manifest to a cluster."""
        yaml_content = yaml.dump(manifest)
        cmd = ["kubectl", "--context", context, "apply", "-f", "-"]
        subprocess.run(cmd, input=yaml_content, text=True, check=True)

    def get_mesh_status(self, cluster_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the status of the service mesh.

        Args:
            cluster_name: Specific cluster or None for all clusters

        Returns:
            Dictionary with mesh status information
        """
        clusters_to_check = [cluster_name] if cluster_name else list(self.clusters.keys())
        status = {"clusters": {}, "overall_health": "healthy"}

        for name in clusters_to_check:
            if name not in self.clusters:
                continue

            cluster = self.clusters[name]
            cluster_status = {
                "connected": False,
                "istio_version": None,
                "components": {},
                "services_in_mesh": 0
            }

            try:
                # Check cluster connectivity
                cluster_status["connected"] = self.validate_cluster_connectivity(name)

                if cluster_status["connected"]:
                    # Get Istio version
                    version_output = self._run_istioctl(
                        ["version", "--short"],
                        context=cluster.context
                    )
                    cluster_status["istio_version"] = version_output.strip()

                    # Check component health
                    for component in MeshComponent:
                        pod_status = self._check_component_health(
                            component.value, cluster.context
                        )
                        cluster_status["components"][component.value] = pod_status

                    # Count services in mesh
                    result = self._run_command(
                        ["kubectl", "get", "pods", "-A",
                         "-l", "security.istio.io/tlsMode=istio",
                         "-o", "json"],
                        context=cluster.context,
                        check=False
                    )
                    if result.returncode == 0:
                        pods = json.loads(result.stdout)
                        cluster_status["services_in_mesh"] = len(pods.get("items", []))

            except Exception as e:
                logger.error(f"Error checking status for {name}: {e}")
                cluster_status["error"] = str(e)
                status["overall_health"] = "degraded"

            status["clusters"][name] = cluster_status

        return status

    def _check_component_health(self, component: str, context: str) -> Dict[str, Any]:
        """Check health of a specific Istio component."""
        result = self._run_command(
            ["kubectl", "get", "pods", "-n", "istio-system",
             "-l", f"app={component}", "-o", "json"],
            context=context,
            check=False
        )

        if result.returncode != 0:
            return {"status": "not_found", "replicas": 0, "ready": 0}

        pods = json.loads(result.stdout)
        items = pods.get("items", [])

        ready = sum(
            1 for pod in items
            if pod.get("status", {}).get("phase") == "Running"
        )

        return {
            "status": "healthy" if ready > 0 else "unhealthy",
            "replicas": len(items),
            "ready": ready
        }

    def configure_canary_deployment(self, service: str, namespace: str,
                                    stable_version: str, canary_version: str,
                                    canary_weight: int, cluster_name: str) -> None:
        """
        Configure canary deployment with traffic splitting.

        Args:
            service: Service name
            namespace: Kubernetes namespace
            stable_version: Stable version label
            canary_version: Canary version label
            canary_weight: Percentage of traffic to canary (0-100)
            cluster_name: Target cluster
        """
        if cluster_name not in self.clusters:
            raise ValueError(f"Cluster {cluster_name} not in configuration")

        cluster = self.clusters[cluster_name]
        stable_weight = 100 - canary_weight

        # Create DestinationRule
        destination_rule = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "DestinationRule",
            "metadata": {
                "name": service,
                "namespace": namespace
            },
            "spec": {
                "host": service,
                "trafficPolicy": {
                    "connectionPool": {
                        "tcp": {"maxConnections": 100},
                        "http": {"h2UpgradePolicy": "UPGRADE"}
                    },
                    "outlierDetection": {
                        "consecutive5xxErrors": 5,
                        "interval": "30s",
                        "baseEjectionTime": "30s"
                    }
                },
                "subsets": [
                    {"name": "stable", "labels": {"version": stable_version}},
                    {"name": "canary", "labels": {"version": canary_version}}
                ]
            }
        }

        # Create VirtualService with traffic splitting
        virtual_service = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": service,
                "namespace": namespace
            },
            "spec": {
                "hosts": [service],
                "http": [
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": service,
                                    "subset": "stable"
                                },
                                "weight": stable_weight
                            },
                            {
                                "destination": {
                                    "host": service,
                                    "subset": "canary"
                                },
                                "weight": canary_weight
                            }
                        ]
                    }
                ]
            }
        }

        self._apply_manifest(destination_rule, cluster.context)
        self._apply_manifest(virtual_service, cluster.context)

        logger.info(
            f"Configured canary deployment for {service}: "
            f"stable={stable_weight}%, canary={canary_weight}%"
        )

    def install_observability_stack(self, cluster_name: str) -> None:
        """
        Install observability components (Jaeger, Kiali, Prometheus, Grafana).

        Args:
            cluster_name: Target cluster name
        """
        if cluster_name not in self.clusters:
            raise ValueError(f"Cluster {cluster_name} not in configuration")

        cluster = self.clusters[cluster_name]

        logger.info(f"Installing observability stack on {cluster_name}")

        # Install Prometheus
        self._run_command(
            ["kubectl", "apply", "-f",
             "https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/prometheus.yaml"],
            context=cluster.context
        )

        # Install Jaeger
        self._run_command(
            ["kubectl", "apply", "-f",
             "https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/jaeger.yaml"],
            context=cluster.context
        )

        # Install Kiali
        self._run_command(
            ["kubectl", "apply", "-f",
             "https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/kiali.yaml"],
            context=cluster.context
        )

        # Install Grafana
        self._run_command(
            ["kubectl", "apply", "-f",
             "https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/grafana.yaml"],
            context=cluster.context
        )

        logger.info("Observability stack installed successfully")

    def export_config(self, output_path: str) -> None:
        """Export current mesh configuration to YAML file."""
        config = {
            "istio_version": self.istio_version,
            "clusters": [cluster.to_dict() for cluster in self.clusters.values()]
        }

        with open(output_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)

        logger.info(f"Configuration exported to {output_path}")


def create_sample_bookinfo_manifests() -> Dict[str, Any]:
    """Generate sample Bookinfo application manifests for demo."""
    return {
        "productpage": {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "productpage-v1", "labels": {"app": "productpage", "version": "v1"}},
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": "productpage", "version": "v1"}},
                "template": {
                    "metadata": {"labels": {"app": "productpage", "version": "v1"}},
                    "spec": {
                        "containers": [{
                            "name": "productpage",
                            "image": "docker.io/istio/examples-bookinfo-productpage-v1:1.18.0",
                            "ports": [{"containerPort": 9080}],
                            "resources": {
                                "requests": {"cpu": "100m", "memory": "128Mi"},
                                "limits": {"cpu": "200m", "memory": "256Mi"}
                            }
                        }]
                    }
                }
            }
        },
        "details": {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "details-v1", "labels": {"app": "details", "version": "v1"}},
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": "details", "version": "v1"}},
                "template": {
                    "metadata": {"labels": {"app": "details", "version": "v1"}},
                    "spec": {
                        "containers": [{
                            "name": "details",
                            "image": "docker.io/istio/examples-bookinfo-details-v1:1.18.0",
                            "ports": [{"containerPort": 9080}]
                        }]
                    }
                }
            }
        },
        "reviews": {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "reviews-v1", "labels": {"app": "reviews", "version": "v1"}},
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": "reviews", "version": "v1"}},
                "template": {
                    "metadata": {"labels": {"app": "reviews", "version": "v1"}},
                    "spec": {
                        "containers": [{
                            "name": "reviews",
                            "image": "docker.io/istio/examples-bookinfo-reviews-v1:1.18.0",
                            "ports": [{"containerPort": 9080}]
                        }]
                    }
                }
            }
        },
        "ratings": {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "ratings-v1", "labels": {"app": "ratings", "version": "v1"}},
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": "ratings", "version": "v1"}},
                "template": {
                    "metadata": {"labels": {"app": "ratings", "version": "v1"}},
                    "spec": {
                        "containers": [{
                            "name": "ratings",
                            "image": "docker.io/istio/examples-bookinfo-ratings-v1:1.18.0",
                            "ports": [{"containerPort": 9080}]
                        }]
                    }
                }
            }
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Cloud Service Mesh Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install Istio on a cluster")
    install_parser.add_argument("--cluster", required=True, help="Cluster name")
    install_parser.add_argument("--profile", default="default", help="Istio profile")
    install_parser.add_argument("--config", help="Path to mesh configuration file")

    # Status command
    status_parser = subparsers.add_parser("status", help="Get mesh status")
    status_parser.add_argument("--cluster", help="Specific cluster (optional)")
    status_parser.add_argument("--config", help="Path to mesh configuration file")
    status_parser.add_argument("--output", choices=["json", "text"], default="text")

    # Cross-cluster setup
    cross_parser = subparsers.add_parser("setup-cross-cluster",
                                          help="Setup cross-cluster discovery")
    cross_parser.add_argument("--primary", required=True, help="Primary cluster name")
    cross_parser.add_argument("--remote", required=True, help="Remote cluster name")
    cross_parser.add_argument("--config", help="Path to mesh configuration file")

    # Canary deployment
    canary_parser = subparsers.add_parser("canary", help="Configure canary deployment")
    canary_parser.add_argument("--service", required=True, help="Service name")
    canary_parser.add_argument("--namespace", default="default", help="Namespace")
    canary_parser.add_argument("--stable", required=True, help="Stable version label")
    canary_parser.add_argument("--canary", required=True, help="Canary version label")
    canary_parser.add_argument("--weight", type=int, default=10, help="Canary traffic %")
    canary_parser.add_argument("--cluster", required=True, help="Cluster name")
    canary_parser.add_argument("--config", help="Path to mesh configuration file")

    # Observability
    obs_parser = subparsers.add_parser("install-observability",
                                        help="Install observability stack")
    obs_parser.add_argument("--cluster", required=True, help="Cluster name")
    obs_parser.add_argument("--config", help="Path to mesh configuration file")

    # Security policy
    security_parser = subparsers.add_parser("apply-security",
                                             help="Apply security policies")
    security_parser.add_argument("--name", required=True, help="Policy name")
    security_parser.add_argument("--namespace", default="default", help="Namespace")
    security_parser.add_argument("--mtls", choices=["STRICT", "PERMISSIVE", "DISABLE"],
                                  default="STRICT", help="mTLS mode")
    security_parser.add_argument("--cluster", required=True, help="Cluster name")
    security_parser.add_argument("--config", help="Path to mesh configuration file")

    # Generate sample app
    sample_parser = subparsers.add_parser("generate-sample",
                                           help="Generate sample Bookinfo manifests")
    sample_parser.add_argument("--output", default="bookinfo.yaml", help="Output file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize manager
    config_path = getattr(args, 'config', None)
    manager = ServiceMeshManager(config_path)

    try:
        if args.command == "install":
            manager.install_istio(args.cluster, args.profile)

        elif args.command == "status":
            status = manager.get_mesh_status(args.cluster)
            if args.output == "json":
                print(json.dumps(status, indent=2))
            else:
                print(f"\nMesh Status: {status['overall_health'].upper()}")
                for name, cluster_status in status["clusters"].items():
                    print(f"\n  Cluster: {name}")
                    print(f"    Connected: {cluster_status['connected']}")
                    print(f"    Istio Version: {cluster_status.get('istio_version', 'N/A')}")
                    print(f"    Services in Mesh: {cluster_status.get('services_in_mesh', 0)}")
                    if cluster_status.get("components"):
                        print("    Components:")
                        for comp, comp_status in cluster_status["components"].items():
                            print(f"      - {comp}: {comp_status['status']} "
                                  f"({comp_status['ready']}/{comp_status['replicas']})")

        elif args.command == "setup-cross-cluster":
            manager.setup_cross_cluster_discovery(args.primary, args.remote)

        elif args.command == "canary":
            manager.configure_canary_deployment(
                args.service, args.namespace,
                args.stable, args.canary, args.weight,
                args.cluster
            )

        elif args.command == "install-observability":
            manager.install_observability_stack(args.cluster)

        elif args.command == "apply-security":
            policy = SecurityPolicy(
                name=args.name,
                namespace=args.namespace,
                mtls_mode=args.mtls
            )
            manager.apply_security_policy(policy, args.cluster)

        elif args.command == "generate-sample":
            manifests = create_sample_bookinfo_manifests()
            with open(args.output, 'w') as f:
                for name, manifest in manifests.items():
                    f.write(f"# {name.title()} Service\n")
                    yaml.dump(manifest, f)
                    f.write("---\n")
            print(f"Sample Bookinfo manifests written to {args.output}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
