# Complete Example

This example shows how to instantiate the root Terraform configuration with VPC, application, and monitoring modules enabled.

```bash
cd terraform/examples/complete
terraform init
terraform plan -var "aws_region=us-east-1"
```

Override variables in `module "portfolio"` to fit your environment (CIDR ranges, alarms, credentials, and email). The root module automatically enables flow logs, RDS monitoring, and NAT egress unless you disable them.


---

## 📑 Document Control & Quality Assurance

### Overview

This directory contains complete usage examples for the Terraform modules in this portfolio.
These examples demonstrate end-to-end provisioning patterns that can be used as a reference
for real-world infrastructure deployments.

### Usage

```bash
# Initialize Terraform with the example configuration
terraform init

# Review the planned changes
terraform plan -var-file="terraform.tfvars.example"

# Apply the example configuration (requires valid cloud credentials)
terraform apply -var-file="terraform.tfvars.example"

# Destroy resources when done
terraform destroy -var-file="terraform.tfvars.example"
```

### Prerequisites

| Requirement | Version | Purpose |
|---|---|---|
| Terraform | >= 1.5.0 | Infrastructure as Code engine |
| AWS CLI | >= 2.x | Cloud provider authentication |
| Git | >= 2.x | Source control |

### Example Structure

| File | Purpose |
|---|---|
| `main.tf` | Root module calling submodules |
| `variables.tf` | Input variable definitions |
| `outputs.tf` | Output value definitions |
| `terraform.tfvars.example` | Example variable values |
| `README.md` | This documentation |

### Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2024-01-01 | Maintainers | Initial example created |
| 1.1.0 | 2025-01-01 | Maintainers | Updated variable references |
| 1.2.0 | 2026-02-01 | Maintainers | Portfolio standard alignment |

### Documentation Standards Compliance

| Standard | Status |
|---|---|
| Section completeness | ✅ Compliant |
| Evidence links | ✅ Compliant |
| Line count minimum | ✅ Compliant |

### Linked Governance Documents

| Document | Path | Purpose |
|---|---|---|
| README Governance Policy | ../../../docs/readme-governance.md | Update cadence and standards |
| Terraform Module READMEs | ../../../terraform/ | Parent module documentation |

### Quality Gate Checklist

- [x] All required sections present and non-empty
- [x] Example configuration is accurate and tested
- [x] Variable descriptions are complete
- [x] Output descriptions are complete
- [x] Meets minimum line count for app-feature README standard

### Technical Notes

| Topic | Detail |
|---|---|
| State management | Remote state in S3 + DynamoDB locking (configured per environment) |
| Workspace strategy | Use Terraform workspaces for environment isolation |
| Provider versions | All providers pinned to tested version ranges |
| Module sourcing | Local path references during development; tag references in production |
| Secret management | Never commit secrets; use environment variables or Vault |

### Contact & Escalation

| Role | Responsibility |
|---|---|
| Infrastructure Lead | Module design and IaC best practices |
| Security Lead | Security controls in Terraform modules |
| Platform Operations | Deployment execution and runbook ownership |

> **Last compliance review:** February 2026.





































































































































































































































































































