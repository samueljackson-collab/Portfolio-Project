# Project 3: Kubernetes CI/CD Pipeline

Declarative delivery pipeline with GitHub Actions, ArgoCD, and progressive delivery strategies.

## Contents
- `pipelines/github-actions.yaml` — build, test, scan, and progressive delivery workflow.
- `pipelines/argocd-app.yaml` — GitOps application manifest.

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
