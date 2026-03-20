# Infrastructure as Code Standards

**Version:** 2.1 | **Owner:** Platform Engineering | **Last Updated:** 2026-01-10

---

## 1. Terraform Standards

### 1.1 Module Structure

Every reusable Terraform module must follow this structure:

```
modules/<name>/
├── main.tf          # Resources
├── variables.tf     # Input variables with descriptions + validations
├── outputs.tf       # Outputs with descriptions
├── versions.tf      # Required providers + version constraints
└── README.md        # Auto-generated via terraform-docs
```

### 1.2 Required Variable Attributes

```hcl
# GOOD — description, type, validation
variable "instance_type" {
  description = "EC2 instance type. Must be from approved list."
  type        = string
  default     = "t3.small"

  validation {
    condition     = contains(["t3.small", "t3.medium", "t3.large", "m5.large"], var.instance_type)
    error_message = "instance_type must be one of the approved types."
  }
}

# BAD — no description, no type, no validation
variable "instance_type" {}
```

### 1.3 Naming Convention

```
# Resources: <project>-<env>-<component>-<purpose>
resource "aws_s3_bucket" "portfolio_prod_assets_static" {}

# Locals: snake_case
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
```

### 1.4 State Management

- Remote state required in all non-local environments
- State bucket: versioned S3 + DynamoDB locking
- State files per environment, per component (not one monolithic state)

```hcl
terraform {
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "prod/networking/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-locks"
  }
}
```

### 1.5 Terraform Workflow

```bash
# Standard workflow — all steps required before apply
terraform fmt -check -recursive       # 1. Format check
terraform validate                    # 2. Syntax validation
tfsec .                               # 3. Security scan
terraform plan -out=tfplan            # 4. Plan review
terraform apply tfplan                # 5. Apply (from saved plan only)
```

---

## 2. Kubernetes / Helm Standards

### 2.1 Required Resource Limits

All Kubernetes workloads must define resource requests and limits:

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
```

### 2.2 Security Context

```yaml
# Required on all pods
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
```

### 2.3 Health Probes

Every deployment must define all three probes:

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
startupProbe:
  httpGet:
    path: /health/startup
    port: 8080
  failureThreshold: 30
  periodSeconds: 10
```

---

## 3. Docker Standards

### 3.1 Base Image Policy

| Runtime | Approved Base | Rationale |
|---------|--------------|-----------|
| Python | `python:3.11-slim` | Minimal attack surface |
| Node.js | `node:20-alpine` | Minimal, well-maintained |
| Go | `scratch` (with static binary) | Zero OS attack surface |
| Java | `eclipse-temurin:21-jre-alpine` | LTS, minimal |

### 3.2 Dockerfile Requirements

```dockerfile
# GOOD — all requirements met
FROM python:3.11-slim AS base

# Non-root user
RUN useradd --no-create-home --system appuser

WORKDIR /app

# Separate dependency install for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

USER appuser

# Explicit health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s CMD \
    python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Required in every Dockerfile:**
- Non-root user
- `COPY requirements.txt` before `COPY .` (layer cache optimisation)
- `HEALTHCHECK`
- Explicit `CMD` (not `ENTRYPOINT` for application containers)
- No secrets in build args or ENV
