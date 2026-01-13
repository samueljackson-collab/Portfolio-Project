# ADR 0002: Envoy as Data Plane Proxy
## Context
We need a sidecar that enforces mTLS, exposes rich metrics, and integrates with SPIFFE identities.
## Decision
Deploy Envoy sidecars for each service to terminate mTLS and forward authorized traffic.
## Alternatives Considered
- Nginx sidecars
- Native Kubernetes networking with NetworkPolicy only
## Consequences
- Consistent telemetry and mTLS handling.
- Slight increase in resource usage per pod.
