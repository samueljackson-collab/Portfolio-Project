# Troubleshooting Guide

## Common Issues

### Pods Pending Scheduling
- Check resource quotas and namespace limits.
- Verify node group capacity; trigger scale-up if needed.
- Inspect taints/tolerations and node selectors.

### Failing Deployments
- Review Argo CD events for sync errors.
- Validate container image availability and pull secrets.
- Confirm ConfigMap or Secret references are correct.

### Network Connectivity Problems
- Inspect network policies for allow/deny rules.
- Validate AWS security groups and route tables.
- Use `kubectl exec` with curl or ping for diagnostics.

### Control Plane Access Issues
- Ensure AWS IAM Authenticator map includes current users/roles.
- Check API server endpoint status in AWS Console.
- Use bastion host for private cluster connectivity.

### Persistent Volume Failures
- Confirm storage class configuration and availability zones.
- Check for dangling EBS volumes and clean up manually if necessary.

## Escalation Path
1. Attempt remediation using steps above and document actions.
2. Notify on-call channel with summary of impact and ETA.
3. Escalate to platform lead if issue exceeds 30 minutes without resolution.
4. Open AWS support ticket for provider-level incidents.

Keep notes of resolved incidents to feed retrospectives and ADR updates.
