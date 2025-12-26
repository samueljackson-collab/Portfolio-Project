# Runbook — P09 (Cloud-Native POC Deployment)

## Overview

Production operations runbook for the FastAPI cloud-native application. This runbook covers container operations, database management, API monitoring, incident response, and troubleshooting procedures for the Dockerized FastAPI application with SQLite backend.

**System Components:**
- FastAPI REST API application
- SQLite database with SQLAlchemy ORM
- Docker containerization
- Uvicorn ASGI server
- Health check endpoints (/health, /ready)
- Structured logging (JSON format)
- pytest test suite

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Application availability** | 99.5% | Health check uptime |
| **API response time (p95)** | < 200ms | 95th percentile latency |
| **Error rate** | < 1% | 5xx errors / Total requests |
| **Container restart rate** | < 3/day | Docker restart count |
| **Database query time (p95)** | < 50ms | SQLAlchemy query timing |
| **Test coverage** | > 90% | pytest coverage report |

---

## Dashboards & Alerts

### Dashboards

#### Application Health Dashboard
```bash
# Check application health
curl http://localhost:8000/health

# Expected: {"status": "healthy"}

# Check readiness
curl http://localhost:8000/ready

# Expected: {"status": "ready", "database": "connected"}

# Check API docs
curl http://localhost:8000/docs
# Opens Swagger UI
```

#### Container Status Dashboard
```bash
# Check container status
docker ps | grep cloud-native-poc

# View container stats
docker stats cloud-native-poc --no-stream

# Check container health
docker inspect cloud-native-poc | jq '.[0].State.Health'

# View recent container events
docker events --filter container=cloud-native-poc --since 1h
```

#### Performance Metrics Dashboard
```bash
# Check Prometheus metrics (if enabled)
curl http://localhost:8000/metrics

# Parse response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/items

# curl-format.txt:
# time_total: %{time_total}s
# time_connect: %{time_connect}s
# time_starttransfer: %{time_starttransfer}s
```

#### Database Dashboard
```bash
# Check database size
ls -lh data/app.db

# Count records
sqlite3 data/app.db "SELECT COUNT(*) FROM items;"

# Check database integrity
sqlite3 data/app.db "PRAGMA integrity_check;"

# View database schema
sqlite3 data/app.db ".schema"
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Container down | Immediate | Restart container, check logs |
| **P0** | Health check failing | Immediate | Investigate app, check database |
| **P1** | Error rate > 5% | 15 minutes | Check logs, rollback if needed |
| **P1** | Response time > 1s (p95) | 30 minutes | Investigate performance |
| **P2** | Database file locked | 1 hour | Check concurrent connections |
| **P2** | Disk usage > 80% | 2 hours | Clean up logs, expand storage |
| **P3** | Memory usage > 90% | 4 hours | Investigate memory leak |

#### Alert Queries

**Check container health:**
```bash
# Container running?
docker inspect cloud-native-poc | jq -e '.[0].State.Running' || \
  echo "ALERT: Container not running"

# Health check passing?
curl -f http://localhost:8000/health || \
  echo "ALERT: Health check failing"

# Check exit code if stopped
docker inspect cloud-native-poc | jq '.[0].State.ExitCode'
```

**Monitor error rate:**
```bash
# Count recent errors in logs
docker logs cloud-native-poc --since 5m 2>&1 | \
  jq -r 'select(.level == "ERROR")' | wc -l

# Alert if > 10 errors in 5 minutes
[ $(docker logs cloud-native-poc --since 5m 2>&1 | grep -c "ERROR") -gt 10 ] && \
  echo "ALERT: High error rate"
```

**Check resource usage:**
```bash
# Memory usage
MEM_USAGE=$(docker stats cloud-native-poc --no-stream --format "{{.MemPerc}}" | sed 's/%//')
[ "${MEM_USAGE%.*}" -gt 90 ] && echo "ALERT: High memory usage: ${MEM_USAGE}%"

# CPU usage
CPU_USAGE=$(docker stats cloud-native-poc --no-stream --format "{{.CPUPerc}}" | sed 's/%//')
[ "${CPU_USAGE%.*}" -gt 80 ] && echo "ALERT: High CPU usage: ${CPU_USAGE}%"
```

---

## Standard Operations

### Container Management

#### Start Application
```bash
# Start with Docker Compose
make run

# Or manually
docker-compose up -d

# Start with specific configuration
docker-compose up -d --build

# Verify startup
docker ps | grep cloud-native-poc
curl http://localhost:8000/health
```

#### Stop Application
```bash
# Graceful stop
make stop

