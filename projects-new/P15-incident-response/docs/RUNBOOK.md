# Incident Response Automation - Operations Runbook

**Version:** 1.0.0 | **Last Updated:** 2025-11-10

## Overview

This runbook provides operational procedures, troubleshooting guides, and incident response workflows for Incident Response Automation.

## Table of Contents

1. [Service Overview](#service-overview)
2. [Deployment Procedures](#deployment-procedures)
3. [Monitoring & Alerts](#monitoring--alerts)
4. [Troubleshooting](#troubleshooting)
5. [Incident Response](#incident-response)
6. [Maintenance Procedures](#maintenance-procedures)

---

## Service Overview

### Service Details

- **Service Name:** Incident Response Automation
- **Owner:** Platform Engineering Team
- **On-Call Rotation:** PagerDuty
- **SLA Target:** 99.9% uptime
- **RTO:** 1 hour
- **RPO:** 15 minutes

### Dependencies

- **Database:** PostgreSQL (RDS)
- **Cache:** Redis (ElastiCache)
- **Queue:** SQS
- **Storage:** S3

### Endpoints

- **Health Check:** `/health`
- **Metrics:** `/metrics`
- **API Docs:** `/docs`

---

## Deployment Procedures

### Pre-Deployment Checklist

- [ ] All tests passing in CI/CD
- [ ] Security scan completed
- [ ] Change ticket approved
- [ ] Deployment window confirmed
- [ ] Team notified in #deployments Slack channel

### Deployment Steps

```bash
# 1. Connect to bastion host
ssh bastion.example.com

# 2. Pull latest code
cd /opt/incident-response
git fetch origin
git checkout tags/v1.2.3

# 3. Run database migrations (if any)
make migrate

# 4. Deploy application
make deploy ENV=production

# 5. Verify health
curl https://api.example.com/health

# 6. Monitor for 15 minutes
watch -n 10 'curl -s https://api.example.com/health | jq'
```

### Rollback Procedure

```bash
# 1. Identify previous version
git tag --sort=-creatordate | head -n 5

# 2. Deploy previous version
git checkout tags/v1.2.2
make deploy ENV=production

# 3. Verify rollback
curl https://api.example.com/health
```

---

## Monitoring & Alerts

### Key Dashboards

- **Grafana:** https://grafana.example.com/d/incident-response
- **CloudWatch:** https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=incident-response

### Alert Severity Levels

| Severity | Response Time | Escalation |
|----------|--------------|------------|
| P1 (Critical) | 15 minutes | Page on-call engineer |
| P2 (High) | 1 hour | Email + Slack |
| P3 (Medium) | 4 hours | Slack notification |
| P4 (Low) | Next business day | Ticket in backlog |

### Common Alerts

#### High Error Rate

**Alert:** `incident-response_high_error_rate`

**Symptoms:**
- 5xx error rate >5% over 5 minutes
- Users reporting "Service Unavailable" errors

**Diagnosis:**
```bash
# Check error logs
aws logs tail /aws/lambda/incident-response --follow --filter '5xx'

# Check service health
kubectl get pods -n incident-response
kubectl logs -n incident-response <pod-name> --tail=100
```

**Resolution:**
1. Check for recent deployments (potential bad release)
2. Review application logs for stack traces
3. If recent deployment, rollback immediately
4. If database issue, check connection pool exhaustion
5. Scale up if resource saturation detected

#### High Latency

**Alert:** `incident-response_high_latency`

**Symptoms:**
- P95 latency >500ms
- Users reporting slow page loads

**Diagnosis:**
```bash
# Check slow query log
psql -h <db-host> -U admin -c "SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Check cache hit rate
redis-cli INFO stats | grep keyspace
```

**Resolution:**
1. Identify slow database queries and add indexes
2. Check cache hit rate, warm cache if needed
3. Review recent code changes for inefficient loops
4. Scale up database if CPU >80%

---

## Troubleshooting

### Service Won't Start

**Symptoms:**
- Container crashes immediately after start
- Health check failing

**Diagnosis:**
```bash
# Check container logs
docker logs <container-id>

# Check environment variables
docker exec <container-id> env | grep -E '(DB_|REDIS_|API_)'

# Check connectivity
docker exec <container-id> nc -zv <db-host> 5432
```

**Common Causes:**
- Missing environment variables
- Database connection failure
- Port already in use
- Insufficient permissions

### Database Connection Errors

**Symptoms:**
- `psycopg2.OperationalError: could not connect to server`

**Resolution:**
```bash
# 1. Verify database is running
aws rds describe-db-instances --db-instance-identifier incident-response-prod

# 2. Check security group rules
aws ec2 describe-security-groups --group-ids sg-xxxxx

# 3. Test connection from application host
psql -h <db-host> -U <user> -d <database>

# 4. Check connection pool settings in code
# Ensure max_connections not exceeded
```

### Memory Leak

**Symptoms:**
- Gradual memory increase over time
- OOM killer terminating processes

**Diagnosis:**
```bash
# Check memory usage trend
kubectl top pods -n incident-response

# Generate memory profile
curl http://localhost:8080/debug/pprof/heap > heap.prof
go tool pprof heap.prof
```

**Resolution:**
1. Review recent code for unbounded data structures
2. Check for unclosed database connections
3. Increase memory limit as temporary fix
4. Profile application to identify leak source

---

## Incident Response

### Incident Lifecycle

1. **Detection** - Alert fires or user report
2. **Triage** - Assess severity, page on-call
3. **Investigation** - Gather logs, metrics, traces
4. **Mitigation** - Apply fix or rollback
5. **Resolution** - Verify issue resolved
6. **Post-Mortem** - Conduct blameless review

### Incident Roles

- **Incident Commander:** Coordinates response
- **Technical Lead:** Investigates root cause
- **Communications Lead:** Updates stakeholders
- **Scribe:** Documents timeline

### Post-Incident Review Template

```markdown
# Incident Report: incident-response Outage

**Date:** YYYY-MM-DD
**Duration:** X hours Y minutes
**Severity:** P1
**Impact:** XX% of users affected

## Timeline
- 14:23 UTC: Alert fired for high error rate
- 14:25 UTC: On-call engineer paged
- 14:30 UTC: Root cause identified (database CPU 100%)
- 14:35 UTC: Mitigation applied (scaled up RDS instance)
- 14:45 UTC: Service restored, monitoring

## Root Cause
Unoptimized database query introduced in v1.2.3 caused full table scan.

## Resolution
1. Rolled back to v1.2.2
2. Scaled up RDS instance from db.t3.medium to db.t3.large
3. Added missing index to `users` table

## Action Items
- [ ] Add query performance tests to CI/CD (@engineer, ETA: 2 days)
- [ ] Review all queries for similar patterns (@team, ETA: 1 week)
- [ ] Set up database query monitoring alerts (@sre, ETA: 3 days)
```

---

## Maintenance Procedures

### Database Backup Verification

```bash
# Weekly DR drill
cd /opt/incident-response
python3 scripts/dr_drill.py

# Verify backup exists and is recent
aws s3 ls s3://backups-incident-response/latest/
```

### SSL Certificate Renewal

```bash
# Check certificate expiry
openssl s_client -connect api.example.com:443 -servername api.example.com \
  | openssl x509 -noout -dates

# Renew with Let's Encrypt
certbot renew --dry-run
certbot renew
```

### Log Rotation

```bash
# Ensure logrotate is configured
cat /etc/logrotate.d/incident-response

# Test log rotation
logrotate -d /etc/logrotate.d/incident-response
```

---

## Escalation

### On-Call Contacts

- **Primary:** PagerDuty rotation
- **Secondary:** platform-engineering@example.com
- **Escalation:** CTO (for P1 incidents >2 hours)

### External Dependencies

- **AWS Support:** https://console.aws.amazon.com/support/
- **Database Vendor:** support@vendor.com
- **CDN Provider:** https://dashboard.cdn.com/support

---

**Maintained by:** Platform Engineering Team
**Last Review:** 2025-11-10
**Next Review:** 2026-02-10
