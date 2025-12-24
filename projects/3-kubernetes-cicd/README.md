# Project 3: Kubernetes CI/CD Pipeline

Declarative delivery pipeline with GitHub Actions, ArgoCD, and progressive delivery strategies.

## Contents
- `pipelines/github-actions.yaml` — build, test, scan, and progressive delivery workflow.
- `pipelines/argocd-app.yaml` — GitOps application manifest.

## GitHub Actions workflow

The `portfolio-delivery` workflow now implements end-to-end quality gates:

- **Lint & schema validation**: `yamllint` plus `kubeconform` against `k8s/` manifests with strict mode enabled.
- **Unit tests**: Python toolchain bootstrapped from `requirements.txt` followed by `pytest` on `projects/3-kubernetes-cicd/tests`.
- **Image build & push**: Docker Buildx pushes the application image from `projects/3-kubernetes-cicd/Dockerfile`.
- **Security scans**: Trivy (HIGH/CRITICAL severities) and Dockle (CIS hardening) fail the pipeline on findings.
- **Progressive delivery**: ArgoCD sync + Argo Rollouts canary (default) or blue/green promotion with automated rollback on failure.

### Required secrets/vars

| Name | Type | Purpose |
| --- | --- | --- |
| `REGISTRY_HOST` | Secret | Container registry hostname (e.g., `ghcr.io`). |
| `REGISTRY_USERNAME` / `REGISTRY_PASSWORD` | Secret | Credentials for pushing images. |
| `REGISTRY_REPOSITORY` | Secret (optional) | Override repository path (defaults to `<owner>/<repo>`). |
| `KUBECONFIG_BASE64` | Secret | Base64-encoded kubeconfig for promotion steps. |
| `ARGOCD_SERVER` / `ARGOCD_AUTH_TOKEN` | Secret | API endpoint and token for ArgoCD CLI. |
| `ARGOCD_APP_NAME` | Secret | Target ArgoCD application to sync and monitor. |
| `ROLLOUT_NAME` | Secret | Argo Rollouts resource to promote (canary or blue/green). |
| `ROLLOUT_NAMESPACE` | Secret/Var | Namespace for the rollout (defaults to `default`). |
| `DEPLOY_STRATEGY` | Repository variable | Set to `canary` (default) or `blue-green`. |

### Canary vs. blue/green

- **Canary (default):** Sets the rollout image to the freshly built tag, gates at 20% traffic weight, and promotes to 100% after health verification.
- **Blue/green:** Updates the rollout image, promotes the green slot, and optionally waits on the service specified by `BLUE_GREEN_SERVICE_NAME` before cutover.

On any sync or promotion failure, the workflow triggers `argocd app rollback` to restore the last healthy revision.

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
