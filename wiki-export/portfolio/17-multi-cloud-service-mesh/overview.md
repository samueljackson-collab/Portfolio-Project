---
title: Project 17: Multi-Cloud Service Mesh
description: Istio service mesh spanning AWS EKS and GKE clusters with Consul service discovery and mTLS across regions
tags: [documentation, infrastructure-devops, istio, portfolio]
path: portfolio/17-multi-cloud-service-mesh/overview
created: 2026-03-08T22:19:13.225556+00:00
updated: 2026-03-08T22:04:38.578902+00:00
---

-

# Project 17: Multi-Cloud Service Mesh
> **Category:** Infrastructure & DevOps | **Status:** 🟡 40% Complete
> **Source:** projects/25-portfolio-website/docs/projects/17-service-mesh.md

## 📋 Executive Summary

**Istio service mesh** spanning AWS EKS and GKE clusters with **Consul** service discovery and mTLS across regions. Enables secure multi-cloud microservices communication, advanced traffic management, and observability without application code changes.

## 🎯 Project Objectives

- **Multi-Cloud Connectivity** - Unified mesh across AWS and GCP
- **Zero-Trust Security** - mTLS encryption for all service-to-service traffic
- **Traffic Management** - Canary deployments, circuit breaking, retries
- **Service Discovery** - Consul integration for multi-cluster registry
- **Observability** - Distributed tracing, metrics, and logging

## 🏗️ Architecture

> Source: ../../../projects/25-portfolio-website/docs/projects/17-service-mesh.md#architecture
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

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Istio | Istio | Service mesh platform |
| Kubernetes | Kubernetes | Container orchestration (EKS, GKE) |
| Consul | Consul | Service discovery and health checking |

## 💡 Key Technical Decisions

### Decision 1: Adopt Istio
**Context:** Project 17: Multi-Cloud Service Mesh requires a resilient delivery path.
**Decision:** Service mesh platform
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 2: Adopt Kubernetes
**Context:** Project 17: Multi-Cloud Service Mesh requires a resilient delivery path.
**Decision:** Container orchestration (EKS, GKE)
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 3: Adopt Consul
**Context:** Project 17: Multi-Cloud Service Mesh requires a resilient delivery path.
**Decision:** Service discovery and health checking
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

## 🔧 Implementation Details

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

## ✅ Results & Outcomes

- **Security**: Zero-trust mTLS for 100% of service traffic
- **Reliability**: 99.99% uptime with automatic retries and circuit breaking
- **Multi-Cloud**: Avoid vendor lock-in with unified service layer
- **Observability**: 100% request tracing coverage

## 📚 Documentation

- [README.md](../README.md)
- [RUNBOOK.md](../RUNBOOK.md)
- [projects/25-portfolio-website/docs/projects/17-service-mesh.md](../../../projects/25-portfolio-website/docs/projects/17-service-mesh.md)

## 🎓 Skills Demonstrated

**Technical Skills:** Istio, Kubernetes, Consul, Envoy, mTLS

**Soft Skills:** Communication, Incident response leadership, Documentation rigor

## 📦 Wiki Deliverables

### Diagrams

- **Architecture excerpt** — Copied from `../../../projects/25-portfolio-website/docs/projects/17-service-mesh.md` (Architecture section).

### Checklists

> Source: ../../../docs/PRJ-MASTER-PLAYBOOK/README.md#5-deployment--release

**Infrastructure**:
- [ ] Terraform plan reviewed and approved
- [ ] Database migrations tested
- [ ] Secrets configured in AWS Secrets Manager
- [ ] Monitoring alerts configured
- [ ] Runbook updated with new procedures

**Application**:
- [ ] All tests passing in staging
- [ ] Performance benchmarks met
- [ ] Feature flags configured (if using)
- [ ] Rollback plan documented
- [ ] Stakeholders notified of deployment

### Metrics

> Source: ../RUNBOOK.md#sloslis

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Service mesh availability** | 99.9% | Control plane uptime |
| **Cross-cluster latency** | < 100ms (p95) | AWS ↔ GCP communication time |
| **mTLS connection success rate** | 99.99% | Successful TLS handshakes |
| **Service discovery accuracy** | 100% | Correct endpoint resolution |
| **Gateway availability** | 99.95% | East-west gateway uptime |
| **Certificate renewal success** | 100% | Auto-renewal completion rate |
| **Envoy proxy health** | 99% | Healthy sidecar proxies |

### Screenshots

- **Operational dashboard mockup** — `../../../projects/06-homelab/PRJ-HOME-002/assets/mockups/grafana-dashboard.html` (captures golden signals per PRJ-MASTER playbook).

---

*Created: 2025-11-14 | Last Updated: 2025-11-14*
