# Runbook: Security Incident Response

## Overview

**Severity**: P0
**Response Time**: Immediate (< 15 minutes)
**Related ADRs**: [ADR-006: Zero-Trust Security Architecture](../adr/ADR-006-zero-trust-security-architecture.md)

## Incident Types

1. **Data Breach**: Unauthorized access to sensitive data
2. **Account Compromise**: User or admin account takeover
3. **DDoS Attack**: Distributed denial of service
4. **Malware/Ransomware**: Malicious software infection
5. **Insider Threat**: Malicious internal activity
6. **API Abuse**: Unauthorized API access or scraping
7. **SQL Injection**: Database attack attempts

## Immediate Response (First 15 Minutes)

### 1. Contain the Incident

```bash
# Isolate affected systems
kubectl cordon <affected-node>
kubectl drain <affected-node> --ignore-daemonsets --delete-emptydir-data

# Block suspicious IP addresses
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind:NetworkPolicy
metadata:
  name: block-suspicious-ips
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: portfolio
  policyTypes:
  - Ingress
  ingress:
  - from:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 192.0.2.0/24  # Suspicious IP range
EOF

# Revoke compromised credentials immediately
aws iam update-access-key \
  --access-key-id AKIAIOSFODNN7EXAMPLE \
  --status Inactive \
  --user-name compromised-user
```

### 2. Preserve Evidence

```bash
# Capture logs before they rotate
kubectl logs <affected-pod> > evidence-$(date +%Y%m%d-%H%M%S).log
kubectl logs <affected-pod> --previous >> evidence-$(date +%Y%m%d-%H%M%S).log

# Capture events
kubectl get events --sort-by='.lastTimestamp' -n production \
  > events-$(date +%Y%m%d-%H%M%S).log

# Capture pod state
kubectl describe pod <affected-pod> -n production \
  > pod-state-$(date +%Y%m%d-%H%M%S).txt

# Copy filesystem for forensics
kubectl cp production/<affected-pod>:/app ./forensics/app-$(date +%Y%m%d-%H%M%S)

# Database audit logs
aws rds download-db-log-file \
  --db-instance-identifier portfolio-prod \
  --log-file-name error/postgres.log \
  --output text > db-logs-$(date +%Y%m%d-%H%M%S).log
```

### 3. Notify Stakeholders

```bash
# Alert security team
curl -X POST $SECURITY_SLACK_WEBHOOK -d '{
  "text": "🚨 SECURITY INCIDENT - P0\nType: Data Breach\nTime: '$(date)'\nStatus: Investigating",
  "channel": "#security-incidents"
}'

# Email security team
aws ses send-email \
  --from security@example.com \
  --to security-team@example.com \
  --subject "SECURITY INCIDENT - IMMEDIATE ACTION REQUIRED" \
  --text "Security incident detected at $(date). War room: [link]"
```

## Investigation Checklist

### Data Breach Investigation

```bash
# 1. Identify attack vector
kubectl logs -n production deployment/app --since=2h | \
  grep -i "unauthorized\|forbidden\|breach"

# 2. Check access logs for suspicious patterns
aws logs filter-log-events \
  --log-group-name /aws/eks/production \
  --start-time $(date -d '2 hours ago' +%s)000 \
  --filter-pattern "401 OR 403 OR 500"

# 3. Review database access
kubectl exec -n production db-proxy -- \
  psql -U postgres -c "
    SELECT
      datname,
      usename,
      client_addr,
      query,
      query_start
    FROM pg_stat_activity
    WHERE client_addr IS NOT NULL
    ORDER BY query_start DESC
    LIMIT 100;"

# 4. Check for data exfiltration
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name NetworkTransmitThroughput \
  --dimensions Name=DBInstanceIdentifier,Value=portfolio-prod \
  --start-time $(date -u -d '2 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average

# 5. Identify affected users/data
psql -h db.amazonaws.com -U postgres -d portfolio -c "
  SELECT
    user_id,
    email,
    accessed_at,
    ip_address
  FROM audit_log
  WHERE accessed_at > NOW() - INTERVAL '2 hours'
  AND suspicious = true;"
```

