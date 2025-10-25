# Project 17: Multi-Cloud Service Mesh

## Overview
Istio service mesh spanning AWS and GKE clusters with Consul service discovery and mTLS across regions.

## Files
- `manifests/istio-operator.yaml` – installs Istio operator with multi-cluster support.
- `manifests/mesh-config.yaml` – configures east-west gateways and trust domains.
- `scripts/bootstrap.sh` – provisions remote clusters and installs the mesh.
