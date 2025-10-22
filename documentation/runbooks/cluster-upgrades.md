# Kubernetes Cluster Upgrade Runbook

## Overview

Perform EKS version upgrades twice per year, aligning with AWS supported versions.

## Pre-Upgrade Checklist

- Review AWS EKS release notes.
- Confirm worker AMI availability for target version.
- Ensure [`scripts/compliance-scan.sh`](../../scripts/compliance-scan.sh) passes on latest image.

## Upgrade Steps

1. Update Terraform variable `eks_version` in `env/<env>.tfvars`.
2. Run `terraform apply` via [`scripts/deploy.sh`](../../scripts/deploy.sh).
3. Cordon and drain nodes one at a time:
   ```bash
   kubectl drain <node> --ignore-daemonsets --delete-emptydir-data
   ```
4. Verify workloads rescheduled successfully.
5. Run [`scripts/smoke-test.sh`](../../scripts/smoke-test.sh) and review Prometheus alerts.

## Post-Upgrade

- Update Grafana dashboard annotations.
- Close change request ticket with summary of findings.
