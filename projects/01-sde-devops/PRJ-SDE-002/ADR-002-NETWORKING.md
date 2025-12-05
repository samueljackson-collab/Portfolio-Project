# ADR-002: Networking & Access

## Status
Accepted

## Context
Monitoring and backup services span multiple ports and require secure cross-host communication. Default open access would expose metrics and logs.

## Decision
- Place Prometheus, Grafana, Loki, and Alertmanager on a **management VLAN** with firewall rules allowing only required source IP ranges (jump hosts, CI runners, PBS).
- Enforce **mTLS** between Promtail→Loki and Prometheus→Alertmanager; TLS for Grafana and PBS via ACME or internal CA.
- Use **reverse proxy** (Traefik/Caddy/Nginx) for unified entry with HTTPS and rate limiting; enable OIDC for Grafana access.
- Allocate static IPs/DNS (`monitoring.local`, `backups.local`) and publish SRV records for exporters where possible.

## Consequences
- Pros: Reduced attack surface, predictable connectivity, easier certificate management.
- Cons: Added complexity for certificate rotation and initial bootstrap.
- Follow-ups: Automate firewall as code; periodically pen-test exposed endpoints; monitor cert expiry.
