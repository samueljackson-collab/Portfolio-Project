# Kubernetes Platform Runbook

## Purpose
Provide operators with clear, repeatable steps to manage the Kubernetes platform.

## Table of Contents
1. Cluster Health Checks
2. Scaling Procedures
3. Deployment Guidelines
4. Backup & Restore
5. Incident Response
6. Maintenance Windows

## 1. Cluster Health Checks
- Use `kubectl get nodes` to confirm node readiness.
- Monitor control plane health via AWS Console or `aws eks describe-cluster`.
- Review Prometheus dashboards for CPU, memory, and etcd health.

## 2. Scaling Procedures
- Adjust node group sizes via Terraform variables and run the pipeline.
- For emergency scale-ups, use the AWS Console while documenting manual changes.

## 3. Deployment Guidelines
- All workloads use GitOps via Argo CD.
- Ensure namespaces and resource quotas are defined before onboarding teams.

## 4. Backup & Restore
- Enable Velero for cluster state backups.
- Nightly backups stored in S3 with lifecycle policies.
- Restoration drills performed quarterly with documented results.

## 5. Incident Response
- Reference on-call rotation in `docs/troubleshooting.md`.
- Escalate to platform lead if control plane unavailable for >15 minutes.

## 6. Maintenance Windows
- Patch Tuesdays for node AMIs and addons.
- Communicate change windows 48 hours in advance to application teams.

Keep this runbook current with every platform change.
