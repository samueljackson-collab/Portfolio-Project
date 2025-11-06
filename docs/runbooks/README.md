# Production Runbooks & Incident Response

This directory contains operational runbooks for managing production incidents, performance issues, and disaster recovery scenarios.

## Purpose

These runbooks provide step-by-step procedures for:
- Detecting and diagnosing production issues
- Mitigating immediate impact
- Resolving root causes
- Preventing recurrence

## Runbook Index

### Incident Management
- [Incident Response Framework](./incident-response-framework.md) - Overall incident management process and communication templates

### Performance Issues
- [High CPU Usage](./runbook-high-cpu-usage.md) - Investigating and resolving CPU performance problems
- [Database Connection Pool Exhaustion](./runbook-database-connection-pool-exhaustion.md) - Managing database connection issues
- [High Error Rate](./runbook-high-error-rate.md) - Responding to elevated error rates

### Disaster Recovery
- [Disaster Recovery](./runbook-disaster-recovery.md) - Complete region failover and recovery procedures

### Security
- [Security Incident Response](./runbook-security-incident-response.md) - Data breach and security incident procedures

## Severity Levels

| Severity | Description | Response Time | Escalation |
|----------|-------------|---------------|------------|
| **P0 - Critical** | Complete service outage, data breach | 15 minutes | Immediate - Page on-call engineer |
| **P1 - High** | Major functionality impaired | 1 hour | Notify engineering lead |
| **P2 - Medium** | Degraded performance | 4 hours | Create ticket, assign owner |
| **P3 - Low** | Minor issues, cosmetic bugs | 24 hours | Backlog prioritization |

## Quick Reference

### Emergency Contacts
```
On-Call Engineer: PagerDuty rotation
Engineering Lead: @eng-lead (Slack)
Security Team: security@example.com
Legal/Compliance: legal@example.com
```

### War Room
```
Zoom: https://zoom.us/j/incident-war-room
Slack: #incident-response
Status Page: https://status.example.com
```

### Essential Commands

#### Health Checks
```bash
# Check pod status
kubectl get pods -n production

# View recent logs
kubectl logs -n production deployment/app --tail=100 --since=10m

# Check metrics
curl https://prometheus/api/v1/query?query=up
```

#### Quick Rollback
```bash
# Rollback to previous version
kubectl rollout undo deployment/app -n production

# Check rollback status
kubectl rollout status deployment/app -n production
```

#### Scale Resources
```bash
# Scale up
kubectl scale deployment/app -n production --replicas=10

# Scale down
kubectl scale deployment/app -n production --replicas=3
```

## Using These Runbooks

1. **Identify the Issue**: Use monitoring alerts or symptoms to determine which runbook applies
2. **Follow Investigation Steps**: Execute commands in order to diagnose the problem
3. **Execute Mitigation**: Apply immediate fixes to reduce impact
4. **Resolve Root Cause**: Implement permanent solutions
5. **Document**: Update the runbook with lessons learned

## Runbook Maintenance

- **Review Frequency**: Monthly
- **Testing**: Quarterly disaster recovery drills
- **Updates**: After each major incident (postmortem action item)
- **Owner**: DevOps Team

## Related Documentation

- [Architecture Decision Records](../adr/README.md) - System design decisions
- [Security Documentation](../security.md) - Security policies and procedures
- [Deployment Guide](../../projects/01-sde-devops/PRJ-SDE-001/README.md) - Infrastructure deployment

## Postmortem Template

After resolving an incident, create a postmortem using this structure:

```markdown
# Postmortem: [Incident Title]

**Date**: YYYY-MM-DD
**Duration**: [Total time]
**Severity**: P0/P1/P2/P3
**Impact**: [User impact description]

## Summary
[Brief description of what happened]

## Timeline
- HH:MM - [Event]
- HH:MM - [Detection]
- HH:MM - [Mitigation started]
- HH:MM - [Resolved]

## Root Cause
[Technical explanation of what went wrong]

## Resolution
[What fixed the issue]

## Action Items
- [ ] [Preventive measure 1]
- [ ] [Preventive measure 2]
- [ ] [Monitoring improvement]
- [ ] [Runbook update]

## Lessons Learned
[What we learned and will do differently]
```

---

**Last Updated**: December 2024
**Maintained By**: DevOps Team
**Emergency Contact**: oncall@example.com
