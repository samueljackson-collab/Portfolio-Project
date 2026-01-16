# Project 4: DevSecOps Pipeline

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).

## 📊 Portfolio Status Board

🟢 Done · 🟠 In Progress · 🔵 Planned

**Current Status:** 🟢 Done (Implemented)

Security-first CI/CD pipeline with comprehensive security scanning, SBOM generation, container scanning, OPA policy validation, and automated security dashboards.

## Overview

This project implements a complete DevSecOps pipeline that integrates security at every stage of the software development lifecycle. It includes:

- **SAST** (Static Application Security Testing) with Semgrep, Bandit, and CodeQL
- **Secrets Detection** with Gitleaks and TruffleHog
- **SCA** (Software Composition Analysis) with Trivy
- **SBOM Generation** with Syft
- **IaC Security** with Checkov and OPA policies
- **Container Security** with Trivy and Dockle
- **Automated Security Dashboard** generation

## Project Structure

```
projects/4-devsecops/
├── .github/workflows/
│   └── security-pipeline.yml    # Main security CI pipeline
├── sample-app/
│   ├── vulnerable.py            # Intentionally vulnerable app (for testing)
│   ├── secure.py                # Secure implementation
│   ├── requirements.txt
│   └── README.md                # Sample app documentation
├── policies/
│   ├── kubernetes.rego          # OPA policies for Kubernetes
│   └── terraform.rego           # OPA policies for Terraform
├── scripts/
│   └── generate-dashboard.py    # Security dashboard generator
├── templates/
│   └── dashboard.html           # Dashboard HTML template
├── k8s/
│   └── deployment.yaml          # Secure Kubernetes deployment
├── terraform/
│   └── main.tf                  # Secure AWS infrastructure
└── README.md                    # This file
```

## Security Pipeline

### CI Pipeline Jobs

| Job | Tools | Purpose |
|-----|-------|---------|
| `sast-scan` | Semgrep, Bandit, CodeQL | Find vulnerabilities in application code |
| `secrets-scan` | Gitleaks, TruffleHog | Detect hardcoded secrets and credentials |
| `dependency-scan` | Trivy | Find CVEs in dependencies |
| `sbom-generation` | Syft | Generate Software Bill of Materials |
| `iac-scan` | Checkov, Trivy Config | Scan infrastructure as code |
| `policy-check` | OPA, Conftest | Validate against security policies |
| `build-and-scan-container` | Trivy, Dockle | Scan container images |
| `generate-dashboard` | Python script | Create visual security report |
| `security-gate` | Custom | Block deployments with critical issues |

### Running the Pipeline

The pipeline runs automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main`
- Daily at 2 AM UTC (scheduled)
- Manual trigger via workflow_dispatch

### Viewing Results

1. **GitHub Security Tab**: SARIF results uploaded automatically
2. **Artifacts**: Download `security-dashboard` artifact for HTML report
3. **PR Comments**: Summary posted automatically on pull requests

## Sample Application

The `sample-app/` directory contains two versions of a Flask application:

### vulnerable.py (For Testing Only)

Demonstrates common security vulnerabilities:
- SQL Injection (CWE-89)
- Command Injection (CWE-78)
- XSS (CWE-79)
- Hardcoded Credentials (CWE-798)
- Insecure Deserialization (CWE-502)
- Path Traversal (CWE-22)
- Weak Cryptography (CWE-327)
- XXE (CWE-611)
- SSRF (CWE-918)

### secure.py (Best Practices)

Shows secure implementations:
- Parameterized queries
- Input validation
- Secure password hashing (PBKDF2)
- Content Security Policy headers
- Rate limiting
- Authentication/authorization
- defusedxml for XXE protection

### Running Locally

```bash
cd sample-app

# Install dependencies
pip install -r requirements.txt

# Run vulnerable app (testing only!)
python vulnerable.py