### Account Compromise Response

```bash
# 1. Disable compromised accounts
psql -h db.amazonaws.com -U postgres -d portfolio -c "
  UPDATE users
  SET is_active = false,
      locked_reason = 'Security incident',
      locked_at = NOW()
  WHERE id IN ('[compromised-user-ids]');"

# 2. Force password reset for all users
psql -h db.amazonaws.com -U postgres -d portfolio -c "
  UPDATE users
  SET password_reset_required = true,
      reset_token = gen_random_uuid(),
      reset_token_expires = NOW() + INTERVAL '24 hours';"

# 3. Invalidate all sessions
redis-cli FLUSHDB  # Clears session cache

# 4. Revoke API keys
aws secretsmanager update-secret \
  --secret-id prod/api-keys \
  --secret-string '{}'  # Clear all keys

# 5. Rotate database credentials
aws secretsmanager rotate-secret \
  --secret-id prod/db-credentials
```

## Containment Measures

### 1. Network Isolation

```yaml
# Restrict egress traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-egress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: portfolio
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: production
    ports:
    - protocol: TCP
      port: 5432  # Only allow DB access
```

### 2. Enable Enhanced Logging

```bash
# Enable audit logging
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: audit-policy
  namespace: kube-system
data:
  audit-policy.yaml: |
    apiVersion: audit.k8s.io/v1
    kind: Policy
    rules:
    - level: RequestResponse
      resources:
      - group: ""
        resources: ["secrets", "configmaps"]
EOF

# Enable database query logging
kubectl exec -n production db-proxy -- \
  psql -U postgres -c "ALTER SYSTEM SET log_statement = 'all';"

kubectl exec -n production db-proxy -- \
  psql -U postgres -c "SELECT pg_reload_conf();"
```

### 3. Enable WAF Rules

```bash
# Block common attack patterns
aws wafv2 update-web-acl \
  --name portfolio-waf \
  --scope REGIONAL \
  --id [waf-id] \
  --lock-token [token] \
  --rules file://waf-emergency-rules.json

# Rate limiting
aws wafv2 create-rate-based-rule \
  --name emergency-rate-limit \
  --scope REGIONAL \
  --rate-limit 100  # 100 requests per 5 minutes
```

## Recovery Actions

### 1. Patch Vulnerabilities

```bash
# Update dependencies
npm audit fix --force

# Update container images
docker pull node:18-alpine
docker build -t portfolio:patched .

# Deploy patched version
kubectl set image deployment/app app=portfolio:patched -n production
```

### 2. Rotate All Secrets

```bash
#!/bin/bash
# rotate-all-secrets.sh

echo "Rotating all production secrets..."

# Rotate database credentials
aws secretsmanager rotate-secret --secret-id prod/db-credentials

# Rotate API keys
aws secretsmanager rotate-secret --secret-id prod/api-keys

# Rotate JWT secret
aws secretsmanager rotate-secret --secret-id prod/jwt-secret

# Rotate encryption keys
aws kms schedule-key-deletion \
  --key-id [old-key-id] \
  --pending-window-in-days 7

aws kms create-key --description "Portfolio encryption key (rotated)"

# Update Kubernetes secrets
kubectl create secret generic app-secrets \
  --from-literal=jwt-secret=$(aws secretsmanager get-secret-value --secret-id prod/jwt-secret --query SecretString --output text) \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart all pods to use new secrets
kubectl rollout restart deployment/app -n production

echo "Secret rotation complete"
```

### 3. Re-deploy from Clean Source

```bash
# Verify source code integrity
git verify-commit HEAD
git verify-tag v1.2.3

# Clean build
docker rmi $(docker images -q portfolio)
docker build --no-cache -t portfolio:clean .

# Security scan
trivy image portfolio:clean

# Deploy clean image
kubectl set image deployment/app app=portfolio:clean -n production
```

## Legal & Compliance Notifications

### GDPR (EU Customers)

```markdown
**Timeline**: Within 72 hours of discovery
**Authority**: Data Protection Authority (DPA)
**Content**:
- Nature of the breach
- Categories of data affected
- Approximate number of individuals affected
- Mitigation measures taken
- Contact point for information

**Contact**: DPA@example.com
```

