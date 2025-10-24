# OPA Security Policy for Kubernetes

## Overview
Policy-as-code bundle using Open Policy Agent Gatekeeper to enforce Kubernetes workload security standards across clusters.

## Policies
- Require namespaces to include approved labels (`team`, `cost-center`, `data-classification`).
- Enforce Pod Security Standards (restricted) including read-only root filesystem, dropping host namespaces, and requiring seccomp/apparmor profiles.
- Validate container images originate from trusted registries and have signed provenance attestations.
- Ensure resource requests/limits and liveness/readiness probes are defined.

## Repository Layout
- `policies/` – Rego constraint templates.
- `constraints/` – Environment-specific constraint definitions.
- `tests/` – `conftest` suites validating compliance scenarios.
- `docs/` – Policy reference matrix mapping to CIS Benchmarks.

## Deployment
1. Package bundle: `opa build -b . -o bundle.tar.gz`.
2. Publish to OCI registry or push to Gatekeeper via ConfigMap.
3. Apply constraints using `kubectl apply -f constraints/`.
4. Monitor violations via Gatekeeper audit logs integrated with Prometheus/Grafana dashboards.

## Testing & CI
- Run `conftest test` pre-commit and in CI.
- Use `gatekeeper-policy-manager` for UI visualization.
- Integration tests executed against KinD cluster via `make test-integration`.