# Run secure app
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
python secure.py
```

See [sample-app/README.md](./sample-app/README.md) for detailed scanning instructions.

## OPA Policies

### Kubernetes Policies (`policies/kubernetes.rego`)

Enforces security best practices:
- Deny privileged containers
- Require resource limits
- Deny running as root
- Deny host networking/PID/IPC
- Block dangerous capabilities
- Require health probes
- Deny hostPath volumes
- Require image tags (no `latest`)

### Terraform Policies (`policies/terraform.rego`)

AWS security validation:
- S3 encryption and public access blocks
- RDS encryption and private subnets
- EBS volume encryption
- Security group rules validation
- IAM least privilege checks
- CloudTrail logging requirements
- KMS key rotation

### Using Policies

```bash
# Kubernetes validation
opa eval --data policies/kubernetes.rego \
  --input k8s/deployment.yaml \
  "data.kubernetes.deny"

# Terraform validation (requires plan JSON)
terraform plan -out=tfplan
terraform show -json tfplan > tfplan.json
opa eval --data policies/terraform.rego \
  --input tfplan.json \
  "data.terraform.deny"

# Using Conftest
conftest test k8s/ --policy policies/
conftest test terraform/ --policy policies/
```

## Security Dashboard

### Generating the Dashboard

```bash
# After running scans, generate dashboard
python scripts/generate-dashboard.py \
  --scan-dir ./scan-results \
  --output security-dashboard.html \
  --json-output security-report.json \
  --commit $(git rev-parse HEAD) \
  --branch $(git branch --show-current)
```

### Dashboard Features

- Summary metrics (Critical, High, Medium, Low)
- Tool-by-tool breakdown
- All findings table with severity
- Software Bill of Materials display
- Color-coded status indicators

### Supported Scan Formats

The dashboard parser supports:
- Semgrep JSON
- Bandit JSON
- Gitleaks JSON
- Trivy JSON
- Syft SBOM (SPDX/CycloneDX)
- Checkov JSON

## Infrastructure as Code

### Kubernetes (`k8s/deployment.yaml`)

Secure deployment with:
- Non-root containers
- Read-only root filesystem
- Resource limits
- Security contexts
- Network policies
- Pod disruption budgets
- Horizontal pod autoscaler

### Terraform (`terraform/main.tf`)

AWS infrastructure with:
- VPC with private subnets
- Encrypted S3 buckets
- Encrypted RDS with multi-AZ
- KMS key rotation
- CloudTrail logging
- Security groups with minimal access

## Customizing Policies

### Adding New Kubernetes Rules

```rego
# In policies/kubernetes.rego
deny contains msg if {
    # Your custom rule logic
    input.kind == "Deployment"
    # ... conditions ...
    msg := "Custom: Your error message"
}
```

### Adding New Terraform Rules

```rego
# In policies/terraform.rego
deny contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_your_resource")
    values := get_planned_values(resource)
    # ... validation logic ...
    msg := sprintf("Issue with %s", [resource.address])
}
```

## Failing on Critical Issues

To fail the pipeline when critical vulnerabilities are found, uncomment the exit line in the security-gate job:

```yaml
# In security-pipeline.yml, security-gate job
if [ "$CRITICAL" -gt "0" ]; then
  echo "::error::Security gate failed"
  exit 1  # Uncomment this line
fi
```

## Live Deployment
- **Deployment record:** [DEPLOYMENT_STATUS.md](./DEPLOYMENT_STATUS.md)
- **Pipeline dashboard:** https://devsecops.example.com
- **SBOM index:** https://devsecops.example.com/sbom
- **Verification endpoint:** https://devsecops.example.com/healthz

### Verification steps
```bash
curl -fsSL https://devsecops.example.com/healthz
curl -fsSL https://devsecops.example.com/sbom
```

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [Open Policy Agent](https://www.openpolicyagent.org/docs/)
- [Semgrep Rules](https://semgrep.dev/explore)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Checkov Policies](https://www.checkov.io/5.Policy%20Index/all.html)

## License

MIT
