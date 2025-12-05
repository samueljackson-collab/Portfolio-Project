# Multi-Variant Code Generation Prompts

Use these curated prompts to generate consistent artifacts across infrastructure, application services, and pipelines. Each variant specifies intent, constraints, and quality gates.

## Variant A: Terraform Module Expansion
```
You are extending the PRJ-SDE-001 Terraform stack. Create a reusable module that provisions <service> with:
- Inputs for region, tags, subnet_ids, security_group_ids, kms_key_id, log_retention_days
- Enforced encryption at rest and in transit
- CloudWatch log/metric integration and alarms for availability/performance
- Sensible defaults for production (no public endpoints, deletion protection enabled)
- Example usage wiring into existing VPC, ECS, and IAM patterns
Outputs must expose ARNs, security group IDs, endpoints, and connection details. Include README usage and examples.
Quality gates: terraform fmt/validate, tflint, tfsec, and OPA/Conftest policies.
```

## Variant B: Application Service Scaffold
```
Generate a containerized Python/Node service named <service_name> that will run on ECS Fargate behind an ALB.
Requirements:
- Health check endpoint `/healthz` returning 200
- Structured JSON logging with correlation IDs (trace_id/span_id)
- Environment-driven DB connection strings (use AWS Secrets Manager pattern)
- Dockerfile optimized for small image (alpine/slim) and non-root user
- CI workflow steps for lint/test/build/push to ECR and image signing
- IaC snippet to wire the service into existing ALB target group and security groups
- Default autoscaling policy based on CPU/Memory and custom request rate
Quality gates: unit tests with coverage thresholds, container scan (trivy), and SBOM upload.
```

## Variant C: CI/CD Policy Enforcement
```
Design a GitHub Actions workflow for PRJ-SDE-001 that runs on pull requests and main merges.
Stages:
1) Static analysis: terraform fmt/validate, tflint, tfsec, trivy IaC, gitleaks
2) Unit + integration tests with coverage thresholds and junit/cobertura outputs
3) Terraform plan with cost estimate and PR comment; fail if cost delta > threshold
4) Security gates: dependency scan, secret scan, and OPA policy check
5) On main: apply to dev, run smoke tests, and gate prod apply on manual approval
Provide caching, failure notifications to Slack, and artifact uploads for plans and test reports.
```

## Variant D: Disaster Recovery Playbook Generator
```
Produce an automated DR procedure for PRJ-SDE-001.
- Terraform/CLI steps to recreate VPC, ECS, and RDS from latest backups/snapshots
- Traffic failover steps (Route53 health checks or ALB weighted target groups)
- Data validation checks post-restore (row counts, checksums, synthetic transactions)
- Rollback plan if integrity checks fail
- Time-bound RTO/RPO targets and success criteria
Format as a runbook with commands, checkpoints, and owner roles.
```

## Variant E: Observability Dashboards
```
Create a CloudWatch dashboard JSON for PRJ-SDE-001 showing:
- ALB latency (p95), 4xx/5xx rates
- ECS service CPU/Mem utilization, task count, and throttling/errors
- RDS connections, CPU, disk queue depth, free storage, replication lag
- Error budget burn rate and SLO attainment
- Log query widgets for key error patterns and auth failures
Ensure dimensions target the existing cluster, service, and database identifiers. Include alarms with runbook links.
```

## Variant F: Compliance Evidence Packager
```
Generate a script/workflow that collects deployment evidence for audits:
- Terraform plan/apply outputs, state versions, and module versions
- SBOMs and vulnerability scan results for images and dependencies
- Change request IDs, approvals, and deployment timestamps
- Log excerpts for authentication events and WAF blocks around change windows
Package artifacts into a timestamped bundle stored in S3 with retention policies.
```
