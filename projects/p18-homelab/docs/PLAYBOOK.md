# P18 · Homelab Infrastructure — Incident Playbook

## Power Loss / UPS Event (P1)
1. Confirm alerts from UPS and Prometheus; ensure critical loads on battery.
2. Initiate graceful shutdown order: Kubernetes worker nodes → application VMs → storage.
3. Verify backups completed prior to event; if not, trigger manual snapshot when power restored.
4. After power returns, bring infrastructure up in reverse order and validate monitoring dashboards.

## Storage Pool Degradation (P1)
1. Check TrueNAS alert details for failed disk ID.
2. Replace disk using hot-swap procedure; mark old disk for RMA.
3. Monitor resilver progress; do not perform maintenance until 100% complete.
4. Update asset inventory and incident record once pool healthy.

## Network Isolation / VLAN Failure (P2)
1. Validate UniFi controller shows affected VLAN offline.
2. If caused by config drift, restore last known-good backup.
3. If hardware fault suspected, relocate patch connections to spare switch port.
4. Run end-to-end ping tests across VLAN boundaries to confirm recovery.

## Service Failure (Reverse Proxy) (P2)
1. Check Traefik container status via `docker ps` on services host.
2. Review logs at `/var/log/traefik/traefik.log`; look for certificate renewal issues.
3. Restart service `systemctl restart traefik`; if failure persists, deploy new config via Ansible.
4. Validate HTTPS access from trusted and guest networks.

## Security Alert (Suspicious Login) (P2)
1. Review Vault audit logs and Proxmox access logs for suspicious entries.
2. Immediately rotate credentials for affected account; revoke tokens.
3. Inspect network flows using Zeek capture; ensure no data exfiltration occurred.
4. Document incident in `documentation/security/incidents/` with timeline and root cause.

## Communication Template
- **Initial:** "Homelab incident detected (<summary>). Investigation underway; next update in 15 minutes."
- **Mitigation:** "Mitigation in progress: <actions>. Monitoring impact."
- **Resolved:** "Incident resolved at <time>. Cause: <summary>. Follow-up: <actions>."
