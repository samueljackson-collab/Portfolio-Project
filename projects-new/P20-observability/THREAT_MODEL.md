# Threat Model

Threats:
- Unauthorized dashboard access
- Silenced alerts missing incidents
- Log retention overrun

Mitigations:
- Grafana SSO + folders RBAC
- Alertmanager silence TTL + audit
- Loki retention config with compaction
