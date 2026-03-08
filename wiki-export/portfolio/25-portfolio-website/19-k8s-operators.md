---
title: Project 19: Advanced Kubernetes Operators
description: **Category:** Infrastructure & DevOps **Status:** 🟡 50% Complete **Source:** [View Code](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/19-kubernetes-operators) Custom re
tags: [documentation, portfolio]
path: portfolio/25-portfolio-website/19-k8s-operators
created: 2026-03-08T22:19:13.341234+00:00
updated: 2026-03-08T22:04:38.692902+00:00
---

# Project 19: Advanced Kubernetes Operators

**Category:** Infrastructure & DevOps
**Status:** 🟡 50% Complete
**Source:** [View Code](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/19-kubernetes-operators)

## Overview

Custom resource operator built with **Kopf** (Kubernetes Operator Pythonic Framework) that manages portfolio deployments and orchestrates database migrations. Automates complex application lifecycle management with declarative custom resources.

## Key Features

- **Custom Resources** - Define `PortfolioApp` and `DatabaseMigration` CRDs
- **Automated Reconciliation** - Continuous state convergence to desired configuration
- **Database Migrations** - Orchestrates schema changes with zero downtime
- **Lifecycle Management** - Handles creation, updates, deletion, and scaling
- **Event-Driven** - React to Kubernetes events and external triggers

## Architecture

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

## Technologies

- **Python** - Operator implementation language
- **Kopf** - Kubernetes Operator framework
- **Kubernetes** - Container orchestration platform
- **CustomResourceDefinitions (CRDs)** - Extend Kubernetes API
- **Helm** - Package custom resources
- **Liquibase/Flyway** - Database migration tools
- **Docker** - Operator containerization

## Quick Start

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

## Project Structure

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

## Business Impact

- **Automation**: 90% reduction in manual deployment steps
- **Consistency**: Standardized deployment patterns across teams
- **Reliability**: Self-healing reconciliation ensures desired state
- **Migration Safety**: Zero-downtime database schema changes
- **Developer Experience**: Declarative app definition simplifies operations

## Current Status

**Completed:**
- ✅ Core operator structure with Kopf
- ✅ Basic event handling framework
- ✅ CRD design and schema

**In Progress:**
- 🟡 Complete CRD definitions (PortfolioApp, DatabaseMigration)
- 🟡 Full reconciliation logic
- 🟡 Database migration orchestration
- 🟡 Comprehensive examples

**Next Steps:**
1. Create complete CRD YAML definitions with validation
2. Implement create/update/delete handlers
3. Build deployment reconciler (generate K8s resources)
4. Add database migration orchestrator with Flyway/Liquibase
5. Implement status reporting and conditions
6. Add finalizers for cleanup logic
7. Create comprehensive integration tests
8. Build operator Docker image
9. Add RBAC policies and service account
10. Document custom resource API and examples

## Key Learning Outcomes

- Kubernetes operator pattern
- CustomResourceDefinitions (CRDs)
- Python Kopf framework
- Kubernetes API programming
- Declarative infrastructure
- Database migration strategies
- Controller reconciliation loops
- Event-driven automation

---

**Related Projects:**
- [Project 2: Database Migration](/projects/02-database-migration) - Migration patterns
- [Project 3: Kubernetes CI/CD](/projects/03-kubernetes-cicd) - Deployment automation
- [Project 1: AWS Infrastructure](/projects/01-aws-infrastructure) - EKS cluster hosting