### CCPA (California Residents)

```markdown
**Timeline**: Without unreasonable delay
**Content**:
- Types of information compromised
- Date of breach
- Steps users should take

**Contact**: legal@example.com
```

### PCI DSS (Payment Data)

```markdown
**Timeline**: Immediate notification
**Notify**:
- Acquiring bank
- Card brands (Visa, Mastercard, etc.)
- Forensic investigation required

**Contact**: acquiring-bank@example.com
```

### User Notification Template

```
Subject: Important Security Notice

Dear [User],

We are writing to inform you of a security incident that may have affected your account.

What Happened:
On [date], we detected [description of incident]. We immediately took steps to secure our systems and investigate the extent of the breach.

What Information Was Involved:
The following types of information may have been accessed:
- [Data type 1]
- [Data type 2]

What We're Doing:
- Secured our systems
- Engaged forensic investigators
- Notified law enforcement
- Implemented additional security measures

What You Should Do:
1. Reset your password immediately
2. Enable two-factor authentication
3. Monitor your account for suspicious activity
4. Review your recent transactions

We take this matter very seriously and sincerely apologize for any inconvenience.

For questions: security@example.com
Support: 1-800-XXX-XXXX

Sincerely,
[Company] Security Team
```

## Post-Incident Actions

### Immediate (Day 1-3)

- [ ] Complete forensic investigation
- [ ] Patch all vulnerabilities
- [ ] Rotate all credentials
- [ ] Notify affected users
- [ ] File regulatory notifications

### Short-term (Week 1-4)

- [ ] Conduct comprehensive security audit
- [ ] Update security policies
- [ ] Implement additional monitoring
- [ ] Review access controls
- [ ] Security training for team

### Long-term (Month 1-3)

- [ ] Penetration testing
- [ ] Third-party security assessment
- [ ] Update disaster recovery plan
- [ ] Review cyber insurance
- [ ] Implement recommended controls

## Forensics Preservation

```bash
# Create forensics snapshot
aws ec2 create-snapshot \
  --volume-id vol-1234567890abcdef0 \
  --description "Forensic snapshot - Incident $(date +%Y%m%d)"

# Preserve database state
pg_dump -h db.amazonaws.com -U postgres portfolio \
  > forensics/db-backup-$(date +%Y%m%d-%H%M%S).sql

# Collect memory dump (if applicable)
kubectl exec -n production <pod-name> -- \
  gcore $(pgrep -f "node.*app.js") \
  /tmp/core.dump

kubectl cp production/<pod-name>:/tmp/core.dump \
  ./forensics/memory-$(date +%Y%m%d-%H%M%S).dump
```

## Security Metrics

### Track and Report

```typescript
interface SecurityIncidentMetrics {
  incidentType: string;
  detectionTime: Date;
  containmentTime: Date;
  resolutionTime: Date;
  affectedUsers: number;
  dataExfiltrated: boolean;
  attackVector: string;
  MTTR: number; // Mean Time to Resolve
  MTTD: number; // Mean Time to Detect
}

async function recordIncident(incident: SecurityIncidentMetrics) {
  await db.security_incidents.create({
    ...incident,
    MTTR: incident.resolutionTime.getTime() - incident.detectionTime.getTime(),
    MTTD: incident.detectionTime.getTime() - incident.occurredAt.getTime()
  });

  // Alert if MTTD or MTTR exceeds threshold
  if (incident.MTTD > 15 * 60 * 1000) { // 15 minutes
    await alertSecurityTeam('MTTD exceeded threshold');
  }
}
```

## Related Runbooks

- [Incident Response Framework](./incident-response-framework.md)
- [Disaster Recovery](./runbook-disaster-recovery.md)

## Additional Resources

- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [OWASP Incident Response](https://owasp.org/www-community/Incident_Response)
- [SANS Incident Handler's Handbook](https://www.sans.org/white-papers/33901/)

---

**Last Updated**: December 2024
**Document Owner**: Security Team
**Review Frequency**: Quarterly
**Emergency Contact**: security@example.com
