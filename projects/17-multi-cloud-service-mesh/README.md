# Project 17: Multi-Cloud Service Mesh

## Overview
Istio service mesh spanning AWS and GKE clusters with Consul service discovery and mTLS across regions.

## Architecture
- **Context:** Services run across AWS and GKE clusters but must communicate over mTLS with shared identity, centralized policy, and consistent observability.
- **Decision:** Deploy east-west gateways on each cluster, peer them via Istio control plane and shared Consul catalog, and feed telemetry to a unified observability stack.
- **Consequences:** Delivers cross-cloud resiliency and secure service discovery, but requires disciplined certificate distribution and version alignment across clusters.

[Mermaid source](assets/diagrams/architecture.mmd) · Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

## Files
- `manifests/istio-operator.yaml` – installs Istio operator with multi-cluster support.
- `manifests/mesh-config.yaml` – configures east-west gateways and trust domains.
- `scripts/bootstrap.sh` – provisions remote clusters and installs the mesh.
