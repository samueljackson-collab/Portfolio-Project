---
title: "Kubernetes CI/CD Pipeline"
description: "GitOps-driven continuous delivery pipeline combining GitHub Actions and ArgoCD for progressive deployment."
published: true
date: 2026-01-23T15:24:46.000Z
tags:
  - kubernetes
  - ci-cd
  - argocd
  - github-actions
editor: markdown
dateCreated: 2026-01-23T15:24:46.000Z
---


# Kubernetes CI/CD Pipeline

> **Status**: Production Ready | **Completion**: [██████████] 100%
>
> `kubernetes` `ci-cd` `argocd` `github-actions`

GitOps-driven continuous delivery pipeline combining GitHub Actions and ArgoCD for progressive deployment.

---


## 📋 Table of Contents

1. [Problem Statement](#-problem-statement) - Why this project exists
2. [Learning Objectives](#-learning-objectives) - What you'll learn
3. [Architecture](#-architecture) - System design and components
4. [Tech Stack](#-tech-stack) - Technologies and their purposes
5. [Technology Deep Dives](#-technology-deep-dives) - In-depth explanations
6. [Implementation Guide](#-implementation-guide) - How to build it
7. [Best Practices](#-best-practices) - Do's and don'ts
8. [Quick Start](#-quick-start) - Get running in minutes
9. [Operational Guide](#-operational-guide) - Day-2 operations
10. [Real-World Scenarios](#-real-world-scenarios) - Practical applications

---


## 🎯 Problem Statement

### The Deployment Challenge

Traditional deployment processes are fraught with manual steps, tribal knowledge,
and prayers to the deployment gods:

**The Fear Factor**: "Deploy Fridays" are banned. Changes queue up for weeks waiting
for the "safe" deployment window. By the time they ship, developers have forgotten
the context, and issues are harder to debug.

**Inconsistent Environments**: "It works on my machine" becomes "it worked in staging."
Configuration differences between environments cause production failures that couldn't
be caught earlier.

**Rollback Roulette**: When deployments fail, rolling back is a manual, error-prone
process. Teams maintain "rollback runbooks" that are perpetually out of date.

**Coordination Overhead**: Deploying requires synchronizing between dev, QA, ops, and
often a manual approval chain. A simple change takes days to reach production.


**Business Impact:**
- Deployment velocity measured in weeks, not hours
- High-stress deployment events with all-hands-on-deck
- Customer-impacting incidents from failed deployments
- Developer frustration and burnout
- Competitive disadvantage from slow feature delivery


### How This Project Solves It


**GitOps and Progressive Delivery transform deployments:**

1. **Git as Source of Truth**: All configuration lives in Git. To change production,
   you change Git. Audit trail is automatic.

2. **Automated Pipelines**: Every commit triggers build, test, security scan, and
   deployment. Humans review, machines execute.

3. **Progressive Rollout**: Canary deployments expose changes to small user segments
   first. Issues are detected before full rollout.

4. **Automated Rollback**: Health checks continuously monitor deployments. Failures
   trigger automatic rollback—no human intervention required.


### Key Capabilities Delivered

- ✅ **Blue-Green/Canary deployments**
- ✅ **Automated rollback on health failure**
- ✅ **Multi-environment support**
- ✅ **Container security scanning**

---


## 🎓 Learning Objectives

By studying and implementing this project, you will:

   1. Design GitOps workflows with Git as source of truth
   2. Implement progressive deployment strategies (canary, blue-green)
   3. Configure automated rollback on health check failures
   4. Set up multi-environment promotion pipelines
   5. Integrate security scanning into CI/CD workflows

**Prerequisites:**
- Basic understanding of cloud services (AWS/GCP/Azure)
- Familiarity with containerization (Docker)
- Command-line proficiency (Bash/Linux)
- Version control with Git

**Estimated Learning Time:** 15-25 hours for full implementation

---


## 🏗️ Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Kubernetes CI/CD Pipeline                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌───────────────┐    ┌─────────────────┐    ┌───────────────────┐   │
│   │    INPUT      │    │   PROCESSING    │    │     OUTPUT        │   │
│   │               │───▶│                 │───▶│                   │   │
│   │ • API Gateway │    │ • Business Logic│    │ • Response/Events │   │
│   │ • Event Queue │    │ • Validation    │    │ • Persistence     │   │
│   │ • File Upload │    │ • Transformation│    │ • Notifications   │   │
│   └───────────────┘    └─────────────────┘    └───────────────────┘   │
│           │                    │                       │              │
│           └────────────────────┴───────────────────────┘              │
│                                │                                       │
│                    ┌───────────┴───────────┐                          │
│                    │    INFRASTRUCTURE     │                          │
│                    │ • Compute (EKS/Lambda)│                          │
│                    │ • Storage (S3/RDS)    │                          │
│                    │ • Network (VPC/ALB)   │                          │
│                    │ • Security (IAM/KMS)  │                          │
│                    └───────────────────────┘                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Breakdown

**Source Control**
- GitHub Repository, Branch Protection, Code Review

**CI Pipeline**
- GitHub Actions, Build, Test, Security Scan

**Artifact Storage**
- Container Registry, Helm Repository, Image Signing

**CD Pipeline**
- ArgoCD, Sync Policies, Health Checks, Rollback

### Data Flow

`Commit → Build → Test → Scan → Push Image → Sync to Cluster → Health Check`

### Design Decisions

| Decision | Rationale |
|----------|-----------|
| Multi-AZ Deployment | Ensures high availability during AZ failures |
| Managed Services | Reduces operational burden, focus on business logic |
| Infrastructure as Code | Reproducibility, version control, audit trail |
| GitOps Workflow | Single source of truth, automated reconciliation |

---


## 🛠️ Tech Stack

### Technologies Used

| Technology | Purpose & Rationale |
|------------|---------------------|
| **GitHub Actions** | Native CI/CD automation with deep GitHub integration and marketplace ecosystem |
| **ArgoCD** | GitOps controller continuously syncing Kubernetes state from Git repositories |
| **Helm** | Kubernetes package manager with templating for environment-specific configurations |
| **Kustomize** | Native Kubernetes configuration customization without templating |
| **Python** | Primary automation language for scripts, data processing, and ML pipelines |

### Why This Combination?

This stack was carefully selected based on:

1. **Production Maturity** - All components are battle-tested at scale
2. **Community & Ecosystem** - Strong documentation, plugins, and support
3. **Integration** - Technologies work together with established patterns
4. **Scalability** - Architecture supports growth without major refactoring
5. **Operability** - Built-in observability and debugging capabilities
6. **Cost Efficiency** - Balance of capability and cloud spend optimization

### Alternative Considerations

| Current Choice | Alternatives Considered | Why Current Was Chosen |
|---------------|------------------------|------------------------|
| Terraform | CloudFormation, Pulumi | Provider-agnostic, mature ecosystem |
| Kubernetes | ECS, Nomad | Industry standard, portable |
| PostgreSQL | MySQL, MongoDB | ACID compliance, JSON support |

---

## 🔬 Technology Deep Dives

### 📚 Why Kubernetes?

Kubernetes (K8s) is the industry-standard container orchestration platform.
Originally designed by Google based on their internal Borg system, it automates deployment,
scaling, and management of containerized applications across clusters of hosts.

Kubernetes abstracts away the underlying infrastructure, allowing you to describe your
application's desired state declaratively. The control plane continuously works to
maintain that state, handling failures, scaling, and updates automatically.

#### How It Works


**Architecture Overview:**
- **Control Plane**: API Server, etcd, Scheduler, Controller Manager
- **Worker Nodes**: kubelet, kube-proxy, Container Runtime
- **Pods**: Smallest deployable unit (one or more containers)

**Key Concepts:**
- **Deployments**: Manage stateless application replicas
- **Services**: Stable networking for pod communication
- **ConfigMaps/Secrets**: Configuration and sensitive data management
- **Ingress**: HTTP/HTTPS routing to services
- **Namespaces**: Virtual clusters for resource isolation


#### Working Code Example

```yaml
# Example: Kubernetes Deployment with Service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-application
  labels:
    app: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: nginx:1.25
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 5
        readinessProbe:
          httpGet:
            path: /ready
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 3
---
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

#### Key Benefits

- **Self-Healing**: Automatically restarts failed containers and replaces unhealthy nodes
- **Horizontal Scaling**: Scale applications based on CPU, memory, or custom metrics
- **Service Discovery**: Built-in DNS and load balancing between pods
- **Rolling Updates**: Zero-downtime deployments with automatic rollback
- **Declarative Configuration**: Define desired state, K8s reconciles reality
- **Secret Management**: Secure storage for sensitive configuration
- **Resource Management**: CPU/memory limits prevent noisy neighbors

#### Best Practices

- ✅ Always set resource requests and limits for containers
- ✅ Use namespaces to isolate environments and teams
- ✅ Implement liveness and readiness probes for all services
- ✅ Use PodDisruptionBudgets for high availability during maintenance
- ✅ Store manifests in Git and use GitOps for deployments
- ✅ Use NetworkPolicies to restrict pod-to-pod communication

#### Common Pitfalls to Avoid

- ❌ Running containers as root without security context
- ❌ Using `latest` tag for container images
- ❌ Storing secrets in ConfigMaps or environment variables
- ❌ Not setting resource limits (allows resource exhaustion)
- ❌ Single replica deployments for production workloads

#### Further Reading

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [CNCF Kubernetes Training](https://www.cncf.io/certification/cka/)
- [Kubernetes Patterns (Book)](https://k8spatterns.io/)

---

### 📚 Why ArgoCD?

ArgoCD is a declarative GitOps continuous delivery tool for Kubernetes.
It continuously monitors Git repositories and automatically syncs application state
to match the desired configuration stored in version control.

GitOps treats Git as the single source of truth for infrastructure and applications.
ArgoCD watches for changes in Git and reconciles the cluster state, providing
audit trails, easy rollbacks, and consistent deployments across environments.

#### How It Works


**GitOps Workflow:**
1. Developer commits changes to Git repository
2. ArgoCD detects changes via webhook or polling
3. ArgoCD compares desired state (Git) vs live state (cluster)
4. Out-of-sync resources are identified
5. ArgoCD syncs changes (manual or automatic)
6. Health checks verify deployment success

**Sync Strategies:**
- **Manual Sync**: Require explicit approval
- **Auto-Sync**: Automatically apply changes
- **Self-Heal**: Revert manual cluster changes


#### Working Code Example

```yaml
# Example: ArgoCD Application Manifest
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-application
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default

  source:
    repoURL: https://github.com/org/app-manifests.git
    targetRevision: main
    path: environments/production

    # Helm support
    helm:
      valueFiles:
        - values-production.yaml
      parameters:
        - name: image.tag
          value: "v1.2.3"

  destination:
    server: https://kubernetes.default.svc
    namespace: production

  syncPolicy:
    automated:
      prune: true      # Delete removed resources
      selfHeal: true   # Revert manual changes
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m

  # Health checks
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas  # Ignore HPA-managed replicas
```

#### Key Benefits

- **GitOps Native**: Git as single source of truth with full audit trail
- **Auto-Sync**: Automatically reconciles cluster state with Git
- **Multi-Cluster**: Manage deployments across multiple Kubernetes clusters
- **Rollback**: One-click rollback to any previous Git commit
- **RBAC**: Fine-grained access control with SSO integration
- **Health Monitoring**: Custom health checks for application resources
- **Web UI**: Visual dashboard for deployment status and history

#### Best Practices

- ✅ Separate application code repos from manifest repos
- ✅ Use ApplicationSets for multi-cluster/multi-env deployments
- ✅ Implement progressive delivery with Argo Rollouts
- ✅ Configure webhook triggers for faster sync detection
- ✅ Use projects to isolate teams and limit cluster access
- ✅ Enable self-heal to prevent configuration drift

#### Common Pitfalls to Avoid

- ❌ Storing sensitive values in Git (use sealed-secrets or external-secrets)
- ❌ Manual kubectl changes that bypass GitOps workflow
- ❌ Single Application for multiple unrelated services
- ❌ Disabling pruning (leaves orphaned resources)
- ❌ Auto-sync without proper CI validation gates

#### Further Reading

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [GitOps Principles](https://opengitops.dev/)
- [Argo Project](https://argoproj.github.io/)

---



## 📖 Implementation Guide

This section provides production-ready code you can adapt for your own projects.

### Pipeline

```yaml
# Complete GitOps CI/CD Pipeline
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ============================================
  # Stage 1: Build and Test
  # ============================================
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linting
        run: |
          ruff check .
          mypy src/

      - name: Run tests with coverage
        run: |
          pytest tests/ \
            --cov=src \
            --cov-report=xml \
            --cov-report=term-missing \
            --cov-fail-under=80

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage.xml
          fail_ci_if_error: true

  # ============================================
  # Stage 2: Security Scanning
  # ============================================
  security:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'

      - name: Run Semgrep SAST
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/secrets

  # ============================================
  # Stage 3: Build and Push Container
  # ============================================
  build:
    runs-on: ubuntu-latest
    needs: [test, security]
    permissions:
      contents: read
      packages: write
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
      digest: ${{ steps.build.outputs.digest }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix=
            type=ref,event=branch
            type=semver,pattern={{version}}

      - name: Build and push
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}@${{ steps.build.outputs.digest }}

  # ============================================
  # Stage 4: Deploy to Staging
  # ============================================
  deploy-staging:
    runs-on: ubuntu-latest
    needs: build
    environment: staging
    if: github.ref == 'refs/heads/develop'

    steps:
      - uses: actions/checkout@v4

      - name: Update Kubernetes manifests
        run: |
          cd k8s/overlays/staging
          kustomize edit set image app=${{ needs.build.outputs.image-tag }}

      - name: Commit and push
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add .
          git commit -m "Deploy to staging: ${{ github.sha }}"
          git push

      # ArgoCD will auto-sync from Git

  # ============================================
  # Stage 5: Deploy to Production
  # ============================================
  deploy-production:
    runs-on: ubuntu-latest
    needs: build
    environment: production
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Update Kubernetes manifests
        run: |
          cd k8s/overlays/production
          kustomize edit set image app=${{ needs.build.outputs.image-tag }}

      - name: Create canary deployment
        run: |
          # Deploy to 10% of traffic initially
          kubectl apply -f k8s/canary/

      - name: Monitor canary metrics
        run: |
          # Check error rate for 5 minutes
          ./scripts/canary-analysis.sh --threshold 0.01 --duration 300

      - name: Promote to full deployment
        run: |
          kubectl apply -f k8s/overlays/production/
```

### Argocd

```yaml
# ArgoCD Application with Progressive Delivery
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: production-app
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default

  source:
    repoURL: https://github.com/org/app-manifests.git
    targetRevision: main
    path: k8s/overlays/production

  destination:
    server: https://kubernetes.default.svc
    namespace: production

  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m

---
# Argo Rollout for Canary Deployments
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: app-rollout
  namespace: production
spec:
  replicas: 10
  selector:
    matchLabels:
      app: production-app
  template:
    metadata:
      labels:
        app: production-app
    spec:
      containers:
        - name: app
          image: app:latest
          ports:
            - containerPort: 8080
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5

  strategy:
    canary:
      steps:
        - setWeight: 10
        - pause: {duration: 5m}
        - setWeight: 30
        - pause: {duration: 5m}
        - setWeight: 50
        - pause: {duration: 10m}
        - setWeight: 100

      analysis:
        templates:
          - templateName: success-rate
        startingStep: 1
        args:
          - name: service-name
            value: production-app

      trafficRouting:
        istio:
          virtualService:
            name: app-vsvc
            routes:
              - primary

---
# Analysis Template for Canary Validation
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
    - name: service-name
  metrics:
    - name: success-rate
      interval: 1m
      successCondition: result[0] >= 0.99
      failureLimit: 3
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            sum(rate(http_requests_total{
              service="{{args.service-name}}",
              status=~"2.."
            }[5m])) /
            sum(rate(http_requests_total{
              service="{{args.service-name}}"
            }[5m]))
```

---


## ✅ Best Practices

### Infrastructure

| Practice | Description | Why It Matters |
|----------|-------------|----------------|
| **Infrastructure as Code** | Define all resources in version-controlled code | Reproducibility, audit trail, peer review |
| **Immutable Infrastructure** | Replace instances, don't modify them | Consistency, easier rollback, no drift |
| **Least Privilege** | Grant minimum required permissions | Security, blast radius reduction |
| **Multi-AZ Deployment** | Distribute across availability zones | High availability during AZ failures |

### Security

- ⛔ **Never** hardcode credentials in source code
- ⛔ **Never** commit secrets to version control
- ✅ **Always** use IAM roles over access keys
- ✅ **Always** encrypt data at rest and in transit
- ✅ **Always** enable audit logging (CloudTrail, VPC Flow Logs)

### Operations

1. **Observability First**
   - Instrument code before production deployment
   - Establish baselines for normal behavior
   - Create actionable alerts, not noise

2. **Automate Everything**
   - Manual processes don't scale
   - Runbooks should be scripts, not documents
   - Test automation regularly

3. **Practice Failure**
   - Regular DR drills validate recovery procedures
   - Chaos engineering builds confidence
   - Document and learn from incidents

### Code Quality

```python
# ✅ Good: Clear, testable, observable
class PaymentProcessor:
    def __init__(self, gateway: PaymentGateway, metrics: MetricsClient):
        self.gateway = gateway
        self.metrics = metrics
        self.logger = logging.getLogger(__name__)

    def process(self, payment: Payment) -> Result:
        self.logger.info(f"Processing payment {payment.id}")
        start = time.time()

        try:
            result = self.gateway.charge(payment)
            self.metrics.increment("payments.success")
            return result
        except GatewayError as e:
            self.metrics.increment("payments.failure")
            self.logger.error(f"Payment failed: {e}")
            raise
        finally:
            self.metrics.timing("payments.duration", time.time() - start)

# ❌ Bad: Untestable, no observability
def process_payment(payment):
    return requests.post(GATEWAY_URL, json=payment).json()
```

---


## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have:

- [ ] **Docker** (20.10+) and Docker Compose installed
- [ ] **Python** 3.11+ with pip
- [ ] **AWS CLI** configured with appropriate credentials
- [ ] **kubectl** installed and configured
- [ ] **Terraform** 1.5+ installed
- [ ] **Git** for version control

### Step 1: Clone the Repository

```bash
git clone https://github.com/samueljackson-collab/Portfolio-Project.git
cd Portfolio-Project/projects/3-kubernetes-cicd
```

### Step 2: Review the Documentation

```bash
# Read the project README
cat README.md

# Review available make targets
make help
```

### Step 3: Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your configuration
vim .env

# Validate configuration
make validate-config
```

### Step 4: Start Local Development

```bash
# Start all services with Docker Compose
make up

# Verify services are running
make status

# View logs
make logs

# Run tests
make test
```

### Step 5: Deploy to Cloud

```bash
# Initialize Terraform
cd terraform
terraform init

# Review planned changes
terraform plan -out=tfplan

# Apply infrastructure
terraform apply tfplan

# Deploy application
cd ..
make deploy ENV=staging
```

### Verification

```bash
# Check deployment health
make health

# Run smoke tests
make smoke-test

# View dashboards
open http://localhost:3000  # Grafana
```

---


## ⚙️ Operational Guide

### Monitoring & Alerting

| Metric Type | Tool | Dashboard |
|-------------|------|-----------|
| **Metrics** | Prometheus | Grafana `http://localhost:3000` |
| **Logs** | Loki | Grafana Explore |
| **Traces** | Tempo/Jaeger | Grafana Explore |
| **Errors** | Sentry | `https://sentry.io/org/project` |

### Key Metrics to Monitor

```promql
# Request latency (P99)
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
sum(rate(http_requests_total{status=~"5.."}[5m])) /
sum(rate(http_requests_total[5m]))

# Resource utilization
container_memory_usage_bytes / container_spec_memory_limit_bytes
```

### Common Operations

| Task | Command | When to Use |
|------|---------|-------------|
| View logs | `kubectl logs -f deploy/app` | Debugging issues |
| Scale up | `kubectl scale deploy/app --replicas=5` | Handling load |
| Rollback | `kubectl rollout undo deploy/app` | Bad deployment |
| Port forward | `kubectl port-forward svc/app 8080:80` | Local debugging |
| Exec into pod | `kubectl exec -it deploy/app -- bash` | Investigation |

### Runbooks

<details>
<summary><strong>🔴 High Error Rate</strong></summary>

**Symptoms:** Error rate exceeds 1% threshold

**Investigation:**
1. Check recent deployments: `kubectl rollout history deploy/app`
2. Review error logs: `kubectl logs -l app=app --since=1h | grep ERROR`
3. Check dependency health: `make check-dependencies`
4. Review metrics dashboard for patterns

**Resolution:**
- If recent deployment: `kubectl rollout undo deploy/app`
- If dependency failure: Check upstream service status
- If resource exhaustion: Scale horizontally or vertically

**Escalation:** Page on-call if not resolved in 15 minutes
</details>

<details>
<summary><strong>🟡 High Latency</strong></summary>

**Symptoms:** P99 latency > 500ms

**Investigation:**
1. Check traces for slow operations
2. Review database query performance
3. Check for resource constraints
4. Review recent configuration changes

**Resolution:**
- Identify slow queries and optimize
- Add caching for frequently accessed data
- Scale database read replicas
- Review and optimize N+1 queries
</details>

<details>
<summary><strong>🔵 Deployment Failure</strong></summary>

**Symptoms:** ArgoCD sync fails or pods not ready

**Investigation:**
1. Check ArgoCD UI for sync errors
2. Review pod events: `kubectl describe pod <pod>`
3. Check image pull status
4. Verify secrets and config maps exist

**Resolution:**
- Fix manifest issues and re-sync
- Ensure image exists in registry
- Verify RBAC permissions
- Check resource quotas
</details>

### Disaster Recovery

**RTO Target:** 15 minutes
**RPO Target:** 1 hour

```bash
# Failover to DR region
./scripts/dr-failover.sh --region us-west-2

# Validate data integrity
./scripts/dr-validate.sh

# Failback to primary
./scripts/dr-failback.sh --region us-east-1
```

---


## 🌍 Real-World Scenarios

These scenarios demonstrate how this project applies to actual business situations.

### Scenario: Critical Bug in Production

**Challenge:** Security vulnerability discovered in production, needs immediate fix

**Solution:** Emergency PR triggers fast-track pipeline, automated tests validate fix, ArgoCD deploys within minutes

---

### Scenario: Feature Flag Rollout

**Challenge:** Launch risky feature to 1% of users, expand if metrics look good

**Solution:** Canary deployment with automated metric analysis, progressive rollout controlled by GitOps

---



## 🔗 Related Projects

Explore these related projects that share technologies or concepts:

| Project | Description | Shared Tags |
|---------|-------------|-------------|
| [DevSecOps Pipeline](/projects/devsecops-pipeline) | Security-first CI pipeline integrating SAST, DAST,... | 1 |
| [MLOps Platform](/projects/mlops-platform) | End-to-end MLOps workflow for training, evaluating... | 1 |
| [Multi-Cloud Service Mesh](/projects/multi-cloud-service-mesh) | Istio service mesh spanning AWS and GKE clusters.... | 1 |
| [Advanced Kubernetes Operators](/projects/advanced-kubernetes-operators) | Custom resource operator built with Kopf.... | 1 |

---


## 📚 Resources

### Project Links

| Resource | Link |
|----------|------|
| 📂 Source Code | [GitHub Repository](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/3-kubernetes-cicd) |
| 📖 Documentation | [`projects/3-kubernetes-cicd/docs/`](projects/3-kubernetes-cicd/docs/) |
| 🐛 Issues | [Report bugs or request features](https://github.com/samueljackson-collab/Portfolio-Project/issues) |

### Recommended Reading

- [The Twelve-Factor App](https://12factor.net/)
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

### Community Resources

- Stack Overflow: Tag your questions appropriately
- Reddit: r/devops, r/aws, r/kubernetes
- Discord: Many technology-specific servers

---

<div align="center">

**Last Updated:** 2026-01-23 |
**Version:** 3.0 |
**Generated by:** Portfolio Wiki Content Generator

*Found this helpful? Star the repository!*

</div>
