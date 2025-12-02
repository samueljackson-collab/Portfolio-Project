# ADR 0003: OPA for Service-to-Service Authorization
## Context
Policies must be codified, versioned, and evaluated close to workloads with auditability.
## Decision
Use OPA sidecars with Rego policies to implement deny-by-default authorization for all service calls.
## Alternatives Considered
- Envoy RBAC filters only
- Hard-coded authorization in each service
## Consequences
- Centralized policy authoring and testing.
- Requires ConfigMap updates and policy rollouts.
