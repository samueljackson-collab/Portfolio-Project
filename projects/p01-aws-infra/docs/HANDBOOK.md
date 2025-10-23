# P01 · AWS Infrastructure Automation — Engineering Handbook

> **Purpose:** Provide a deep technical reference for architects, engineers, and operators building and maintaining the AWS landing zone delivered in Project P01. This handbook explains the architecture, module design, security posture, observability, deployment workflows, and governance required to run the platform in production.

---
## 1. Executive Summary
- **Business Outcome:** Deliver a scalable, secure foundation for customer-facing services with 99.95% uptime SLO and cost visibility between $416–$656/month.  
- **Scope:** Multi-account AWS organization (landing zone, shared services, workloads) automated with Terraform, supporting blue/green and multi-environment deployments.  
- **Key Differentiators:** Opinionated Terraform modules, policy-as-code guardrails, automated operations scripts, and comprehensive documentation (handbook, runbook, playbook).  

---
## 2. Architecture Overview
### 2.1 Logical Layout
- **Network layer:** Dedicated VPC per environment with public, private, and data subnets across three AZs. Ingress handled by CloudFront + ALB, egress via NAT gateways.  
- **Compute layer:** EC2 Auto Scaling Groups (optionally ECS) behind ALB, patched via SSM Maintenance Windows.  
- **Data layer:** Amazon RDS PostgreSQL (Multi-AZ) and S3 for object storage. Backups replicate to secondary region.  
- **Edge & Security:** AWS WAF, AWS Shield, CloudFront edge caching, ACM certificates, Secrets Manager for credentials, KMS CMKs for encryption.  

### 2.2 Component Diagram
See the project README for a rendered Mermaid diagram and `docs/diagrams/` for editable sources (draw.io + Mermaid).  

### 2.3 Module Interactions
- `network` module creates VPC, subnets, IGW, NAT, route tables, and security group baselines.  
- `compute` module consumes subnet IDs and security groups to provision Launch Templates, ASGs, ALB, Target Groups, and listener rules.  
- `storage` module provisions RDS, S3 buckets, and optional CloudFront distributions with origin access identity (OAI).  

---
## 3. Infrastructure as Code
### 3.1 Repository Layout
```
infra/
├── environments/
│   └── prod/
│       ├── backend.tf
│       ├── main.tf
│       ├── outputs.tf
│       ├── terraform.tfvars.example
│       └── variables.tf
└── modules/
    ├── network/
    ├── compute/
    └── storage/
```

### 3.2 Module Standards
- Version all modules via Git tags and semantic versioning.  
- Inputs/outputs documented in `README.md` (future enhancement).  
- Variables use `validation` blocks and sensible defaults while supporting overrides.  
- Implement tagging strategy (`Environment`, `CostCenter`, `Owner`, `Compliance`).  

### 3.3 Development Workflow
1. Branch from `main` using naming convention `feature/<description>`.  
2. Run `terraform fmt`, `tflint`, and `tfsec` locally.  
3. Commit changes with conventional commits (`feat:`, `fix:`, `docs:`).  
4. Open PR — GitHub Actions executes validation suite (fmt, validate, tflint, tfsec, Terratest, integration script).  
5. Peer review focuses on drift detection, security posture, and tagging compliance.  
6. Merge into `main`; pipeline auto-tags module version and updates documentation changelog.  

---
## 4. Security Architecture
### 4.1 Identity & Access Management
- **Roles:** `TerraformProvisioner`, `OperationsEngineer`, `ReadOnlyAuditor`, `BreakGlass`.  
- **Access Controls:** Enforced MFA, session duration ≤ 1 hour, AWSSSO or IAM Identity Center groups mapped to roles.  
- **Policy Guardrails:** SCPs blocking root access keys, restricting regions, enforcing TLS 1.2. Access Analyzer integrated with CI to detect overly permissive IAM policies before merge.  

### 4.2 Data Protection
- All data stores encrypted with customer-managed KMS CMKs.  
- Secrets stored in Secrets Manager with rotation Lambda (cron: daily).  
- TLS enforced via ACM certificates (90-day rotation).  
- Backups encrypted and replicated to disaster recovery region.  

### 4.3 Network Security
- Security groups follow least privilege: ALB only exposes ports 80/443 to the internet, compute nodes only accept ALB traffic, RDS only accepts compute subnet traffic.  
- NACLs provide stateless deny rules for known malicious ranges.  
- VPC Flow Logs shipped to CloudWatch Logs with retention 400 days.  

