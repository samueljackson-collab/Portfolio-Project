# ADR-004: Database Platform

## Context
The application requires a relational database with strong consistency, managed backups, and minimal operational overhead. Multi-AZ resilience and encryption are mandatory.

## Decision
- Use **Amazon RDS for PostgreSQL** with Multi-AZ deployment for HA and automated backups.
- Enable **encryption at rest** via KMS and enforce TLS in transit; disallow public access.
- Configure **parameter groups** for workload tuning (connection limits, autovacuum) and enable performance insights for analysis.
- **Backups:** Daily automated snapshots with point-in-time recovery; optional cross-region copy for DR.
- Access controlled via **security groups** allowing only ECS tasks and admin bastions (via Session Manager) where necessary.

## Consequences
- Managed service reduces patching/maintenance overhead; limited control over minor version timing.
- Multi-AZ increases cost but meets availability requirements; cross-region copy adds additional spend.
- Parameter tuning and performance insights provide levers for optimization with DB engineer oversight.

## Status
Accepted
