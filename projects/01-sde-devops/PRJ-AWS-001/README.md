# PRJ-AWS-001 · AWS Three-Tier Terraform Platform

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../../DOCUMENTATION_INDEX.md).


Production-ready AWS landing zone for a highly available three-tier web application. The project highlights enterprise patterns including secure network segmentation, autoscaling compute, managed database services, observability, disaster recovery, and cost governance.

## Highlights
- **Fully modular Terraform** structure with reusable networking, compute, database, security, monitoring, and storage layers.
- **Environment parity** across dev, staging, and production with remote state, validation scripts, and deployment automation.
- **Documentation-first** approach providing architecture diagrams, deployment instructions, operations runbooks, DR plan, and cost optimization strategies.

## Repository Layout
```
projects/01-sde-devops/PRJ-AWS-001/
├── terraform
│   ├── environments/{dev,staging,prod}
│   ├── modules/{networking,compute,database,security,monitoring,storage}
│   ├── global/{iam,route53,s3}
│   └── scripts
├── docs
│   ├── *.md
│   └── diagrams/*.md
├── tests/{integration,validation}
└── README.md
```

## Getting Started
1. Install Terraform >= 1.5 and AWS CLI v2.
2. Populate `terraform/environments/<env>/terraform.tfvars` with project-specific values (account IDs, domain names, instance types, etc.).
3. Configure the backend S3 bucket and DynamoDB lock table described in `terraform/environments/<env>/backend.tf`.
4. Run `terraform init`, `terraform validate`, and `terraform plan` from the desired environment folder.
5. Use helper scripts in `terraform/scripts/` for deploy/destroy/validate/cost estimation workflows.

## Automation Scripts
- `deploy.sh` – Wrapper that runs `terraform init`, `plan`, and `apply` with consistent tagging and cost-estimate logging.
- `destroy.sh` – Destroys an environment with additional prompts and safety checks.
- `validate.sh` – Runs `terraform fmt`, `validate`, tfsec (if installed), and unit tests under `tests/`.
- `cost-estimate.sh` – Calls `infracost` (if available) with sensible defaults and exports JSON for reporting.

## Documentation Package
Refer to the `docs/` folder for:
- Architecture explanation, diagrams, and data flow narratives.
- Deployment guide with bootstrap instructions.
- Operations runbook covering monitoring, alerting, and routine maintenance.
- Disaster recovery and cost-optimization strategies.

## Testing Strategy
- **Validation tests** assert Terraform configuration quality (linting, `terraform validate`).
- **Integration tests** (placeholder) will leverage Terratest or similar frameworks to deploy ephemeral stacks and verify networking, autoscaling, and monitoring behaviors.

## Roadmap
- Add Terratest suites for networking and compute modules.
- Expand compute module with ECS/Fargate and EC2 ASG blueprints.
- Integrate GitHub Actions pipeline for CI/CD, policy checks, and security scanning.
