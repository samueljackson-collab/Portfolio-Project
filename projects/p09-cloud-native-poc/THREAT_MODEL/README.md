# Threat Model — P09

## Assets
- API endpoints, SQLite/Postgres data, container images, metrics and logs.

## Entry Points
- Public API routes, metrics endpoint, k8s service exposure, CI pipeline artifacts.

## Threats
- **Unauthorized access:** missing auth on demo endpoints.
- **Data leakage:** logs containing payload data.
- **Supply chain:** dependencies or container base images compromised.

## Mitigations
- Optional API key middleware enabled via `ENABLE_AUTH`.
- Structured logging with field filters; avoid logging secrets.
- Dependency scanning via `pip-audit`; base images pinned.

## Residual Risks
- Demo deployments may run without auth; ensure non-production data only.
