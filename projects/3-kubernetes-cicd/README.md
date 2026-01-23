# Project 3: Kubernetes CI/CD Pipeline

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


## Live Deployment
| Detail | Value |
| --- | --- |
| Live URL | `https://3-kubernetes-cicd.staging.portfolio.example.com` |
| DNS | `3-kubernetes-cicd.staging.portfolio.example.com` → `CNAME portfolio-gateway.staging.example.net` |
| Deployment environment | Staging (AWS us-east-1, containerized services; IaC in `terraform/`, `infra/`, or `deploy/` for this project) |

### Deployment automation
- **CI/CD:** GitHub Actions [`/.github/workflows/ci.yml`](../../.github/workflows/ci.yml) gates builds; [`/.github/workflows/deploy-portfolio.yml`](../../.github/workflows/deploy-portfolio.yml) publishes the staging stack.
- **Manual steps:** Follow the project Quick Start/Runbook instructions in this README to build artifacts, apply IaC, and validate health checks.

### Monitoring
- **Prometheus:** `https://prometheus.staging.portfolio.example.com` (scrape config: `prometheus/prometheus.yml`)
- **Grafana:** `https://grafana.staging.portfolio.example.com` (dashboard JSON: `grafana/dashboards/*.json`)

### Live deployment screenshots
Live deployment dashboard screenshot stored externally.


## 📊 Portfolio Status Board

🟢 Done · 🟠 In Progress · 🔵 Planned

**Current Status:** 🟢 Done (Implemented)

---

## 📋 Overview

A production-ready CI/CD pipeline for deploying containerized applications to Kubernetes, featuring:

- **Flask REST API** with health checks, metrics, and database connectivity
- **GitHub Actions** for automated testing, building, and deployment
- **ArgoCD** for GitOps-based continuous delivery
- **Argo Rollouts** for canary deployments (10% → 30% → 60% → 100%)
- **Security scanning** with Trivy (CVE detection) and Dockle (container best practices)
- **Kustomize** for environment-specific configurations

## 🚀 Quick Start

### Run Locally

```bash
# Navigate to project directory
cd projects/3-kubernetes-cicd

# Install dependencies
pip install -r app/requirements.txt

# Initialize database (optional)
python app/database.py

# Run the application
python app/main.py

# Test endpoints
curl http://localhost:8080/health
curl http://localhost:8080/api/v1/status
curl http://localhost:8080/api/v1/config
```

### Run with Docker

```bash
# Build image
docker build -t k8s-cicd-demo .

# Run container
docker run -p 8080:8080 k8s-cicd-demo

# Test
curl http://localhost:8080/health
```

### Deploy to Kubernetes

```bash
# Using Kustomize
kubectl apply -k k8s/base

# Wait for deployment
kubectl rollout status deployment/k8s-cicd-demo

# Run smoke tests
./scripts/smoke-test.sh http://localhost:8080
```

## 📁 Project Structure

```
projects/3-kubernetes-cicd/
├── app/                          # Flask application
│   ├── main.py                   # Main application with API endpoints
│   ├── database.py               # SQLAlchemy models and CRUD operations
│   └── requirements.txt          # Python dependencies
├── k8s/                          # Kubernetes manifests
│   ├── base/                     # Base Kustomize configuration
│   │   ├── deployment.yaml       # Standard deployment
│   │   ├── rollout.yaml          # Argo Rollouts (canary)
│   │   ├── service.yaml          # ClusterIP service
│   │   ├── ingress.yaml          # Ingress configuration
│   │   ├── hpa.yaml              # Horizontal Pod Autoscaler
│   │   ├── networkpolicy.yaml    # Network security policies
│   │   ├── secret.yaml           # Secrets template
│   │   └── kustomization.yaml    # Kustomize config
│   └── overlays/                 # Environment-specific overlays
│       └── production/           # Production configuration
├── .github/workflows/
│   └── ci-cd.yaml                # GitHub Actions pipeline
├── scripts/
│   ├── smoke-test.sh             # Post-deployment smoke tests
│   └── load-test.py              # Locust load testing
├── argocd/
│   └── application.yaml          # ArgoCD application manifest
├── tests/                        # Test suite
├── Dockerfile                    # Multi-stage Docker build
└── README.md                     # This file
```

## 🔌 API Endpoints

### Health & Status

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Liveness probe - returns health status |
| `/ready` | GET | Readiness probe - checks if app is ready |
| `/metrics` | GET | Prometheus-format metrics |
| `/api/v1/status` | GET | Application status, version, and system info |
| `/api/v1/config` | GET | Non-sensitive configuration settings |

### Core API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home endpoint with pod info |
| `/api/info` | GET | Application metadata |
| `/api/echo` | POST | Echo back JSON payload |

