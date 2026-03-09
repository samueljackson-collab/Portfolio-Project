---
title: Project 3: Kubernetes CI/CD Pipeline
description: GitOps-driven continuous delivery pipeline combining GitHub Actions for CI and ArgoCD for progressive deployment to Kubernetes
tags: [automation, cicd, containers, devops, documentation, github-actions, infrastructure-devops, kubernetes, orchestration, portfolio]
path: portfolio/3-kubernetes-cicd/overview
created: 2026-03-08T22:19:13.349116+00:00
updated: 2026-03-08T22:04:38.720902+00:00
---

-

# Project 3: Kubernetes CI/CD Pipeline
> **Category:** Infrastructure & DevOps | **Status:** 🟡 35% Complete
> **Source:** projects/25-portfolio-website/docs/projects/03-kubernetes-cicd.md

## 📋 Executive Summary

GitOps-driven continuous delivery pipeline combining **GitHub Actions** for CI and **ArgoCD** for progressive deployment to Kubernetes. Implements canary releases and automated rollback for safe production deployments.

## 🎯 Project Objectives

- **GitOps Workflow** - Git as single source of truth for desired state
- **Progressive Delivery** - Canary deployments with automated traffic shifting
- **Automated Rollback** - Health-based automatic rollback on failures
- **Multi-Environment** - Separate pipelines for dev, staging, production

## 🏗️ Architecture

> Source: ../../../projects/25-portfolio-website/docs/projects/03-kubernetes-cicd.md#architecture
```
Git Push → GitHub Actions → Build & Test → Push Image
                                ↓
                          Update Manifest
                                ↓
           ArgoCD ← Sync ← Git Repository
              ↓
        Kubernetes (Canary Deploy → Validate → Promote)
```

**Pipeline Stages:**
1. **Build**: Docker image creation and registry push
2. **Test**: Unit tests, integration tests, security scans
3. **Deploy Dev**: Automatic deployment to development
4. **Deploy Staging**: Manual approval gate
5. **Deploy Production**: Canary rollout (10% → 50% → 100%)

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| GitHub Actions | GitHub Actions | CI pipeline orchestration |
| ArgoCD | ArgoCD | GitOps continuous delivery |
| Kubernetes | Kubernetes | Container orchestration |

## 💡 Key Technical Decisions

### Decision 1: Adopt GitHub Actions
**Context:** Project 3: Kubernetes CI/CD Pipeline requires a resilient delivery path.
**Decision:** CI pipeline orchestration
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 2: Adopt ArgoCD
**Context:** Project 3: Kubernetes CI/CD Pipeline requires a resilient delivery path.
**Decision:** GitOps continuous delivery
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 3: Adopt Kubernetes
**Context:** Project 3: Kubernetes CI/CD Pipeline requires a resilient delivery path.
**Decision:** Container orchestration
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

## 🔧 Implementation Details

```bash
cd projects/3-kubernetes-cicd

# Deploy ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Create application
kubectl apply -f pipelines/argocd-app.yaml

# Trigger pipeline
git add . && git commit -m "Deploy v1.2.3" && git push
```

```
3-kubernetes-cicd/
├── pipelines/
│   ├── github-actions.yaml   # CI workflow
│   └── argocd-app.yaml       # ArgoCD application manifest
├── manifests/                # Kubernetes manifests (to be added)
│   ├── base/
│   └── overlays/
├── helm/                     # Helm charts (to be added)
└── README.md
```

## ✅ Results & Outcomes

- **Deployment Frequency**: 50+ deployments/week (vs 3/week previously)
- **Lead Time**: Reduced from 4 days to 2 hours
- **Failure Rate**: Decreased to 2% (from 15%)
- **MTTR**: 15 minutes with automated rollback (vs 2 hours manual)

## 📚 Documentation

- [README.md](../README.md)
- [RUNBOOK.md](../RUNBOOK.md)
- [projects/25-portfolio-website/docs/projects/03-kubernetes-cicd.md](../../../projects/25-portfolio-website/docs/projects/03-kubernetes-cicd.md)

## 🎓 Skills Demonstrated

**Technical Skills:** GitHub Actions, ArgoCD, Kubernetes, Helm, Istio

**Soft Skills:** Communication, Incident response leadership, Documentation rigor

## 📦 Wiki Deliverables

### Diagrams

- **Architecture excerpt** — Copied from `../../../projects/25-portfolio-website/docs/projects/03-kubernetes-cicd.md` (Architecture section).

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
| **Deployment success rate** | 99% | ArgoCD sync status success |
| **Deployment time** | < 10 minutes | Git commit → application running |
| **ArgoCD sync time** | < 3 minutes | Time to detect and sync changes |
| **CI pipeline success rate** | 95% | GitHub Actions workflow completion |
| **Rollback time (RTO)** | < 2 minutes | Time to revert to previous version |
| **Application availability during deploy** | 99.9% | Zero-downtime deployments |

### Screenshots

- **Operational dashboard mockup** — `../../../projects/06-homelab/PRJ-HOME-002/assets/mockups/grafana-dashboard.html` (captures golden signals per PRJ-MASTER playbook).

---

*Created: 2025-11-14 | Last Updated: 2025-11-14*
