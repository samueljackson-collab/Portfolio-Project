# Runbook — PRJ-AIML-001 (Document Packaging Pipeline)

## Overview

Production operations runbook for the Document Packaging Pipeline - an AI/ML-powered automation system for one-click generation of professional documents (DOC/PDF/XLSX) from natural language prompts.

**System Components:**
- Natural Language Processing (NLP) engine for prompt interpretation
- Document template engine (DOCX/PDF/XLSX generation)
- AI-powered content generation and formatting
- Automated quality validation and formatting checks
- Export pipeline with multi-format support
- Template library management system

**Current Status:** 🔵 Planned

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Document generation success rate** | 98% | Successful completions / total requests |
| **Average generation time** | < 30 seconds | Time from prompt → downloadable file |
| **Template rendering accuracy** | 99% | Correctly formatted outputs / total outputs |
| **API availability** | 99.5% | Uptime of generation service |
| **Concurrent request handling** | 50+ | Simultaneous document generations |
| **Content accuracy** | 95% | AI-generated content meeting requirements |

---

## Dashboards & Alerts

### Dashboards

#### Service Health Dashboard
```bash
# Check service status
systemctl status doc-pipeline-api
systemctl status doc-pipeline-worker

# Check queue status
redis-cli INFO | grep queue
redis-cli LLEN document_queue

# Check recent generations
tail -f /var/log/doc-pipeline/generation.log
```

#### Performance Dashboard
```bash
# Check generation metrics
curl http://localhost:8080/metrics | grep doc_generation

# Monitor resource usage
docker stats doc-pipeline-api doc-pipeline-worker

# Check template cache
ls -lh /var/cache/doc-templates/
du -sh /var/cache/doc-templates/
```

#### Quality Dashboard
```bash
# Review recent quality scores
cat /var/log/doc-pipeline/quality.log | tail -20

# Check error rates
grep "ERROR" /var/log/doc-pipeline/generation.log | wc -l
grep "VALIDATION_FAILED" /var/log/doc-pipeline/quality.log | tail -10
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | API service down | Immediate | Restart service, check logs |
| **P0** | Generation queue blocked | Immediate | Clear queue, restart workers |
| **P1** | Generation time > 60s | 15 minutes | Scale workers, check resource limits |
| **P1** | Success rate < 90% | 15 minutes | Investigate AI model performance |
| **P2** | Template cache miss > 20% | 30 minutes | Warm cache, check storage |
| **P2** | Worker memory > 80% | 30 minutes | Scale workers, investigate memory leak |
| **P3** | Queue depth > 100 | 1 hour | Consider scaling workers |

#### Alert Queries

```bash
# Check service availability
curl -f http://localhost:8080/health || echo "ALERT: API service unavailable"

# Check generation queue depth
QUEUE_DEPTH=$(redis-cli LLEN document_queue)
if [ $QUEUE_DEPTH -gt 100 ]; then
  echo "ALERT: Queue depth at $QUEUE_DEPTH (threshold: 100)"
fi

# Check recent error rate
ERRORS=$(grep "ERROR" /var/log/doc-pipeline/generation.log | tail -100 | wc -l)
if [ $ERRORS -gt 10 ]; then
  echo "ALERT: High error rate: $ERRORS errors in last 100 requests"
fi

# Check worker health
WORKERS=$(docker ps --filter name=doc-pipeline-worker --filter status=running -q | wc -l)
if [ $WORKERS -lt 3 ]; then
  echo "ALERT: Only $WORKERS workers running (expected: 3)"
fi
```

---

## Standard Operations

### Service Management

#### Start Services
```bash
# Start all services
docker-compose -f /opt/doc-pipeline/docker-compose.yml up -d

# Verify services are running
docker-compose -f /opt/doc-pipeline/docker-compose.yml ps

# Check service health
curl http://localhost:8080/health
curl http://localhost:8080/ready

