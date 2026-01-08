# Project 4: DevSecOps Pipeline

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


## 📊 Portfolio Status Board

🟢 Done · 🟠 In Progress · 🔵 Planned

**Current Status:** 🟢 Done (Implemented)


Security-first CI pipeline with SBOM generation, container scanning, and policy checks.

## Live Deployment
| Detail | Value |
| --- | --- |
| Live URL | `https://4-devsecops.staging.portfolio.example.com` |
| DNS | `4-devsecops.staging.portfolio.example.com` → `CNAME portfolio-gateway.staging.example.net` |
| Deployment environment | Staging (AWS us-east-1, containerized services; IaC in `pipelines/` for this project) |

### Deployment automation
- **CI/CD:** GitHub Actions [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) gates builds; [`.github/workflows/deploy-portfolio.yml`](../../.github/workflows/deploy-portfolio.yml) publishes the staging stack.
- **Manual steps:** Follow the project Quick Start/Runbook instructions in this README to build artifacts, apply IaC, and validate health checks.

### Monitoring
- **Prometheus:** `https://prometheus.staging.portfolio.example.com` (scrape config: `prometheus/prometheus.yml`)
- **Grafana:** `https://grafana.staging.portfolio.example.com` (dashboard JSON: `grafana/dashboards/*.json`)

### Live deployment screenshots
![Live deployment dashboard](../../assets/screenshots/live-deployment-placeholder.svg)

## Contents
- `pipelines/github-actions.yaml` — orchestrates build, security scanning, and deployment gates.


## Code Generation Prompts

This section contains AI-assisted code generation prompts that can help you recreate or extend project components. These prompts are designed to work with AI coding assistants like Claude, GPT-4, or GitHub Copilot.

### Security Automation

#### 1. IAM Policy
```
Create an AWS IAM policy that follows principle of least privilege for a Lambda function that needs to read from S3, write to DynamoDB, and publish to SNS
```

#### 2. Security Scanning
```
Generate a Python script that scans Docker images for vulnerabilities using Trivy, fails CI/CD if critical CVEs are found, and posts results to Slack
```

#### 3. Compliance Checker
```
Write a script to audit AWS resources for CIS Benchmark compliance, checking security group rules, S3 bucket policies, and IAM password policies
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
