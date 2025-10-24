# ADR 001: Adopt Multi-AZ Deployment

- **Status:** Accepted
- **Date:** 2025-10-11

## Context

High availability is a core requirement for portfolio projects that claim production readiness. Single availability zone deployments can suffer from prolonged outages during an AZ failure.

## Decision

Deploy critical workloads (application auto-scaling groups and the RDS database) across at least two availability zones using AWS managed services.

## Consequences

- ✅ Improved resilience against zonal failures.
- ✅ Demonstrates understanding of highly available architectures.
- ❌ Slightly higher cost due to duplicate infrastructure across zones.
