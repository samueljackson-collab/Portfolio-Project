# P18 · Homelab Infrastructure — Operations Runbook

## 1. Daily Tasks
| Time | Task | Notes |
| --- | --- | --- |
| 07:00 | Check Proxmox cluster health dashboard | Confirm HA status green, no failed tasks |
| 12:00 | Validate backup jobs completed | Review Proxmox Backup Server activity log |
| 18:00 | Inspect TrueNAS alerts | Resolve disk SMART warnings immediately |
| 22:00 | Verify Vault seal status and unseal keys custody | Rotate audit log export if rotated |

## 2. Weekly Tasks
- Patch Linux VMs via Ansible `ansible-playbook -i inventory site.yml --tags patch`.
- Review firewall rules in UniFi controller; export configuration snapshot.
- Test UPS failover by simulating power event once per quarter (rotate hosts weekly).
- Sync architecture diagrams stored in `documentation/homelab/diagrams/` with current topology.

## 3. Monthly Tasks
1. Restore a random VM from backup to validation host; document duration and issues.
2. Rotate VPN keys for remote access users; update documentation.
3. Reconcile asset inventory vs. `inventory.yml` and update discrepancies.
4. Run security scan using OpenVAS profile `Homelab-Full`; triage findings.

## 4. Change Control
- Record all infrastructure changes in `CHANGELOG.md` at project root.
- Major network modifications require maintenance window approval and rollback plan.
- Use Git branches for Ansible or Terraform updates; merge only after test-lab validation.

## 5. Incident Response
- Trigger `Homelab` escalation policy in PagerDuty for outages exceeding 10 minutes.
- Capture Prometheus snapshots for post-incident analysis.
- Follow incident templates in `projects/p18-homelab/docs/PLAYBOOK.md`.

## 6. Backup Procedures
- Nightly: VMs snapshot to TrueNAS dataset `pool0/backups` via PBS schedule.
- Weekly: `rclone` sync to S3-compatible storage (Wasabi) using encrypted remote.
- Monthly: Export configuration bundle (`proxmox-backup-manager cert info`) to offline vault.

## 7. Access Management
- SSH access restricted via Certificate Authority; issue short-lived certificates using `step ca`.
- TrueNAS and Proxmox admin accounts require hardware MFA keys.
- Maintain access list in `projects/p18-homelab/access/ACCESS.md` with review every 30 days.