# Or manually
docker-compose down

# Stop but keep data volumes
docker-compose stop

# Force stop if unresponsive
docker stop -t 30 cloud-native-poc
```

#### Restart Application
```bash
# Restart container
docker-compose restart

# Or specific service
docker restart cloud-native-poc

# Rebuild and restart
make build
make run

# Zero-downtime restart (if using multiple containers)
docker-compose up -d --no-deps --build app
```

### Application Deployment

#### Deploy New Version
```bash
# 1. Pull latest code
git pull origin main

# 2. Run tests
make test

# 3. Build new image
make build

# 4. Tag image
docker tag cloud-native-poc:latest cloud-native-poc:v1.2.0

# 5. Stop old container
docker-compose down

# 6. Start new version
docker-compose up -d

# 7. Verify deployment
curl http://localhost:8000/health
curl http://localhost:8000/api/items

# 8. Monitor logs
docker logs -f cloud-native-poc
```

#### Rollback Deployment
```bash
# 1. Identify previous version
docker images cloud-native-poc

# 2. Stop current container
docker-compose down

# 3. Run previous version
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  --name cloud-native-poc \
  cloud-native-poc:v1.1.0

# 4. Verify rollback
curl http://localhost:8000/health

# 5. Update docker-compose.yml if needed
vi docker-compose.yml
# Change image: cloud-native-poc:v1.1.0
```

### Database Operations

#### Backup Database
```bash
# Stop application to ensure consistency
docker-compose stop

# Backup database file
cp data/app.db backups/app-$(date +%Y%m%d-%H%M).db

# Compress backup
gzip backups/app-$(date +%Y%m%d-%H%M).db

# Restart application
docker-compose start

# Or online backup (hot backup)
sqlite3 data/app.db ".backup backups/app-$(date +%Y%m%d-%H%M).db"
```

#### Restore Database
```bash
# 1. Stop application
docker-compose stop

# 2. Backup current database
cp data/app.db data/app.db.before-restore

# 3. Restore from backup
gunzip -c backups/app-20251110-1200.db.gz > data/app.db

# Or copy directly
cp backups/app-20251110-1200.db data/app.db

# 4. Verify integrity
sqlite3 data/app.db "PRAGMA integrity_check;"

# 5. Restart application
docker-compose start

# 6. Verify
curl http://localhost:8000/api/items
```

#### Database Maintenance
```bash
# Vacuum database (reclaim space)
sqlite3 data/app.db "VACUUM;"

# Analyze database (update statistics)
sqlite3 data/app.db "ANALYZE;"

# Check integrity
sqlite3 data/app.db "PRAGMA integrity_check;"

# Rebuild indexes
sqlite3 data/app.db << 'EOF'
REINDEX;
ANALYZE;
EOF

# View database statistics
sqlite3 data/app.db << 'EOF'
.dbinfo
EOF
```

### Log Management

#### View Logs
```bash
# Follow logs in real-time
docker logs -f cloud-native-poc

# Last 100 lines
docker logs --tail 100 cloud-native-poc

# Logs from last hour
docker logs --since 1h cloud-native-poc

# Filter for errors
docker logs cloud-native-poc 2>&1 | jq -r 'select(.level == "ERROR")'

# Filter by endpoint
docker logs cloud-native-poc 2>&1 | jq -r 'select(.path == "/api/items")'
```

#### Export Logs
```bash
# Export to file
docker logs cloud-native-poc > logs/app-$(date +%Y%m%d).log

# Export JSON logs
docker logs cloud-native-poc 2>&1 | jq '.' > logs/app-$(date +%Y%m%d).json

# Compress old logs
gzip logs/app-$(date -d '7 days ago' +%Y%m%d).log
```

### Testing

#### Run Tests
```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# View coverage report
open htmlcov/index.html

# Run specific test file
pytest tests/test_api.py -v

# Run in Docker
make test-docker
```

---

## Incident Response

### Detection

**Automated Detection:**
- Health check monitoring
- Container restart events
- Log error patterns

**Manual Detection:**
```bash
# Check application health
curl http://localhost:8000/health

# Check container status
docker ps -a | grep cloud-native-poc

# Check recent errors
docker logs --tail 100 cloud-native-poc 2>&1 | grep -i error