---
## 5. Observability & Operations
### 5.1 Metrics & Dashboards
- **Golden Signals:** latency (p95), traffic (requests/min), errors (5xx rate), saturation (CPU, memory).  
- CloudWatch dashboards per service with autoscaling insights and RDS performance metrics.  
- Prometheus exporters (node_exporter, cloudwatch_exporter) scrape metrics for Grafana dashboards.  

### 5.2 Logging & Tracing
- Application logs to CloudWatch Logs → Kinesis Firehose → S3 + Athena partitions.  
- Structured JSON logging with correlation IDs and trace propagation headers.  
- Optional X-Ray integration for distributed tracing.  

### 5.3 Alerting Strategy
- Severity mapping: P1 (critical outage) triggers PagerDuty & Slack; P2 (degraded) Slack + ticket; P3 (warning) Jira backlog; P4 (informational) metrics only.  
- Burn-rate alerts for error budgets (1h & 6h windows).  

---
## 6. Cost Management
- Baseline monthly cost projection ($416–$656) covers compute (ASG with t3.medium), RDS (db.m6g.large Multi-AZ), NAT gateways, CloudFront, CloudWatch logs.  
- Implement AWS Budgets with 80% / 100% / 110% alerts to Slack & email.  
- Use Savings Plans for steady-state compute and Reserved Instances for RDS after observing usage.  
- Scheduled reports: weekly cost trend (Cost Explorer API), monthly rightsizing recommendations (Compute Optimizer).  

---
## 7. Deployment Guide
1. Configure AWS CLI credentials and bootstrap Terraform remote state bucket + DynamoDB table.  
2. Copy `terraform.tfvars.example` → `terraform.tfvars`; populate environment-specific values (CIDR blocks, key pair, domain, etc.).  
3. Run `terraform init` with backend config, then `terraform plan`.  
4. Acquire approval, then `terraform apply`.  
5. Post-deploy validation: run health-check scripts, confirm ALB target health, verify RDS connectivity, ensure CloudWatch alarms are `OK`.  
6. Update change log, notify stakeholders, and schedule DR drill if major changes occurred.  

---
## 8. Troubleshooting Guide (Extract)
| Symptom | Likely Cause | Resolution |
| --- | --- | --- |
| ALB shows unhealthy targets | Security group mismatch or failing health endpoint | Confirm SG rules, inspect `/healthz` logs, redeploy ASG. |
| Terraform apply fails with state lock | Stale lock in DynamoDB | Run `terraform force-unlock <ID>` after verifying no other deploy in progress. |
| RDS connection timeouts | Incorrect subnet group or route table | Verify RDS subnet group includes private subnets; ensure NACL allows DB port. |
| Elevated 5xx errors | App release regression | Trigger rollback using previous launch template version (documented in Playbook P1-INC-004). |

---
## 9. Compliance & Governance
- CIS AWS Foundations Benchmarks integrated into CI via `cfn-nag`/`terraform-compliance`.  
- Change management tracked with Jira tickets referencing runbook steps and approvals.  
- Quarterly security reviews covering IAM, network ACLs, and encryption keys.  
- Data residency controls documented for GDPR/CCPA alignment.  

---
## 10. Future Enhancements
- Add EKS module to support container workloads.  
- Extend runbooks with chaos engineering game days.  
- Integrate AWS Control Tower for standardized account vending.  
- Automate drift detection with AWS Config + Terraform Cloud notifications.  

---
## 11. Appendices
- **Appendix A:** Module input/output tables (auto-generated via `terraform-docs`).  
- **Appendix B:** Cost calculator spreadsheet (see `/projects/p01-aws-infra/assets/cost-model.xlsx`).  
- **Appendix C:** Diagram sources (Mermaid + draw.io).  
- **Appendix D:** API references for automation scripts (`aws`, `jq`, `curl`).  

---
## 12. Revision History
| Version | Date | Author | Notes |
| --- | --- | --- | --- |
| 3.0.0 | 2025-10-06 | Samuel Jackson | Initial enterprise release with handbook, runbook, playbook, and Terraform modules. |
| 3.1.0 | _Planned_ | _You_ | Add cost anomaly detection workflows and AWS Backup support. |