### Tasks API (Database Demo)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/tasks` | GET | List all tasks |
| `/api/v1/tasks` | POST | Create a new task |
| `/api/v1/tasks/<id>` | GET | Get task by ID |
| `/api/v1/tasks/<id>` | PUT | Update task |
| `/api/v1/tasks/<id>` | DELETE | Delete task |

### Example Requests

```bash
# Get application status
curl http://localhost:8080/api/v1/status | jq

# Get configuration
curl http://localhost:8080/api/v1/config | jq

# Create a task
curl -X POST http://localhost:8080/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Deploy to production", "priority": "high"}'

# List tasks
curl http://localhost:8080/api/v1/tasks | jq
```

## Contents
- `pipelines/github-actions.yaml` — build, test, scan, and progressive delivery workflow.
- `pipelines/argocd-app.yaml` — GitOps application manifest.
- `assets/` — sanitized pipeline screenshots and log summaries.

## Evidence Assets
- [Assets Index](./assets/README.md)
- [Release Evidence Pack](./evidence/release-evidence.md)

## GitHub Actions Workflow
The `portfolio-delivery` workflow enforces validation, security, and progressive deployment stages:

1. **Lint & Validate** — `yamllint` plus `kubeconform` schema validation fails the build on YAML or Kubernetes schema errors.
2. **Unit Tests** — Installs Python 3.11 dependencies (via `requirements.txt` when present) and executes `pytest`.
3. **Build & Push** — Builds the container image and pushes both `latest` and SHA tags to the configured registry.
4. **Image Security** — Runs Trivy (fail on HIGH/CRITICAL) and Dockle (fail on CIS/Owasp findings). Any findings fail the pipeline.
5. **Progressive Delivery** — Syncs manifests through Argo CD, then drives a canary rollout by default (or blue/green when `DEPLOY_STRATEGY=blue-green`). Health checks and rollback steps enforce safe promotion.

### Required Secrets & Inputs
Configure these repository secrets/variables for the workflow to succeed:

| Name | Type | Purpose |
| ---- | ---- | ------- |
| `REGISTRY_URL` | Secret | Registry hostname (e.g., `ghcr.io/owner`). |
| `REGISTRY_USERNAME` / `REGISTRY_PASSWORD` | Secrets | Credentials for `docker/login-action`. |
| `IMAGE_NAME` | Secret | Repository/image name (e.g., `portfolio/api`). |
| `KUBECONFIG_B64` | Secret | Base64-encoded kubeconfig for validation and rollouts. |
| `ARGOCD_SERVER` / `ARGOCD_AUTH_TOKEN` | Secrets | Endpoint and token for Argo CD CLI login. |
| `ARGOCD_APP_NAME` | Secret | Target Argo CD application name. |
| `ARGOCD_NAMESPACE` | Secret | Namespace containing the rollout. |
| `ROLLOUT_NAME` | Secret | Argo Rollouts resource to drive canary/blue-green promotion. |
| `DEPLOY_STRATEGY` | Repository variable (optional) | `canary` (default) or `blue-green` to align promotion steps with release strategy. |

### Failure & Rollback Behavior
- **Lint/Test/Scan**: Any validation, test, Trivy, or Dockle failure stops the pipeline.
- **Deployment**: Argo CD sync failures trigger `argocd app rollback` and Argo Rollouts rollback to the prior stable ReplicaSet.
- **Progressive Delivery**: Canary promotions watch rollout health and block until steady; blue/green promotions gate traffic switching with status checks.


## Code Generation Prompts

This section contains AI-assisted code generation prompts that can help you recreate or extend project components. These prompts are designed to work with AI coding assistants like Claude, GPT-4, or GitHub Copilot.

### Kubernetes Resources

#### 1. Deployment Manifest
```
Create a Kubernetes Deployment manifest for a microservice with 3 replicas, resource limits (500m CPU, 512Mi memory), readiness/liveness probes, and rolling update strategy
```

#### 2. Helm Chart
```
Generate a Helm chart for deploying a web application with configurable replicas, ingress, service, and persistent volume claims, including values for dev/staging/prod environments
```

#### 3. Custom Operator
```
Write a Kubernetes operator in Go that watches for a custom CRD and automatically creates associated ConfigMaps, Secrets, and Services based on the custom resource spec
```

### How to Use These Prompts

1. **Copy the prompt** from the code block above
2. **Customize placeholders** (replace [bracketed items] with your specific requirements)
3. **Provide context** to your AI assistant about:
   - Your development environment and tech stack
   - Existing code patterns and conventions in this project
   - Any constraints or requirements specific to your use case
4. **Review and adapt** the generated code before using it
5. **Test thoroughly** and adjust as needed for your specific scenario

### Best Practices

- Always review AI-generated code for security vulnerabilities
- Ensure generated code follows your project's coding standards
- Add appropriate error handling and logging
- Write tests for AI-generated components
- Document any assumptions or limitations
- Keep sensitive information (credentials, keys) in environment variables
