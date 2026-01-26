# Project 17: Multi-Cloud Service Mesh

**Category:** Infrastructure & DevOps
**Status:** 🟡 40% Complete
**Source:** [View Code](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/17-service-mesh)

## Overview

**Istio service mesh** spanning AWS EKS and GKE clusters with **Consul** service discovery and mTLS across regions. Enables secure multi-cloud microservices communication, advanced traffic management, and observability without application code changes.

## Key Features

- **Multi-Cloud Connectivity** - Unified mesh across AWS and GCP
- **Zero-Trust Security** - mTLS encryption for all service-to-service traffic
- **Traffic Management** - Canary deployments, circuit breaking, retries
- **Service Discovery** - Consul integration for multi-cluster registry
- **Observability** - Distributed tracing, metrics, and logging

## Architecture

```
AWS EKS Cluster (us-east-1)          GKE Cluster (us-central1)
──────────────────────────           ─────────────────────────
Istio Control Plane                  Istio Control Plane
       ↓                                     ↓
  Envoy Sidecars                        Envoy Sidecars
       ↓                                     ↓
Services A, B, C ←──── East-West ────→ Services X, Y, Z
                       Gateway
                          ↓
                  Consul Service Registry
                          ↓
                   mTLS Certificate
                   (Vault/Cert-Manager)
```

**Service Mesh Components:**
1. **Control Plane**: Istiod for configuration and certificate management
2. **Data Plane**: Envoy sidecars for traffic interception
3. **East-West Gateway**: Cross-cluster communication
4. **Consul**: Service discovery across clouds
5. **Observability**: Jaeger (tracing), Prometheus (metrics), Kiali (visualization)

## Technologies

- **Istio** - Service mesh platform
- **Kubernetes** - Container orchestration (EKS, GKE)
- **Consul** - Service discovery and health checking
- **Envoy** - L7 proxy and communication bus
- **mTLS** - Mutual TLS authentication
- **Prometheus** - Metrics collection
- **Jaeger** - Distributed tracing
- **Kiali** - Service mesh observability
- **Bash** - Deployment automation

## Quick Start

```bash
cd projects/17-service-mesh

# Install Istio on primary cluster (AWS EKS)
./scripts/bootstrap.sh --cluster primary --provider aws

# Install Istio on remote cluster (GKE)
./scripts/bootstrap.sh --cluster remote --provider gcp

# Configure multi-cluster mesh
kubectl apply -f manifests/istio-operator.yaml
kubectl apply -f manifests/mesh-config.yaml

# Deploy sample application
kubectl apply -f examples/bookinfo/ -l istio=enabled

# View mesh topology in Kiali
kubectl port-forward -n istio-system svc/kiali 20001:20001
```

## Project Structure

```
17-service-mesh/
├── manifests/
│   ├── istio-operator.yaml      # Istio installation config
│   └── mesh-config.yaml         # Multi-cluster mesh settings
├── scripts/
│   └── bootstrap.sh             # Cluster provisioning
├── examples/                    # Sample services (to be added)
│   ├── bookinfo/
│   └── microservices-demo/
├── policies/                    # Traffic policies (to be added)
│   ├── virtual-services/
│   ├── destination-rules/
│   └── authorization-policies/
├── observability/               # Monitoring configs (to be added)
│   ├── prometheus/
│   └── jaeger/
└── README.md
```

## Business Impact

- **Security**: Zero-trust mTLS for 100% of service traffic
- **Reliability**: 99.99% uptime with automatic retries and circuit breaking
- **Multi-Cloud**: Avoid vendor lock-in with unified service layer
- **Observability**: 100% request tracing coverage
- **Developer Velocity**: Traffic shifting enables safe canary deployments

## Current Status

**Completed:**
- ✅ Istio operator installation manifest
- ✅ Basic mesh configuration
- ✅ Bootstrap script structure
- ✅ Multi-cluster architecture design

**In Progress:**
- 🟡 Complete bootstrap script for both clouds
- 🟡 East-west gateway configuration
- 🟡 Consul integration
- 🟡 Example microservices deployment

**Next Steps:**
1. Finish bootstrap script with full Istio installation
2. Configure east-west gateways for cross-cluster traffic
3. Integrate Consul for service discovery
4. Deploy example microservices application
5. Create traffic management policies (VirtualServices, DestinationRules)
6. Implement authorization policies for zero-trust
7. Set up Prometheus and Jaeger for observability
8. Deploy Kiali for mesh visualization
9. Add chaos testing for resilience validation
10. Document multi-cluster troubleshooting

## Key Learning Outcomes

- Service mesh architecture and patterns
- Istio installation and configuration
- Multi-cluster Kubernetes networking
- mTLS certificate management
- Traffic management and canary deployments
- Service discovery across clouds
- Distributed tracing and observability

---

**Related Projects:**
- [Project 1: AWS Infrastructure](/projects/01-aws-infrastructure) - EKS cluster foundation
- [Project 3: Kubernetes CI/CD](/projects/03-kubernetes-cicd) - Application deployment
- [Project 23: Monitoring](/projects/23-monitoring) - Observability integration
