# Architecture Overview

This document describes the reference architecture for the Portfolio API platform. It captures component responsibilities, network flows, resiliency considerations, and the supporting infrastructure defined in [`infrastructure/`](./infrastructure/).

## High-Level Diagram

```
                           ┌──────────────────────┐
                           │  External Consumers  │
                           └──────────┬───────────┘
                                      │ HTTPS
                           ┌──────────▼───────────┐
                           │  Ingress Controller  │
                           │ (AWS ALB + NGINX)    │
                           └──────────┬───────────┘
                                      │ mTLS + JWT auth
                         ┌────────────▼─────────────┐
                         │     Portfolio API Pods    │
                         │  (stateless containers)   │
                         └────┬───────────┬──────────┘
                              │ gRPC      │ Async Jobs
                              │           │ (SQS)
                ┌─────────────▼─┐    ┌────▼───────────┐
                │ PostgreSQL DB │    │  Worker Pods    │
                │   (RDS/Aurora)│    │ (queue runners) │
                └──────┬────────┘    └────┬────────────┘
                       │                 │
             ┌─────────▼────────┐ ┌──────▼──────────┐
             │ Secrets Manager   │ │ Object Storage  │
             │ (AWS SecretsMgr)  │ │   (S3 buckets)  │
             └───────────────────┘ └────────────────┘
```

## Component Summary

| Component | Description | Defined In |
| --- | --- | --- |
| **Networking** | VPC, subnets, routing tables, and security groups that isolate workloads. | [`infrastructure/terraform/network.tf`](./infrastructure/terraform/network.tf) |
| **Compute** | EKS cluster with managed node groups for API and worker pods. | [`infrastructure/terraform/eks.tf`](./infrastructure/terraform/eks.tf) |
| **Data** | Highly available PostgreSQL via Amazon Aurora and encrypted S3 bucket for assets. | [`infrastructure/terraform/data.tf`](./infrastructure/terraform/data.tf) |
| **Application** | Kubernetes Deployments, Services, ConfigMaps, and Horizontal Pod Autoscalers. | [`infrastructure/kubernetes/`](./infrastructure/kubernetes/) |
| **Observability** | Prometheus Operator stack with Alertmanager integration. | [`monitoring/prometheus/`](./monitoring/prometheus/) |
| **Security** | IAM roles, OPA policies, and Kubernetes NetworkPolicies. | [`security/policies/`](./security/policies/) |

## Application Layer

The Portfolio API is a stateless Go service deployed as a container image. It exposes REST and gRPC interfaces for retrieving case studies, automation artifacts, and operational metrics. Rolling deployments are handled via Kubernetes Deployments with health checks defined for `/healthz` (liveness) and `/readyz` (readiness).

Key design notes:

- **Config separation:** Runtime configuration is injected via ConfigMaps and Secrets. Secrets are synchronized from AWS Secrets Manager using the external-secrets controller.
- **Autoscaling:** Horizontal Pod Autoscaler targets CPU (60%) and custom Prometheus metrics for request latency (p95 < 400ms).
- **Routing:** An ingress object routes `/api/*` traffic to the Portfolio API service and `/metrics` to a metrics sidecar. TLS certificates are managed via AWS Certificate Manager.

## Data Layer

Persistent data lives in a multi-AZ Aurora PostgreSQL cluster. Application pods connect using IAM authentication and short-lived tokens issued via the `rds-iam` authenticator. Read replicas handle analytical queries triggered by asynchronous workers.

- **Schema Management:** Flyway migrations run during CI/CD as described in [DEPLOYMENT.md](./DEPLOYMENT.md#database-migrations).
- **Backups:** Automated snapshots are scheduled daily with a 35-day retention period. Export jobs push weekly point-in-time snapshots to S3 for disaster recovery.
- **Caching:** A managed ElastiCache Redis cluster (optional module) accelerates frequently requested portfolio summaries.

## Integration & Messaging

Long-running tasks—such as generating PDF exports or synchronizing evidence assets—are processed asynchronously:

1. API receives a request and validates payloads against the schema defined in [API_DOCUMENTATION.md](./API_DOCUMENTATION.md).
2. The request metadata is published to an Amazon SQS FIFO queue.
3. Worker pods consume the queue, interact with S3 and PostgreSQL, and update job status records.
4. Clients poll `/api/v1/jobs/{id}` or subscribe to WebSocket notifications.

## Observability Stack

Prometheus scrapes application, Kubernetes, and AWS metrics via the kube-state-metrics and CloudWatch exporter. Alerting rules fire into Alertmanager, which routes notifications to Slack and PagerDuty. Grafana dashboards referenced in [`monitoring/prometheus/dashboards/`](./monitoring/prometheus/dashboards/) visualize golden signals.

- **Logging:** Fluent Bit forwards JSON logs to Amazon OpenSearch with index lifecycle management.
- **Tracing:** OpenTelemetry collectors forward traces to AWS X-Ray for dependency analysis.

## Resiliency Considerations

- **Multi-AZ deployments** across application nodes, databases, and load balancers ensure durability during AZ outages.
- **Circuit breakers** implemented in the service gracefully shed load when dependencies become unavailable.
- **Chaos testing** scenarios are documented in [`documentation/chaos-testing.md`](./documentation/chaos-testing.md).

## Security Controls

Security is applied end-to-end:

- **Network segmentation:** Kubernetes network policies (see [`security/policies/network-policy.yaml`](./security/policies/network-policy.yaml)) restrict east-west traffic to explicit ports.
- **Secrets management:** IAM roles grant least-privilege access. Policies are version-controlled in [`security/policies/iam-portfolio-api.json`](./security/policies/iam-portfolio-api.json).
- **Supply-chain defenses:** Admission controllers enforce signed images. Details reside in [SECURITY.md](./SECURITY.md#supply-chain-protections).

## Architecture Decision Records

ADR summaries are stored under [`documentation/adr/`](./documentation/adr/). Each decision references the Git commit implementing the change and includes:

1. Context and problem statement.
2. Considered options.
3. Decision outcome and consequences.

Refer to `documentation/adr/0001-use-eks.md` for the reasoning behind choosing Amazon EKS over self-managed Kubernetes.

