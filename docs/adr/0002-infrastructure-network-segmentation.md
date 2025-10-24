# ADR 0002: Infrastructure Network Segmentation

- **Status:** Accepted
- **Date:** 2025-10-11

## Context
We needed a networking approach that secures backend services and databases while enabling controlled ingress for public endpoints.

## Decision
Implement a three-tier VPC structure with dedicated subnets for web, application, and data tiers across multiple availability zones. Security groups restrict traffic flow to necessary ports only.

## Consequences
- ✅ Minimizes lateral movement risk inside the VPC.
- ✅ Supports scaling by adding additional private subnets without exposing data tier.
- ⚠️ NAT gateways introduce additional cost; mitigated via shared gateway in non-production.

