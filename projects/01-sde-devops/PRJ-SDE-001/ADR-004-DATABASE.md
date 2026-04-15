# ADR-004: PostgreSQL on Amazon RDS

- **Status:** Accepted
- **Date:** 2025-05-14

## Context
The application needs relational consistency, transactional guarantees, and managed backups. Operational overhead should be minimized while retaining control over performance and security.

## Decision
- Use **Amazon RDS for PostgreSQL** with Multi-AZ capability and automated backups.
- Enable **KMS encryption**, automated minor version upgrades during maintenance windows, and deletion protection in production.
- Expose connection details via **Secrets Manager** with rotation policies and parameter groups tuned for workload.
- Support **read replicas** for scale-out read scenarios and DR readiness.

## Consequences
- ✅ Managed backups, patching, and monitoring reduce operational burden.
- ✅ Native integration with VPC/security groups and IAM auth options.
- ⚠️ Less control than self-managed databases; extensions limited to RDS support.
- ⚠️ Costs scale with storage/IOPS; requires monitoring and rightsizing.