# Test API endpoints
curl http://localhost:8000/api/items
```

### Triage

#### Severity Classification

**P0: Application Down**
- Container stopped/crashed
- Health check returning 500
- Database corrupted
- All API requests failing

**P1: Degraded Service**
- Error rate > 5%
- Response time > 1 second
- Some API endpoints failing
- Database locked

**P2: Performance Issues**
- Response time 500ms-1s
- Memory usage > 90%
- Slow database queries
- Error rate 1-5%

**P3: Minor Issues**
- Individual request failures
- Warning logs
- Non-critical endpoint issues

### Incident Response Procedures

#### P0: Container Crashed

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check container status
docker ps -a | grep cloud-native-poc

# 2. Check exit code
docker inspect cloud-native-poc | jq '.[0].State'

# 3. View recent logs
docker logs --tail 200 cloud-native-poc

# 4. Attempt restart
docker start cloud-native-poc

# 5. Verify
curl http://localhost:8000/health
```

**Investigation (5-15 minutes):**
```bash
# Check crash logs
docker logs cloud-native-poc 2>&1 | tail -100

# Check for OOM kill
dmesg | grep -i oom

# Check disk space
df -h

# Check database file
ls -lh data/app.db
sqlite3 data/app.db "PRAGMA integrity_check;"

# Review recent changes
git log --oneline -5
```

**Recovery:**
```bash
# If database corrupt: Restore from backup
docker-compose stop
cp backups/app-latest.db data/app.db
docker-compose start

# If container issue: Rebuild
docker-compose down
docker-compose up -d --build

# If code issue: Rollback
git checkout <previous-commit>
docker-compose up -d --build

# Verify recovery
curl http://localhost:8000/health
curl http://localhost:8000/api/items
```

#### P0: Health Check Failing

**Investigation:**
```bash
# 1. Check health endpoint directly
curl -v http://localhost:8000/health

# 2. Check readiness endpoint
curl -v http://localhost:8000/ready

# 3. Check container logs
docker logs --tail 50 cloud-native-poc

# 4. Check database connection
docker exec cloud-native-poc sqlite3 /app/data/app.db "SELECT 1;"

# 5. Check application process
docker exec cloud-native-poc ps aux
```

**Common Causes & Fixes:**

**Database Locked:**
```bash
# Check for lock file
ls -la data/app.db-*

# Kill processes holding lock
fuser data/app.db

# Or restart container
docker restart cloud-native-poc
```

**Port Already in Use:**
```bash
# Check what's using port 8000
lsof -i :8000

# Kill conflicting process
kill $(lsof -ti :8000)

# Or change port in docker-compose.yml
vi docker-compose.yml
# ports: - "8001:8000"
```

**Database Connection Error:**
```bash
# Check database file permissions
ls -l data/app.db

# Fix permissions
chmod 644 data/app.db
chown 1000:1000 data/app.db  # Match container user

# Restart container
docker restart cloud-native-poc
```

#### P1: High Error Rate

**Investigation:**
```bash
# 1. Count errors by type
docker logs cloud-native-poc --since 1h 2>&1 | \
  jq -r 'select(.level == "ERROR") | .message' | sort | uniq -c

# 2. Check specific error details
docker logs cloud-native-poc 2>&1 | jq 'select(.level == "ERROR")' | head -5

# 3. Check which endpoints are failing
docker logs cloud-native-poc 2>&1 | \
  jq -r 'select(.status_code >= 500) | .path' | sort | uniq -c

# 4. Test failing endpoint
curl -v http://localhost:8000/api/items/999
```

**Mitigation:**
```bash
# If database issue: Check locks
sqlite3 data/app.db "PRAGMA locking_mode;"

# If specific endpoint: Check code
docker exec cloud-native-poc cat /app/app/main.py

# If validation error: Check request format
# Review API documentation: http://localhost:8000/docs

# If resource exhaustion: Restart
docker restart cloud-native-poc
```

#### P2: Performance Degradation

**Investigation:**
```bash
# 1. Measure response time
time curl http://localhost:8000/api/items

# 2. Check database query performance
docker exec cloud-native-poc sqlite3 /app/data/app.db << 'EOF'
.timer on
SELECT * FROM items LIMIT 100;
EOF

# 3. Check container resources
docker stats cloud-native-poc --no-stream

# 4. Check database size
ls -lh data/app.db

# 5. Profile with logs
docker logs cloud-native-poc 2>&1 | \
  jq -r 'select(.duration_ms != null) | .duration_ms' | \
  awk '{sum+=$1; count++} END {print "Avg:", sum/count "ms"}'
```

