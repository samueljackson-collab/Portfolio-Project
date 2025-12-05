# Security Package — PRJ-SDE-002

## Threat Model
- Unauthorized access to metrics/logs revealing sensitive metadata.
- Tampering with alert routes leading to missed incidents.
- Compromise of PBS leading to data exfiltration or ransomware.
- Supply chain risks from container images and IaC modules.

## Controls
- **Identity & Access:** OIDC SSO for Grafana; RBAC roles (Admin/Editor/Viewer). Alertmanager auth via mTLS + basic auth behind reverse proxy. PBS admin limited to break-glass; backups encrypted.
- **Network:** Management VLAN, firewall allowlist, port restrictions, reverse proxy TLS termination with HSTS and rate limiting.
- **Secrets:** Store in Vault or SOPS; inject into compose via env files with 400 permissions; no secrets in git.
- **Images:** Pin image digests; enable container scanning (Trivy/Grype) in CI; signed images where supported.
- **Hardening:** Drop Linux capabilities for containers; run as non-root where possible; enable auditd on hosts.

## Logging & Audit
- Enable Grafana and Alertmanager audit logs; forward to Loki with retention 90d.
- Record backup operations and restores in PBS logs; ship to Loki.
- Preserve CI logs for IaC changes; enforce PR approvals for config changes.

## Certificates & Keys
- ACME/CA-issued certs rotated every 60–90 days; cert expiry alerts in Prometheus.
- mTLS for Promtail→Loki and Prometheus→Alertmanager; separate client/server certs with revocation process.

## Incident Response
- On detection of unauthorized access: rotate creds/certs, invalidate sessions, review audit logs, and perform scope analysis.
- Backup compromise: disable network access, verify integrity via checksums, restore from clean snapshot, rotate encryption keys.

## Compliance Considerations
- Aligns with SOC2 security/availability: access control, change management, logging, backup integrity.
- Data classification: logs and metrics tagged by sensitivity; PII should be excluded or tokenized before shipping.
