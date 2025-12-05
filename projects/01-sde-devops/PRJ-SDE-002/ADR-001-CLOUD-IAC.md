# ADR-001: Infrastructure as Code & Config Management

## Status
Accepted

## Context
The observability stack spans Prometheus, Grafana, Loki, Alertmanager, Promtail, and Proxmox Backup Server with multiple exporters. Manual configuration risks drift, inconsistent alerting, and insecure defaults.

## Decision
- Use **Terraform** to provision infrastructure (VMs, storage volumes, networking, DNS) and **Ansible** to configure services and deploy configuration bundles.
- Store configuration in git and apply changes via **GitOps** workflows (pull-request approvals, CI linting, plan/apply stages).
- Template Prometheus, Loki, Promtail, Alertmanager, and Grafana provisioning using shared variables for ports, TLS, and labels.

## Consequences
- Pros: Repeatable deployments, auditable changes, easier disaster recovery, consistent TLS and RBAC.
- Cons: Increased upfront investment in modules, need for secret management integration.
- Follow-ups: Integrate with CI (pre-commit, terraform fmt/validate, ansible-lint); rotate secrets via Vault or SOPS.