**Mitigation:**
```bash
# Optimize database
sqlite3 data/app.db << 'EOF'
VACUUM;
ANALYZE;
REINDEX;
EOF

# Add database indexes (if missing)
sqlite3 data/app.db << 'EOF'
CREATE INDEX IF NOT EXISTS idx_items_created ON items(created_at);
EOF

# Restart container to clear memory
docker restart cloud-native-poc

# Increase container resources
vi docker-compose.yml
# Add:
# deploy:
#   resources:
#     limits:
#       memory: 512M
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Application Incident Report

**Date:** $(date)
**Severity:** P0
**Duration:** 20 minutes
**Component:** FastAPI Application

## Timeline
- 15:00: Health check started failing
- 15:05: Identified database lock issue
- 15:10: Restarted container
- 15:15: Database lock cleared
- 15:20: Service restored

## Root Cause
Database file locked by orphaned process after abnormal shutdown

## Action Items
- [ ] Implement proper database connection pooling
- [ ] Add lock timeout configuration
- [ ] Improve graceful shutdown handling
- [ ] Add database lock monitoring

EOF

# Update metrics
docker stats cloud-native-poc --no-stream >> metrics/daily-stats.txt
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### Container Issues
```bash
# Check container status
docker ps -a | grep cloud-native-poc

# Inspect container
docker inspect cloud-native-poc | jq '.'

# Check resource usage
docker stats cloud-native-poc

# Check container networks
docker network inspect bridge

# View container mounts
docker inspect cloud-native-poc | jq '.[0].Mounts'
```

#### Application Issues
```bash
# Execute command in container
docker exec cloud-native-poc ls -la /app

# Check Python version
docker exec cloud-native-poc python --version

# Check installed packages
docker exec cloud-native-poc pip list

# Test database connection
docker exec cloud-native-poc python -c "from app.database import get_db; print('DB OK')"

# Get shell access
docker exec -it cloud-native-poc /bin/sh
```

#### Database Issues
```bash
# Check database file
ls -lh data/app.db*

# Count records
sqlite3 data/app.db "SELECT COUNT(*) FROM items;"

# Check table schema
sqlite3 data/app.db ".schema items"

# Check database locks
fuser data/app.db

# Analyze database
sqlite3 data/app.db << 'EOF'
PRAGMA integrity_check;
PRAGMA foreign_key_check;
PRAGMA quick_check;
EOF
```

### Common Issues & Solutions

#### Issue: Container won't start

**Symptoms:**
```bash
$ docker-compose up
Error: Cannot start container...
```

**Diagnosis:**
```bash
# Check logs
docker logs cloud-native-poc

# Check port conflicts
lsof -i :8000

# Check volume mounts
docker inspect cloud-native-poc | jq '.[0].Mounts'

# Check image
docker images cloud-native-poc
```

**Solution:**
```bash
# Remove old container
docker rm -f cloud-native-poc

# Clean volumes if corrupt
docker volume ls
docker volume rm cloud-native-poc_data

# Rebuild image
docker-compose build --no-cache

# Start fresh
docker-compose up -d
```

---

#### Issue: API returning 500 errors

**Symptoms:**
```bash
$ curl http://localhost:8000/api/items
{"detail": "Internal Server Error"}
```

**Diagnosis:**
```bash
# Check logs
docker logs --tail 50 cloud-native-poc

# Check database
docker exec cloud-native-poc sqlite3 /app/data/app.db "SELECT 1;"

# Test health endpoint
curl http://localhost:8000/health

# Check for Python errors
docker logs cloud-native-poc 2>&1 | grep -i "traceback"
```

**Solution:**
```bash
# If database issue: Check permissions
ls -l data/app.db
chmod 644 data/app.db

# If code issue: Check application logs
docker logs cloud-native-poc 2>&1 | jq 'select(.level == "ERROR")'

# Restart application
docker restart cloud-native-poc

# If persistent: Rollback
git checkout <previous-commit>
docker-compose up -d --build
```

---

#### Issue: Database file locked

**Symptoms:**
```bash
sqlite3.OperationalError: database is locked
```

**Diagnosis:**
```bash
# Check for lock file
ls -la data/app.db-*

# Check processes accessing database
fuser data/app.db

# Check database mode
sqlite3 data/app.db "PRAGMA locking_mode;"
```

**Solution:**
```bash
# Stop application
docker-compose stop

# Remove lock files
rm data/app.db-shm data/app.db-wal

# Restart
docker-compose start

# Or force unlock (risky)
sqlite3 data/app.db "PRAGMA locking_mode=NORMAL;"
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 1 hour (hourly database backups)
- **RTO** (Recovery Time Objective): 10 minutes (restore + restart)

### Backup Strategy

