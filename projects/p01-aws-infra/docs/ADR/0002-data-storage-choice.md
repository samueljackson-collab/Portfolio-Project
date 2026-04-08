# ADR 0002 — Data Storage Choice

**Status**: Accepted
**Date**: 2024-11-08
**Deciders**: Platform Team, Data Engineering Lead

## Context
The infrastructure stack requires a durable relational data store for application state, audit logs, and IaC outputs. The service portfolio needs HA across availability zones, support for native IAM authentication, and a managed backup/restore workflow with minimal operational overhead. The database should integrate cleanly with existing CloudFormation templates and support future read scaling without re-architecting the network.

## Decision
Adopt **Amazon RDS for PostgreSQL (Multi-AZ)** as the primary data store.

### Rationale
- Mature feature set (JSONB, extensions) that satisfies current application use cases.
- Native integration with CloudFormation, Secrets Manager, and IAM authentication.
- Automated backups with PITR and snapshot exports to S3 for compliance evidence.
- Clear migration path to read replicas for analytics without impacting primaries.

## Alternatives Considered
- **Amazon Aurora PostgreSQL**: Higher performance and fast failover but higher cost and additional operational tuning not yet required.
- **Amazon RDS for MySQL**: Familiar option, but lacks some PostgreSQL features (e.g., robust JSON operators) used by analytics workloads.
- **Self-managed PostgreSQL on EC2**: Full control but increases patching/operational burden and weakens managed backup guarantees.

## Consequences

### Positive
- Reduced operational toil via managed backups, monitoring, and maintenance windows.
- Consistent IAM-based authentication and integration with existing CloudFormation stacks.
- Future scalability via read replicas without major schema redesign.

### Negative
- Aurora’s lower-failover times are not leveraged; recovery is bounded by RDS Multi-AZ limits.
- Vendor lock-in to AWS-managed database services.
- Storage and IOPS costs scale with Multi-AZ; must monitor budgets.

### Mitigation
- Re-evaluate Aurora if latency/error budget trends degrade or read workloads spike.
- Implement budget alarms on RDS storage/IOPS metrics.
- Document snapshot/restore runbooks to maintain RTO/RPO confidence.
