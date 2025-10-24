# ADR 002: Choose Amazon RDS PostgreSQL

- **Status:** Accepted
- **Date:** 2025-10-11

## Context

The sample workload requires a managed relational database that supports transactions, point-in-time recovery, and integration with existing analytics tooling.

## Decision

Standardize on Amazon RDS for PostgreSQL using the Multi-AZ option. PostgreSQL offers strong SQL compatibility, rich extension support, and integrates cleanly with application frameworks used in portfolio demos.

## Consequences

- ✅ Reduces operational overhead versus self-managed databases.
- ✅ Aligns with common enterprise stack expectations.
- ❌ Increases baseline cost compared to open-source alternatives running on EC2.
