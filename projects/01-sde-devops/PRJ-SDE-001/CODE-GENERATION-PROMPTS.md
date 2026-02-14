# Multi-Variant Code Generation Prompts

Use these curated prompts to generate consistent artifacts across infrastructure, application services, and pipelines. Each variant specifies intent, constraints, and quality gates.

## Variant A: Terraform Module Expansion
```
You are extending the PRJ-SDE-001 Terraform stack. Create a reusable module that provisions <service> with:
- Inputs for region, tags, subnet_ids, security_group_ids
- Enforced encryption at rest and in transit
- CloudWatch log/metric integration
- Sensible defaults for production (no public endpoints, deletion protection enabled)
Output variables must expose ARNs and connection details. Include README usage and examples referencing existing VPC and ECS modules.
```

## Variant B: Application Service Scaffold
```
Generate a containerized Python/Node service named <service_name> that will run on ECS Fargate behind an ALB.
Requirements:
- Health check endpoint `/healthz` returning 200
- Structured JSON logging with correlation IDs
- Environment-driven DB connection strings (use AWS Secrets Manager pattern)
- Dockerfile optimized for small image (alpine/slim) and non-root user
- CI workflow steps for lint/test/build/push to ECR
- Include IaC snippet to wire the service into existing ALB target group and security groups
```

## Variant C: CI/CD Policy Enforcement
```
Design a GitHub Actions workflow for PRJ-SDE-001 that runs on pull requests and main merges.
Stages:
1) Static analysis (terraform fmt/validate, tflint, trivy for IaC)
2) Unit + integration tests with coverage thresholds
3) Terraform plan with cost estimate and comment back to PR
4) Security gates: dependency scan, secret scan, and OPA policy check
5) On main branch: apply to dev, run smoke tests, and gate prod apply on manual approval
Provide caching, failure notifications to Slack, and artifact uploads for plans and test reports.
```

## Variant D: Disaster Recovery Playbook Generator
```
Produce an automated DR procedure for PRJ-SDE-001.
- Terraform/CLI steps to recreate VPC, ECS, and RDS from latest backups/snapshots
- Traffic failover steps (Route53 health checks or ALB swap)
- Data validation checks post-restore
- Rollback plan if integrity checks fail
- Time-bound RTO/RPO targets and success criteria
Format as a runbook with commands and checkpoints.
```

## Variant E: Observability Dashboards
```
Create a CloudWatch dashboard JSON for PRJ-SDE-001 showing:
- ALB latency (p95), 4xx/5xx rates
- ECS service CPU/Mem utilization and task count
- RDS connections, CPU, disk queue depth, free storage
- Error budget burn rate and SLO attainment
- Log query widgets for key error patterns
Ensure dimensions target the existing cluster, service, and database identifiers.
```
