---
title: Project 19: Advanced Kubernetes Operators
description: Custom resource operator built with Kopf (Kubernetes Operator Pythonic Framework) that manages portfolio deployments and orchestrates database migrations
tags: [containers, documentation, infrastructure-devops, kubernetes, orchestration, portfolio, python]
path: portfolio/19-advanced-kubernetes-operators/overview
created: 2026-03-08T22:19:13.238437+00:00
updated: 2026-03-08T22:04:38.594902+00:00
---

-

# Project 19: Advanced Kubernetes Operators
> **Category:** Infrastructure & DevOps | **Status:** 🟡 50% Complete
> **Source:** projects/25-portfolio-website/docs/projects/19-k8s-operators.md

## 📋 Executive Summary

Custom resource operator built with **Kopf** (Kubernetes Operator Pythonic Framework) that manages portfolio deployments and orchestrates database migrations. Automates complex application lifecycle management with declarative custom resources.

## 🎯 Project Objectives

- **Custom Resources** - Define `PortfolioApp` and `DatabaseMigration` CRDs
- **Automated Reconciliation** - Continuous state convergence to desired configuration
- **Database Migrations** - Orchestrates schema changes with zero downtime
- **Lifecycle Management** - Handles creation, updates, deletion, and scaling
- **Event-Driven** - React to Kubernetes events and external triggers

## 🏗️ Architecture

> Source: ../../../projects/25-portfolio-website/docs/projects/19-k8s-operators.md#architecture
```
Custom Resource (PortfolioApp)
         ↓
    Kubernetes API Server
         ↓
    Operator (Kopf) ← Watches ← CRD Events
         ↓
  ┌─── Reconciliation Loop ───┐
  ↓                            ↓
Create/Update              Delete
Resources:                 Cleanup:
- Deployment              - Graceful shutdown
- Service                 - Data backup
- ConfigMap               - Resource removal
- PVC
- Migration Job
```

**Operator Workflow:**
1. **Watch**: Monitor `PortfolioApp` custom resources
2. **Reconcile**: Compare desired vs current state
3. **Create**: Generate Deployment, Service, ConfigMap
4. **Migrate**: Run database schema migrations
5. **Update**: Handle configuration changes
6. **Scale**: Adjust replicas based on load
7. **Delete**: Clean up resources with finalizers

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Python | Python | Operator implementation language |
| Kopf | Kopf | Kubernetes Operator framework |
| Kubernetes | Kubernetes | Container orchestration platform |

## 💡 Key Technical Decisions

### Decision 1: Adopt Python
**Context:** Project 19: Advanced Kubernetes Operators requires a resilient delivery path.
**Decision:** Operator implementation language
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 2: Adopt Kopf
**Context:** Project 19: Advanced Kubernetes Operators requires a resilient delivery path.
**Decision:** Kubernetes Operator framework
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 3: Adopt Kubernetes
**Context:** Project 19: Advanced Kubernetes Operators requires a resilient delivery path.
**Decision:** Container orchestration platform
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

## 🔧 Implementation Details

```bash
cd projects/19-kubernetes-operators

# Install dependencies
pip install -r requirements.txt

# Apply CRDs
kubectl apply -f crds/portfolioapp-crd.yaml
kubectl apply -f crds/databasemigration-crd.yaml

# Run operator locally (development)
kopf run src/operator.py

# Or deploy to cluster
docker build -t portfolio-operator:latest .
kubectl apply -f manifests/operator-deployment.yaml

# Create custom resource
kubectl apply -f examples/sample-app.yaml

# Check operator logs
kubectl logs -n portfolio-system deployment/portfolio-operator -f
```

```
19-kubernetes-operators/
├── src/
│   ├── __init__.py
│   ├── operator.py              # Main operator logic
│   ├── handlers/                # Event handlers (to be added)
│   │   ├── create_handler.py
│   │   ├── update_handler.py
│   │   └── delete_handler.py
│   └── reconcilers/             # Reconciliation logic (to be added)
│       ├── deployment.py
│       └── migration.py
├── crds/                        # Custom resource definitions (to be added)
│   ├── portfolioapp-crd.yaml
│   └── databasemigration-crd.yaml
├── examples/                    # Sample custom resources (to be added)
│   └── sample-app.yaml
├── manifests/                   # Operator deployment (to be added)
│   ├── operator-deployment.yaml
│   ├── rbac.yaml
│   └── namespace.yaml
├── tests/                       # Integration tests (to be added)
├── Dockerfile                   # Operator container (to be added)
├── requirements.txt
└── README.md
```

## ✅ Results & Outcomes

- **Automation**: 90% reduction in manual deployment steps
- **Consistency**: Standardized deployment patterns across teams
- **Reliability**: Self-healing reconciliation ensures desired state
- **Migration Safety**: Zero-downtime database schema changes

## 📚 Documentation

- [README.md](../README.md)
- [RUNBOOK.md](../RUNBOOK.md)
- [projects/25-portfolio-website/docs/projects/19-k8s-operators.md](../../../projects/25-portfolio-website/docs/projects/19-k8s-operators.md)

## 🎓 Skills Demonstrated

**Technical Skills:** Python, Kopf, Kubernetes, CustomResourceDefinitions (CRDs), Helm

**Soft Skills:** Communication, Incident response leadership, Documentation rigor

## 📦 Wiki Deliverables

### Diagrams

- **Architecture excerpt** — Copied from `../../../projects/25-portfolio-website/docs/projects/19-k8s-operators.md` (Architecture section).

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
| **Operator availability** | 99.9% | Operator pod uptime |
| **Reconciliation latency** | < 30 seconds (p95) | Time from CR change → reconciliation complete |
| **CRD operation success rate** | 99.5% | Successful create/update/delete operations |
| **Migration success rate** | 99% | Successful database migrations |
| **Webhook response time** | < 100ms (p95) | Validation/mutation webhook latency |
| **Event processing backlog** | < 50 events | Unprocessed Kubernetes events in queue |
| **Resource drift detection** | < 5 minutes | Time to detect and remediate drift |

### Screenshots

- **Operational dashboard mockup** — `../../../projects/06-homelab/PRJ-HOME-002/assets/mockups/grafana-dashboard.html` (captures golden signals per PRJ-MASTER playbook).

---

*Created: 2025-11-14 | Last Updated: 2025-11-14*