# Tail logs
docker-compose -f /opt/doc-pipeline/docker-compose.yml logs -f
```

#### Stop Services
```bash
# Graceful shutdown (wait for current jobs)
docker-compose -f /opt/doc-pipeline/docker-compose.yml stop

# Force stop
docker-compose -f /opt/doc-pipeline/docker-compose.yml down

# Verify services are stopped
docker ps | grep doc-pipeline
```

#### Restart Services
```bash
# Restart all services
docker-compose -f /opt/doc-pipeline/docker-compose.yml restart

# Restart specific service
docker-compose -f /opt/doc-pipeline/docker-compose.yml restart doc-pipeline-api
docker-compose -f /opt/doc-pipeline/docker-compose.yml restart doc-pipeline-worker

# Rolling restart (zero downtime)
for i in {1..3}; do
  docker-compose -f /opt/doc-pipeline/docker-compose.yml restart doc-pipeline-worker-$i
  sleep 10
done
```

### Document Generation Operations

#### Manual Document Generation
```bash
# Generate document via API
curl -X POST http://localhost:8080/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a project status report for Q4 2025",
    "format": "pdf",
    "template": "status-report-v2"
  }' \
  -o output.pdf

# Check generation status
TASK_ID="abc123"
curl http://localhost:8080/api/v1/status/$TASK_ID

# Download completed document
curl http://localhost:8080/api/v1/download/$TASK_ID -o document.pdf
```

#### Batch Document Generation
```bash
# Submit batch job
curl -X POST http://localhost:8080/api/v1/batch \
  -H "Content-Type: application/json" \
  -d @batch-requests.json

# Monitor batch progress
BATCH_ID="batch-456"
curl http://localhost:8080/api/v1/batch/$BATCH_ID/status

# Download all completed documents
curl http://localhost:8080/api/v1/batch/$BATCH_ID/download -o batch-output.zip
```

#### Queue Management
```bash
# Check queue depth
redis-cli LLEN document_queue

# View queued tasks
redis-cli LRANGE document_queue 0 10

# Clear queue (emergency only)
redis-cli DEL document_queue

# Retry failed tasks
redis-cli LRANGE failed_queue 0 -1 | while read task; do
  redis-cli RPUSH document_queue "$task"
done
redis-cli DEL failed_queue
```

### Template Management

#### Update Templates
```bash
# Upload new template
curl -X POST http://localhost:8080/api/v1/templates \
  -F "template=@report-template.docx" \
  -F "name=quarterly-report" \
  -F "version=2.0"

# List available templates
curl http://localhost:8080/api/v1/templates

# Download template
curl http://localhost:8080/api/v1/templates/quarterly-report/2.0 -o template.docx

