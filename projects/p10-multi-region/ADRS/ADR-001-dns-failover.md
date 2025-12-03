# ADR-001: Route 53 DNS Failover Strategy

## Status
Accepted

## Context
We need region failover without app-level traffic managers. DNS failover with health checks fits the cost and simplicity constraints.

## Decision
- Use Route 53 failover records with health checks on `/healthz` endpoints.
- TTL set to 30s for responsiveness while balancing cache churn.
- Automate health check creation via Terraform.

## Consequences
- Clients may cache DNS beyond TTL; some requests may continue hitting primary during outage.
- Simpler than global load balancers; fewer moving parts for demos.
