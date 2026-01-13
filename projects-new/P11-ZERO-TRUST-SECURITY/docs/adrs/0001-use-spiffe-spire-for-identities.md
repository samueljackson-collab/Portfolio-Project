# ADR 0001: Use SPIFFE/SPIRE for Workload Identities
## Context
We require cryptographic identities for all workloads to enable mTLS and policy decisions. Certificates must rotate automatically and be verifiable across clusters.
## Decision
Adopt SPIFFE IDs with SPIRE server/agent to issue and rotate SVIDs for Kubernetes workloads.
## Alternatives Considered
- Manual TLS certificates per service
- Istio-only certificates without SPIFFE
## Consequences
- Standardized identity format simplifies OPA policies.
- Added operational component (SPIRE) that must be monitored.