**Automated Backups:**
```bash
# Hourly backup script
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="backups"
DATE=$(date +%Y%m%d-%H%M)

# Backup database
sqlite3 data/app.db ".backup ${BACKUP_DIR}/app-${DATE}.db"

# Compress
gzip ${BACKUP_DIR}/app-${DATE}.db

# Clean old backups (keep 7 days)
find ${BACKUP_DIR} -name "app-*.db.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_DIR}/app-${DATE}.db.gz"
EOF

chmod +x scripts/backup.sh

# Add to crontab
crontab -e
# 0 * * * * /path/to/scripts/backup.sh
```

**Manual Backups:**
```bash
# Before deployment
sqlite3 data/app.db ".backup backups/app-pre-deploy-$(date +%Y%m%d).db"

# Before maintenance
docker-compose stop
cp data/app.db backups/app-maintenance-$(date +%Y%m%d).db
docker-compose start
```

### Disaster Recovery Procedures

#### Complete Data Loss

**Recovery Steps (10-15 minutes):**
```bash
# 1. Stop application
docker-compose down

# 2. Restore database from latest backup
gunzip -c backups/app-latest.db.gz > data/app.db

# 3. Verify database integrity
sqlite3 data/app.db "PRAGMA integrity_check;"

# 4. Restore permissions
chmod 644 data/app.db

# 5. Start application
docker-compose up -d

# 6. Verify functionality
curl http://localhost:8000/health
curl http://localhost:8000/api/items

# 7. Run tests
make test
```

#### Container Image Loss

**Recovery Steps (5-10 minutes):**
```bash
# 1. Pull from Git
git pull origin main

# 2. Rebuild image
docker-compose build

# 3. Start application
docker-compose up -d

# 4. Verify
curl http://localhost:8000/health
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks
```bash
# Check application health
curl http://localhost:8000/health

# Check container status
docker ps | grep cloud-native-poc

# Review logs for errors
docker logs --since 24h cloud-native-poc 2>&1 | jq 'select(.level == "ERROR")'

# Backup database
sqlite3 data/app.db ".backup backups/app-$(date +%Y%m%d).db"
```

#### Weekly Tasks
```bash
# Check disk usage
df -h data/
ls -lh data/app.db

# Database maintenance
sqlite3 data/app.db "VACUUM; ANALYZE;"

# Review container logs
docker logs cloud-native-poc > logs/app-weekly-$(date +%Y%m%d).log

# Run tests
make test

# Check for updates
docker pull python:3.11-slim
```

#### Monthly Tasks
```bash
# Rotate logs
tar -czf logs/archive-$(date +%Y%m).tar.gz logs/*.log
find logs/ -name "*.log" -mtime +30 -delete

# Clean old backups
find backups/ -name "app-*.db.gz" -mtime +30 -delete

# Review and optimize database
sqlite3 data/app.db << 'EOF'
VACUUM;
REINDEX;
ANALYZE;
EOF

# Update dependencies
vi requirements.txt
docker-compose build
```

---

## Quick Reference

### Common Commands
```bash
# Start application
make run

# Stop application
make stop

# View logs
docker logs -f cloud-native-poc

# Run tests
make test

# Backup database
sqlite3 data/app.db ".backup backups/app-$(date +%Y%m%d).db"

# Restart application
docker restart cloud-native-poc
```

### Emergency Response
```bash
# P0: Container crashed - restart
docker start cloud-native-poc

# P0: Health failing - check logs
docker logs --tail 100 cloud-native-poc

# P0: Database corrupt - restore
cp backups/app-latest.db data/app.db && docker restart cloud-native-poc

# P1: High errors - restart
docker restart cloud-native-poc

# P2: Database locked - remove locks
rm data/app.db-shm data/app.db-wal && docker restart cloud-native-poc
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Platform Engineering Team
- **Review Schedule:** Quarterly or after major application changes
- **Feedback:** Create issue or submit PR with updates

## Evidence & Verification

Verification summary: Baseline evidence captured to validate the latest quickstart configuration and document supporting artifacts for audits.

**Evidence artifacts**
- [Screenshot](./docs/evidence/screenshot.svg)
- [Run log](./docs/evidence/run-log.txt)
- [Dashboard export](./docs/evidence/dashboard-export.json)
- [Load test summary](./docs/evidence/load-test-summary.txt)

### Evidence Checklist

| Evidence Item | Location | Status |
| --- | --- | --- |
| Screenshot captured | `docs/evidence/screenshot.svg` | ✅ |
| Run log captured | `docs/evidence/run-log.txt` | ✅ |
| Dashboard export captured | `docs/evidence/dashboard-export.json` | ✅ |
| Load test summary captured | `docs/evidence/load-test-summary.txt` | ✅ |
