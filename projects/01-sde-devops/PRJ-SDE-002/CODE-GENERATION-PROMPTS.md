# Code Generation Prompts — PRJ-SDE-002

Use these prompts in your preferred LLM to generate consistent automation. Include environment variables, secrets, and file paths explicitly when running.

## Terraform Baseline (Proxmox VMs + Networking)
```
You are an SRE automating PRJ-SDE-002. Generate Terraform to create two Proxmox VMs: `monitoring` and `backups`. Monitoring VM: 4 vCPU, 8GB RAM, 100GB SSD, static IP 192.168.50.10. Backups VM: 4 vCPU, 16GB RAM, 500GB disk, static IP 192.168.50.11. Add firewall rules allowing 22, 80, 443, 9090, 9093, 3000, 3100, 8007 from management CIDR 192.168.50.0/24 only. Output variables for VLAN, gateway, DNS, and SSH keys. Apply tags `env=lab`, `project=prj-sde-002`. Use cloud-init where possible.
```

## Ansible Play (Monitoring Stack)
```
Act as an infra engineer. Write an Ansible playbook to install Prometheus, Alertmanager, Grafana, Loki, and Promtail on the monitoring VM using Docker Compose. Include tasks to:
- Install Docker/Compose prerequisites.
- Template docker-compose.yml with volumes under /opt/monitoring.
- Configure Prometheus scrape targets from group_vars (node exporters, app exporters, Proxmox exporter).
- Enable systemd service for compose stack with healthcheck retries.
- Configure TLS certs from /etc/ssl/monitoring and inject into Grafana, Alertmanager, Prometheus, and Loki.
- Run ansible-lint compliant YAML.
```

## Alertmanager Routing Rules
```
Generate Alertmanager config for PRJ-SDE-002 with routes: sev0->PagerDuty+Slack #sev0, sev1->Slack #sev1, sev2->Email NOC, sev3->Email backlog. Use labels `service`, `environment`, `owner`. Include inhibition rules to suppress lower-severity alerts when higher-severity for same service is firing. Add receiver templates with runbook URLs and Grafana links. Certificates are in /etc/ssl/monitoring. mTLS between Prometheus and Alertmanager.
```

## Grafana Provisioning
```
Create Grafana provisioning YAML to:
- Configure Prometheus and Loki data sources with TLS and auth.
- Import dashboards from /var/lib/grafana/dashboards (JSON) with folders: Infrastructure, Applications, Backups, Platform Health.
- Set up alerting contact points (Slack, PagerDuty, Email) and mute timings for maintenance windows.
- Enable OIDC (Auth0/Keycloak) with role mapping (Admin for sre-team, Viewer for dev-team).
```

## PBS Backup Policy
```
Write PBS backup policy JSON for nightly VM backups at 02:00 with 30-day retention and weekly full verification. Include prune schedule, encryption setting (AES-256), and hook to run a post-backup script that pushes metrics to Prometheus pushgateway. Apply to VMs tagged `backup=on` in Proxmox.
```

## CI/CD Pipeline
```
Design a CI pipeline (GitHub Actions) that runs terraform fmt/validate, ansible-lint, yamllint, generates a Prometheus config diff, and performs a Loki config dry-run. Include steps to build and push updated docker-compose images and to notify Slack on success/failure.
```
