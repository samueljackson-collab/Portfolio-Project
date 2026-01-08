# Project 1: AWS Infrastructure Automation

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


## 📊 Portfolio Status Board

🟢 Done · 🟠 In Progress · 🔵 Planned

**Current Status:** 🟢 Done (Implemented)


This project provisions a production-ready AWS environment with multiple implementation paths so the portfolio can demonstrate infrastructure-as-code fluency across Terraform, the AWS CDK, and Pulumi.

## Live Deployment
| Detail | Value |
| --- | --- |
| Live URL | `https://1-aws-infrastructure-automation.staging.portfolio.example.com` |
| DNS | `1-aws-infrastructure-automation.staging.portfolio.example.com` → `CNAME portfolio-gateway.staging.example.net` |
| Deployment environment | Staging (AWS us-east-1, containerized services; IaC in `terraform/`, `cdk/`, or `pulumi/` for this project) |

### Deployment automation
- **CI/CD:** GitHub Actions [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) gates builds; [`.github/workflows/deploy-portfolio.yml`](../../.github/workflows/deploy-portfolio.yml) publishes the staging stack.
- **Manual steps:** Follow the project Quick Start/Runbook instructions in this README to build artifacts, apply IaC, and validate health checks.
- **Deployment status:** See [`DEPLOYMENT_STATUS.md`](DEPLOYMENT_STATUS.md) for live deployment tracking and verification steps.

### Monitoring
- **Prometheus:** `https://prometheus.staging.portfolio.example.com` (scrape config: `prometheus/prometheus.yml`)
- **Grafana:** `https://grafana.staging.portfolio.example.com` (dashboard JSON: `grafana/dashboards/*.json`)

### Live deployment screenshots
![Live deployment dashboard](../../assets/screenshots/live-deployment-placeholder.svg)

## Goals
- Launch a multi-AZ network foundation with private, public, and database subnets.
- Provide a managed Kubernetes control plane, managed worker nodes, and autoscaling policies.
- Supply a resilient PostgreSQL database tier with routine backups and monitoring toggles.
- Front application workloads with an Application Load Balancer and auto-scaling group.
- Deliver static assets via S3 with global distribution through CloudFront.
- Offer interchangeable infrastructure definitions so the same outcome can be reached with different toolchains.

## Contents
- `terraform/` — Primary IaC implementation using community modules and environment-specific variables (VPC, ALB, Auto Scaling Group, EKS, RDS, S3 + CloudFront).
- `cdk/` — Python-based AWS CDK app that mirrors the Terraform footprint and highlights programmatic constructs.
- `pulumi/` — Pulumi project using Python for multi-cloud-friendly infrastructure authoring.
- `scripts/` — Helper scripts for planning, deployment, validation, and teardown workflows.

Each implementation aligns with the runbooks described in the Wiki.js guide so the documentation, automation, and validation steps can be exercised end-to-end.

## Footprint Highlights
- Internet-facing Application Load Balancer with target group health checks and deregistration protections.
- Auto Scaling Group for web workloads with Amazon Linux 2023 launch template and SSM access.
- Managed EKS control plane and managed node groups for container orchestration.
- RDS PostgreSQL in isolated database subnets with automated backups.
- Static asset delivery via S3, secured by Origin Access Identity and cached globally by CloudFront.


## Code Generation Prompts

This section contains AI-assisted code generation prompts that can help you recreate or extend project components. These prompts are designed to work with AI coding assistants like Claude, GPT-4, or GitHub Copilot.

### Infrastructure as Code

#### 1. Terraform Module
```
Create a Terraform module for deploying a highly available VPC with public/private subnets across 3 availability zones, including NAT gateways and route tables
```

#### 2. CloudFormation Template
```
Generate a CloudFormation template for an Auto Scaling Group with EC2 instances behind an Application Load Balancer, including health checks and scaling policies
```

#### 3. Monitoring Integration
```
Write Terraform code to set up CloudWatch alarms for EC2 CPU utilization, RDS connections, and ALB target health with SNS notifications
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