# Delete old template version
curl -X DELETE http://localhost:8080/api/v1/templates/quarterly-report/1.0
```

#### Template Cache Management
```bash
# Clear template cache
rm -rf /var/cache/doc-templates/*
docker-compose -f /opt/doc-pipeline/docker-compose.yml restart doc-pipeline-worker

# Warm template cache
curl http://localhost:8080/api/v1/cache/warm

# Check cache hit rate
redis-cli INFO | grep cache_hit_rate
```

### AI Model Operations

#### Model Health Check
```bash
# Test AI model endpoint
curl -X POST http://localhost:8081/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test prompt for model validation"}'

# Check model inference time
time curl -X POST http://localhost:8081/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Generate executive summary"}'

# Monitor model metrics
curl http://localhost:8081/metrics | grep model_inference
```

#### Update AI Model
```bash
# Download new model version
aws s3 cp s3://doc-pipeline-models/nlp-model-v2.0.pkl /opt/models/

# Backup current model
cp /opt/models/nlp-model.pkl /opt/models/backup/nlp-model-$(date +%Y%m%d).pkl

# Deploy new model
cp /opt/models/nlp-model-v2.0.pkl /opt/models/nlp-model.pkl

# Restart model service
docker-compose -f /opt/doc-pipeline/docker-compose.yml restart doc-pipeline-ml

# Validate new model
curl -X POST http://localhost:8081/api/v1/validate
```

#### Rollback AI Model
```bash
# Restore previous model version
BACKUP_DATE="20250101"
cp /opt/models/backup/nlp-model-$BACKUP_DATE.pkl /opt/models/nlp-model.pkl

# Restart service
docker-compose -f /opt/doc-pipeline/docker-compose.yml restart doc-pipeline-ml

# Verify rollback
curl http://localhost:8081/api/v1/model/version
```

### Worker Scaling

#### Scale Up Workers
```bash
# Increase worker count
docker-compose -f /opt/doc-pipeline/docker-compose.yml up -d --scale doc-pipeline-worker=6

# Verify scaling
docker ps --filter name=doc-pipeline-worker

# Monitor queue drain rate
watch "redis-cli LLEN document_queue"
```

#### Scale Down Workers
```bash
# Gracefully reduce workers
docker-compose -f /opt/doc-pipeline/docker-compose.yml up -d --scale doc-pipeline-worker=2

# Verify scaling
docker ps --filter name=doc-pipeline-worker
```

---

## Incident Response

### Detection

**Automated Detection:**
- Service health check failures (Prometheus alerts)
- Queue depth threshold exceeded
- High error rate detection
- Resource utilization alerts

**Manual Detection:**
```bash
# Check service status
docker-compose -f /opt/doc-pipeline/docker-compose.yml ps

# Check recent errors
tail -50 /var/log/doc-pipeline/errors.log

# Check queue health
redis-cli LLEN document_queue
redis-cli LLEN failed_queue

# Check API response
curl -w "\n%{http_code}\n" http://localhost:8080/health
```

### Triage

#### Severity Classification

### P0: Complete Outage
- API service unreachable
- All workers down
- Database/Redis unavailable
- Zero documents being generated

### P1: Degraded Service
- < 50% workers operational
- Generation time > 60 seconds
- Success rate < 90%
- Queue backing up (>200 items)

### P2: Warning State
- Individual worker failures
- Template rendering errors
- Elevated error rate (5-10%)
- Cache performance degradation

### P3: Informational
- Single document generation failure
- Template cache miss
- Minor performance degradation
- Non-critical warnings in logs

### Incident Response Procedures

#### P0: API Service Down

**Immediate Actions (0-2 minutes):**
```bash
# 1. Check service status
docker ps | grep doc-pipeline-api

# 2. Check logs for errors
docker logs doc-pipeline-api --tail 100

# 3. Attempt service restart
docker-compose -f /opt/doc-pipeline/docker-compose.yml restart doc-pipeline-api

# 4. Verify service recovery
curl http://localhost:8080/health
```

**Investigation (2-10 minutes):**
```bash
# Check system resources
docker stats doc-pipeline-api

# Check container logs
docker logs doc-pipeline-api --since 30m

# Check host system
df -h
free -m
top -bn1 | head -20

# Check dependencies
redis-cli PING
psql -h localhost -U postgres -c "SELECT 1"
```

**Mitigation:**
```bash
# Option 1: Restart all services
docker-compose -f /opt/doc-pipeline/docker-compose.yml restart

# Option 2: Rebuild and redeploy
cd /opt/doc-pipeline
docker-compose down
docker-compose up -d

# Option 3: Restore from backup configuration
cd /opt/doc-pipeline
git pull origin main
docker-compose up -d --build

# Verify recovery
curl http://localhost:8080/health
docker-compose ps
```

#### P1: Queue Backing Up

**Investigation:**
```bash
# Check queue depth
QUEUE_DEPTH=$(redis-cli LLEN document_queue)
echo "Current queue depth: $QUEUE_DEPTH"

# Check worker status
docker ps --filter name=doc-pipeline-worker

# Check worker logs
docker logs doc-pipeline-worker --tail 50

# Check for stuck jobs
redis-cli LRANGE processing_queue 0 -1
```

**Mitigation:**
```bash
# Scale up workers
docker-compose -f /opt/doc-pipeline/docker-compose.yml up -d --scale doc-pipeline-worker=8

# Monitor queue drain
watch "redis-cli LLEN document_queue"

# If queue not draining, investigate stuck jobs
redis-cli LRANGE processing_queue 0 -1
# Move stuck jobs back to main queue
redis-cli LRANGE processing_queue 0 -1 | while read job; do
  redis-cli LPUSH document_queue "$job"
done
redis-cli DEL processing_queue

# Restart workers
docker-compose -f /opt/doc-pipeline/docker-compose.yml restart doc-pipeline-worker
```

#### P1: High Generation Failure Rate

**Investigation:**
```bash
# Check recent errors
tail -100 /var/log/doc-pipeline/errors.log

# Check failed job queue
redis-cli LLEN failed_queue
redis-cli LRANGE failed_queue 0 10

# Analyze failure patterns
grep "FAILED" /var/log/doc-pipeline/generation.log | tail -20 | awk '{print $5}' | sort | uniq -c

# Check AI model status
curl http://localhost:8081/health
```

**Common Causes & Fixes:**

**AI Model Issues:**
```bash
# Restart ML service
docker-compose -f /opt/doc-pipeline/docker-compose.yml restart doc-pipeline-ml

# Rollback to previous model version
cp /opt/models/backup/nlp-model-$(date -d "yesterday" +%Y%m%d).pkl /opt/models/nlp-model.pkl
docker-compose -f /opt/doc-pipeline/docker-compose.yml restart doc-pipeline-ml
```

**Template Rendering Errors:**
```bash
# Clear template cache
rm -rf /var/cache/doc-templates/*

# Re-download templates
curl http://localhost:8080/api/v1/cache/warm

# Verify templates
ls -lh /var/cache/doc-templates/
```

**Resource Exhaustion:**
```bash
# Check disk space
df -h /var/lib/docker
df -h /tmp

# Clean up old documents
find /tmp/doc-pipeline -type f -mtime +7 -delete

# Clean up Docker resources
docker system prune -f
```

#### P2: Worker Memory Issues

**Investigation:**
```bash
# Check worker memory usage
docker stats doc-pipeline-worker --no-stream

# Check for memory leaks
docker logs doc-pipeline-worker | grep "OutOfMemory"

# Check worker processes
docker exec doc-pipeline-worker ps aux
```

**Mitigation:**
```bash
# Restart workers with memory limit
docker-compose -f /opt/doc-pipeline/docker-compose.yml stop doc-pipeline-worker
docker-compose -f /opt/doc-pipeline/docker-compose.yml up -d doc-pipeline-worker --memory=2g

# Scale out instead of up
docker-compose -f /opt/doc-pipeline/docker-compose.yml up -d --scale doc-pipeline-worker=6

# Monitor memory usage
watch "docker stats doc-pipeline-worker --no-stream"
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > /opt/doc-pipeline/incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Incident Report

**Date:** $(date)
**Severity:** P1
**Duration:** 25 minutes
**Affected Component:** Document generation workers

## Timeline
- 10:00: Queue depth exceeded 200 items
- 10:05: Workers found to be crashing due to memory issues
- 10:10: Workers restarted with increased memory limits
- 10:15: Workers scaled from 3 to 6 instances
- 10:25: Queue returned to normal levels

## Root Cause
Workers exhausted memory when processing large batch jobs with complex templates

## Action Items
- [ ] Implement memory limits in docker-compose.yml
- [ ] Add memory usage alerts
- [ ] Optimize template rendering for large documents
- [ ] Add worker autoscaling based on queue depth

EOF

# Update metrics
echo "$(date +%Y-%m-%d),P1,25,worker-memory" >> /opt/doc-pipeline/incidents/incident-log.csv
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### Service Issues
```bash
# Check all service status
docker-compose -f /opt/doc-pipeline/docker-compose.yml ps

# Check service logs
docker-compose -f /opt/doc-pipeline/docker-compose.yml logs -f api
docker-compose -f /opt/doc-pipeline/docker-compose.yml logs -f worker
docker-compose -f /opt/doc-pipeline/docker-compose.yml logs -f ml

# Check service health endpoints
curl http://localhost:8080/health
curl http://localhost:8081/health
curl http://localhost:6379/ping

# Check resource usage
docker stats --no-stream
```

#### Generation Issues
```bash
# Test document generation
curl -X POST http://localhost:8080/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test document", "format": "pdf"}' \
  -v

# Check generation logs
tail -f /var/log/doc-pipeline/generation.log

# Check failed jobs
redis-cli LRANGE failed_queue 0 -1

# Retry failed job
FAILED_JOB=$(redis-cli LPOP failed_queue)
redis-cli RPUSH document_queue "$FAILED_JOB"
```

#### Queue Issues
```bash
# Check queue status
redis-cli LLEN document_queue
redis-cli LLEN processing_queue
redis-cli LLEN failed_queue

# View queue contents
redis-cli LRANGE document_queue 0 10

# Clear specific queue
redis-cli DEL failed_queue

# Move jobs between queues
redis-cli LMOVE failed_queue document_queue LEFT RIGHT
```

#### Performance Issues
```bash
# Check API response time
time curl http://localhost:8080/health

# Check generation time
time curl -X POST http://localhost:8080/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Quick test", "format": "pdf"}' \
  -o test.pdf

# Check worker throughput
docker logs doc-pipeline-worker --since 1h | grep "Document generated" | wc -l

# Check cache performance
redis-cli INFO stats | grep cache
```

### Common Issues & Solutions

#### Issue: "Generation timeout"

**Symptoms:**
- Document generation takes > 60 seconds
- Timeout errors in logs
- Requests failing with 504 Gateway Timeout

**Diagnosis:**
```bash
# Check worker status
docker stats doc-pipeline-worker --no-stream

# Check AI model response time
time curl -X POST http://localhost:8081/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test"}'

# Check queue depth
redis-cli LLEN document_queue
```

**Solution:**
```bash
# Scale up workers
docker-compose -f /opt/doc-pipeline/docker-compose.yml up -d --scale doc-pipeline-worker=6

# Optimize AI model (reduce max tokens)
# Edit configuration and restart ML service
docker-compose -f /opt/doc-pipeline/docker-compose.yml restart doc-pipeline-ml

# Increase timeout settings
# Update nginx.conf or API gateway timeout
```

---

#### Issue: "Template not found"

**Symptoms:**
- Generation fails with template error
- Missing template files in cache
- Template rendering errors

**Diagnosis:**
```bash
# List available templates
curl http://localhost:8080/api/v1/templates

# Check template cache
ls -lh /var/cache/doc-templates/

# Check template access permissions
ls -la /var/cache/doc-templates/
```

**Solution:**
```bash
# Re-download templates
curl http://localhost:8080/api/v1/cache/warm

# Manually upload template
curl -X POST http://localhost:8080/api/v1/templates \
  -F "template=@missing-template.docx" \
  -F "name=report-template" \
  -F "version=1.0"

# Fix permissions
chown -R docpipeline:docpipeline /var/cache/doc-templates/
chmod -R 755 /var/cache/doc-templates/
```

---

#### Issue: "AI model inference failing"

**Symptoms:**
- Content generation errors
- Poor quality output
- Model timeout errors

**Diagnosis:**
```bash
# Check ML service
curl http://localhost:8081/health

# Test model inference
curl -X POST http://localhost:8081/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test prompt"}'

# Check model logs
docker logs doc-pipeline-ml --tail 100

# Check GPU/CPU usage (if applicable)
nvidia-smi  # For GPU
docker stats doc-pipeline-ml --no-stream
```

**Solution:**
```bash
# Restart ML service
docker-compose -f /opt/doc-pipeline/docker-compose.yml restart doc-pipeline-ml

# Rollback to previous model
cp /opt/models/backup/nlp-model-stable.pkl /opt/models/nlp-model.pkl
docker-compose -f /opt/doc-pipeline/docker-compose.yml restart doc-pipeline-ml

# Scale ML service if needed
docker-compose -f /opt/doc-pipeline/docker-compose.yml up -d --scale doc-pipeline-ml=2
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 1 hour (database snapshots)
- **RTO** (Recovery Time Objective): 15 minutes (service restoration)

### Backup Strategy

**Configuration Backups:**
```bash
# Backup configuration files
tar -czf /backup/config-$(date +%Y%m%d).tar.gz \
  /opt/doc-pipeline/docker-compose.yml \
  /opt/doc-pipeline/.env \
  /opt/doc-pipeline/nginx.conf

# Backup templates
tar -czf /backup/templates-$(date +%Y%m%d).tar.gz \
  /var/cache/doc-templates/

# Backup AI models
tar -czf /backup/models-$(date +%Y%m%d).tar.gz \
  /opt/models/
```

**Database Backups:**
```bash
# Backup PostgreSQL database
pg_dump -h localhost -U postgres doc_pipeline > /backup/db-$(date +%Y%m%d).sql

# Backup Redis data
redis-cli SAVE
cp /var/lib/redis/dump.rdb /backup/redis-$(date +%Y%m%d).rdb

# Automated daily backup
cat > /etc/cron.daily/doc-pipeline-backup << 'EOF'
#!/bin/bash
pg_dump -h localhost -U postgres doc_pipeline | gzip > /backup/db-$(date +%Y%m%d).sql.gz
redis-cli SAVE && cp /var/lib/redis/dump.rdb /backup/redis-$(date +%Y%m%d).rdb
find /backup -type f -mtime +30 -delete
EOF
chmod +x /etc/cron.daily/doc-pipeline-backup
```

### Disaster Recovery Procedures

#### Complete Service Recovery

**Recovery Steps (10-15 minutes):**
```bash
# 1. Restore configuration
cd /opt/doc-pipeline
tar -xzf /backup/config-latest.tar.gz -C /

# 2. Restore database
psql -h localhost -U postgres doc_pipeline < /backup/db-latest.sql

# 3. Restore Redis data
redis-cli SHUTDOWN
cp /backup/redis-latest.rdb /var/lib/redis/dump.rdb
redis-server &

# 4. Restore templates and models
tar -xzf /backup/templates-latest.tar.gz -C /
tar -xzf /backup/models-latest.tar.gz -C /

# 5. Start services
docker-compose -f /opt/doc-pipeline/docker-compose.yml up -d

# 6. Verify recovery
curl http://localhost:8080/health
docker-compose ps
```

#### Database Recovery Only
```bash
# Stop services
docker-compose -f /opt/doc-pipeline/docker-compose.yml stop

# Restore database
psql -h localhost -U postgres doc_pipeline < /backup/db-$(date +%Y%m%d).sql

# Start services
docker-compose -f /opt/doc-pipeline/docker-compose.yml start

# Verify
curl http://localhost:8080/api/v1/templates
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks
```bash
# Check service health
curl http://localhost:8080/health
docker-compose -f /opt/doc-pipeline/docker-compose.yml ps

# Check queue status
redis-cli LLEN document_queue
redis-cli LLEN failed_queue

# Check error logs
tail -20 /var/log/doc-pipeline/errors.log

# Monitor disk usage
df -h /var/lib/docker
df -h /tmp
```

#### Weekly Tasks
```bash
# Review generation metrics
grep "Document generated" /var/log/doc-pipeline/generation.log | tail -1000 | \
  awk '{sum+=$8; count++} END {print "Average: " sum/count "s"}'

# Clean up old temporary files
find /tmp/doc-pipeline -type f -mtime +7 -delete

# Review and archive logs
cd /var/log/doc-pipeline
gzip generation.log.1
mv generation.log.1.gz archive/

# Update documentation
git pull /opt/doc-pipeline
```

#### Monthly Tasks
```bash
# Update dependencies
cd /opt/doc-pipeline
docker-compose pull
docker-compose up -d

# Review and optimize templates
curl http://localhost:8080/api/v1/templates | jq .

# Review AI model performance
# Update model if new version available

# Backup verification
tar -tzf /backup/config-latest.tar.gz
psql -h localhost -U postgres doc_pipeline < /backup/db-latest.sql --dry-run

# Capacity planning review
# Check trends: queue depth, generation time, error rates
```

### Upgrade Procedures

#### Update Application Version
```bash
# 1. Backup current state
tar -czf /backup/pre-upgrade-$(date +%Y%m%d).tar.gz /opt/doc-pipeline

# 2. Pull new version
cd /opt/doc-pipeline
git fetch origin
git checkout v2.0.0

# 3. Update dependencies
docker-compose pull

# 4. Stop services
docker-compose down

# 5. Run migrations if needed
docker-compose run --rm api python manage.py migrate

# 6. Start services
docker-compose up -d

# 7. Verify upgrade
curl http://localhost:8080/health
curl http://localhost:8080/api/v1/version

# 8. Monitor for issues
docker-compose logs -f --tail 100
```

---

## Operational Best Practices

### Pre-Deployment Checklist
- [ ] All tests passing locally
- [ ] Database migrations prepared
- [ ] Configuration files updated
- [ ] Templates validated
- [ ] AI model tested
- [ ] Backup completed
- [ ] Rollback plan documented

### Post-Deployment Checklist
- [ ] All services running
- [ ] Health checks passing
- [ ] Sample document generation successful
- [ ] Queue processing normally
- [ ] No errors in logs
- [ ] Performance metrics normal
- [ ] Monitor for 30 minutes

### Standard Change Window
- **Time:** Tuesday/Thursday, 10:00 AM - 12:00 PM ET
- **Approval:** Required for ML model updates
- **Blackout:** Avoid Friday deployments, month-end

### Escalation Path

| Level | Role | Response Time | Contact |
|-------|------|---------------|---------|
| L1 | On-call engineer | 15 minutes | Slack #doc-pipeline |
| L2 | Platform lead | 30 minutes | Direct message |
| L3 | Engineering manager | 1 hour | Phone call |

---

## References

### Internal Documentation
- [PRJ-AIML-001 README](./README.md)
- [API Documentation](./docs/api.md)
- [Template Guide](./docs/templates.md)
- [Architecture Overview](./docs/architecture.md)

### External Resources
- [OpenAI GPT Documentation](https://platform.openai.com/docs/)
- [Python-DOCX Documentation](https://python-docx.readthedocs.io/)
- [ReportLab PDF Documentation](https://www.reportlab.com/docs/)
- [Redis Documentation](https://redis.io/documentation)

### Emergency Contacts
- **On-call rotation:** See internal wiki
- **Slack channels:** #doc-pipeline, #incidents
- **Escalation:** Follow escalation path above

---

## Quick Reference Card

### Most Common Operations
```bash
# Check service health
curl http://localhost:8080/health
docker-compose -f /opt/doc-pipeline/docker-compose.yml ps

# Generate document
curl -X POST http://localhost:8080/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Your prompt", "format": "pdf"}'

# Check queue
redis-cli LLEN document_queue

# View logs
docker-compose -f /opt/doc-pipeline/docker-compose.yml logs -f

# Scale workers
docker-compose -f /opt/doc-pipeline/docker-compose.yml up -d --scale doc-pipeline-worker=6

# Restart services
docker-compose -f /opt/doc-pipeline/docker-compose.yml restart
```

### Emergency Response
```bash
# P0: Service down
docker-compose -f /opt/doc-pipeline/docker-compose.yml restart
curl http://localhost:8080/health

# P1: Queue backing up
docker-compose -f /opt/doc-pipeline/docker-compose.yml up -d --scale doc-pipeline-worker=8
watch "redis-cli LLEN document_queue"

# P2: AI model issues
docker-compose -f /opt/doc-pipeline/docker-compose.yml restart doc-pipeline-ml
docker logs doc-pipeline-ml --tail 100
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** AI/ML Automation Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates
