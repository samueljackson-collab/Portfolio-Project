# Runbook — P13 (High-Availability Web Application)

## Overview

Production operations runbook for the P13 High-Availability Web Application platform. This runbook
covers load balancer management, application instance operations, database replication, health
monitoring, incident response, and troubleshooting for the NGINX-based HA architecture.

**System Components:**

- NGINX load balancer with upstream health checks
- Multiple application instances (3 replicas) with Docker Compose
- Database replication (primary-replica configuration)
- Health check endpoints (/health, /ready)
- Rolling deployment capability
- Monitoring and metrics collection

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Application availability** | 99.9% | Health check success rate across all instances |
| **Load balancer uptime** | 99.95% | NGINX process availability |
| **Request success rate** | 99.5% | HTTP 2XX responses / total requests |
| **Response time (p95)** | < 200ms | NGINX access log analysis |
| **Database replication lag** | < 5 seconds | Replication delay monitoring |
| **Failover time (RTO)** | < 30 seconds | Time to detect and route around failed instance |
| **Zero-downtime deployment** | 100% | Rolling updates with no 5XX errors |

---

## Dashboards & Alerts

### Dashboards

#### Load Balancer Dashboard

```bash
# Check NGINX status
docker-compose ps nginx

# Check NGINX access logs (recent requests)
docker-compose logs nginx --tail=100 | grep -v "GET /health\|GET /ready"

# Check upstream status
docker-compose exec nginx cat /etc/nginx/conf.d/upstream.conf

# Get request statistics
docker-compose logs nginx | grep -E "HTTP/[0-9]" | \
  awk '{print $9}' | sort | uniq -c | sort -rn

# Check active connections
docker-compose exec nginx nginx -T | grep -A 5 "upstream backend"
```

#### Application Instance Dashboard

```bash
# Check all app instances
docker-compose ps | grep app

# Check instance health
for i in 1 2 3; do
  echo "=== App Instance $i ==="
  docker-compose exec app-$i curl -s http://localhost:8000/health || echo "Health check failed"
  docker-compose exec app-$i curl -s http://localhost:8000/ready || echo "Ready check failed"
done

# Check resource usage
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Check instance logs
docker-compose logs app-1 app-2 app-3 --tail=50 --follow
```

#### Database Replication Dashboard

```bash
# Check primary database status
docker-compose exec db-primary psql -U postgres -c "SELECT pg_is_in_recovery();"

# Check replica status
docker-compose exec db-replica psql -U postgres -c "SELECT pg_is_in_recovery();"

# Check replication lag
docker-compose exec db-replica psql -U postgres -c "
SELECT
  now() - pg_last_xact_replay_timestamp() AS replication_lag,
  pg_last_xact_replay_timestamp() AS last_replay_time;
"

# Check replication status on primary
docker-compose exec db-primary psql -U postgres -c "
SELECT
  client_addr,
  state,
  sent_lsn,
  write_lsn,
  flush_lsn,
  replay_lsn,
  sync_state
FROM pg_stat_replication;
"

# Check connection counts
docker-compose exec db-primary psql -U postgres -c "
SELECT count(*) as connections, state
FROM pg_stat_activity
WHERE datname='appdb'
GROUP BY state;
"
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | All app instances down | Immediate | Emergency restart, check logs |
| **P0** | Load balancer down | Immediate | Restart NGINX, verify configuration |
| **P0** | Primary database down | Immediate | Promote replica, investigate primary |
| **P1** | 2 of 3 app instances down | 5 minutes | Restart failed instances, investigate |
| **P1** | Replication lag > 60 seconds | 15 minutes | Check network, investigate DB load |
| **P1** | 5XX error rate > 1% | 15 minutes | Check app logs, rollback if recent deploy |
| **P2** | Single app instance down | 30 minutes | Investigate and restart instance |
| **P2** | Response time > 500ms (p95) | 30 minutes | Check DB performance, optimize queries |
| **P3** | High memory usage (>80%) | 1 hour | Review and optimize, consider scaling |

#### Alert Queries

```bash
# Check for unhealthy instances
for i in 1 2 3; do
  STATUS=$(docker-compose exec nginx curl -s -o /dev/null -w "%{http_code}" http://app-$i:8000/health)
  if [ "$STATUS" != "200" ]; then
    echo "ALERT: app-$i unhealthy (HTTP $STATUS)"
  fi
done

# Check error rate in logs
ERROR_COUNT=$(docker-compose logs nginx --since 10m | grep -c " 5[0-9][0-9] ")
TOTAL_COUNT=$(docker-compose logs nginx --since 10m | grep -c "HTTP/")
if [ $TOTAL_COUNT -gt 0 ]; then
  ERROR_RATE=$(echo "scale=2; 100 * $ERROR_COUNT / $TOTAL_COUNT" | bc)
  echo "Error rate: ${ERROR_RATE}%"
  if [ $(echo "$ERROR_RATE > 1.0" | bc) -eq 1 ]; then
    echo "ALERT: Error rate above threshold"
  fi
fi

# Check replication lag
LAG=$(docker-compose exec db-replica psql -U postgres -t -c "
SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()));
" | xargs)
if [ $(echo "$LAG > 60" | bc) -eq 1 ]; then
  echo "ALERT: Replication lag is ${LAG} seconds"
fi
```

---

## Standard Operations

### Load Balancer Operations

#### Start/Stop NGINX

```bash
# Start NGINX
docker-compose up -d nginx

# Stop NGINX (causes downtime!)
docker-compose stop nginx

# Restart NGINX (brief downtime)
docker-compose restart nginx

# Reload NGINX configuration (zero downtime)
docker-compose exec nginx nginx -s reload

# Verify NGINX is running
docker-compose ps nginx
curl -I http://localhost
```

#### Update NGINX Configuration

```bash
# 1. Edit configuration
vim nginx/conf.d/default.conf

# 2. Test configuration syntax
docker-compose exec nginx nginx -t

# 3. If valid, reload configuration (zero downtime)
docker-compose exec nginx nginx -s reload

# 4. Verify changes
docker-compose exec nginx cat /etc/nginx/conf.d/default.conf

# 5. Test load balancing
for i in {1..10}; do
  curl -s http://localhost | grep "App Instance"
done
```

#### View NGINX Logs

```bash
# Access logs (all requests)
docker-compose logs nginx --tail=100 --follow

# Filter for errors
docker-compose logs nginx | grep " 5[0-9][0-9] \| 4[0-9][0-9] "

# Count requests by status code
docker-compose logs nginx | awk '{print $9}' | sort | uniq -c

# Show slow requests (if configured with $request_time)
docker-compose logs nginx | awk '$11 > 1 {print}' | tail -20

# Get request rate
docker-compose logs nginx --since 1h | grep -c "HTTP/" | \
  awk '{print $1/60 " requests/minute"}'
```

### Application Instance Management

#### Check Instance Health

```bash
# Check all instances
make test-ha

# Or manually check each instance
for i in 1 2 3; do
  echo "=== Checking app-$i ==="
  docker-compose exec app-$i curl -s http://localhost:8000/health | jq .
  docker-compose exec app-$i curl -s http://localhost:8000/ready | jq .
done

# Check through load balancer
for i in {1..10}; do
  curl -s http://localhost/health | jq -r '.instance'
done | sort | uniq -c
```

#### Restart Single Instance

```bash
# Restart specific instance (NGINX routes around it)
docker-compose restart app-1

# Verify instance is back up
sleep 5
docker-compose exec app-1 curl -s http://localhost:8000/health

# Check it's receiving traffic
docker-compose logs nginx --since 1m | grep app-1
```

#### Scale Application Instances

```bash
# Scale up to 5 instances
docker-compose up -d --scale app=5

# Scale down to 2 instances
docker-compose up -d --scale app=2

# Note: If using explicit instance names (app-1, app-2, app-3),
# you need to update docker-compose.yml and NGINX config

# After scaling, update NGINX upstream
vim nginx/conf.d/upstream.conf
docker-compose exec nginx nginx -s reload
```

#### Deploy New Version (Rolling Update)

```bash
# Rolling deployment strategy (zero downtime)

# 1. Pull new image
docker-compose pull app

# 2. Update instances one at a time
for instance in app-1 app-2 app-3; do
  echo "=== Updating $instance ==="

  # Remove instance from load balancer
  docker-compose exec nginx sed -i "s/server $instance:8000;/# server $instance:8000;/" /etc/nginx/conf.d/upstream.conf
  docker-compose exec nginx nginx -s reload

  # Wait for connections to drain
  sleep 10

  # Restart instance with new version
  docker-compose up -d --no-deps --build $instance

  # Wait for instance to be healthy
  sleep 15
  until docker-compose exec $instance curl -sf http://localhost:8000/health; do
    echo "Waiting for $instance to be healthy..."
    sleep 5
  done

  # Add instance back to load balancer
  docker-compose exec nginx sed -i "s/# server $instance:8000;/server $instance:8000;/" /etc/nginx/conf.d/upstream.conf
  docker-compose exec nginx nginx -s reload

  echo "$instance updated successfully"
done

echo "Rolling deployment completed"
```

#### View Application Logs

```bash
# View logs from all instances
docker-compose logs app-1 app-2 app-3 --follow

# View logs from single instance
docker-compose logs app-1 --follow

# Filter for errors
docker-compose logs app-1 app-2 app-3 | grep -i "error\|exception\|failed"

# Get request counts per instance
docker-compose logs nginx | grep -oP "app-[0-9]" | sort | uniq -c
```

### Database Operations

#### Check Database Health

```bash
# Check primary database
docker-compose exec db-primary psql -U postgres -c "SELECT version();"
docker-compose exec db-primary psql -U postgres -c "SELECT pg_is_in_recovery();"

# Check replica database
docker-compose exec db-replica psql -U postgres -c "SELECT version();"
docker-compose exec db-replica psql -U postgres -c "SELECT pg_is_in_recovery();"

# Check replication status
docker-compose exec db-primary psql -U postgres -c "SELECT * FROM pg_stat_replication;"
docker-compose exec db-replica psql -U postgres -c "SELECT * FROM pg_stat_wal_receiver;"
```

#### Monitor Replication Lag

```bash
# Check lag in seconds
docker-compose exec db-replica psql -U postgres -c "
SELECT
  EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) AS lag_seconds,
  pg_last_xact_replay_timestamp() AS last_replay_time;
"

# Continuous monitoring
watch -n 5 'docker-compose exec db-replica psql -U postgres -t -c "
SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) AS lag_seconds;
"'
```

#### Promote Replica to Primary (Failover)

```bash
# CAUTION: This is a destructive operation!

# 1. Stop applications to prevent writes
docker-compose stop app-1 app-2 app-3

# 2. Verify replica is caught up
docker-compose exec db-replica psql -U postgres -c "
SELECT pg_last_xact_replay_timestamp();
"

# 3. Promote replica
docker-compose exec db-replica pg_ctl promote -D /var/lib/postgresql/data

# 4. Verify promotion
docker-compose exec db-replica psql -U postgres -c "SELECT pg_is_in_recovery();"
# Should return 'f' (not in recovery)

# 5. Update application configuration to point to new primary
# Edit docker-compose.yml or environment variables
# Change DB_HOST from db-primary to db-replica

# 6. Restart applications
docker-compose up -d app-1 app-2 app-3

# 7. Verify applications can write to database
curl -X POST http://localhost/api/test \
  -H "Content-Type: application/json" \
  -d '{"test":"data"}'
```

#### Backup Database

```bash
# Backup from replica (don't impact primary)
docker-compose exec db-replica pg_dump -U postgres appdb > backup/appdb-$(date +%Y%m%d-%H%M%S).sql

# Compressed backup
docker-compose exec db-replica pg_dump -U postgres appdb | gzip > backup/appdb-$(date +%Y%m%d-%H%M%S).sql.gz

# Backup all databases
docker-compose exec db-replica pg_dumpall -U postgres > backup/all-dbs-$(date +%Y%m%d-%H%M%S).sql

# Restore from backup
docker-compose exec -T db-primary psql -U postgres appdb < backup/appdb-20251110-120000.sql
```

### Health Check and Monitoring

#### Manual Health Checks

```bash
# Full system health check
echo "=== Load Balancer ==="
docker-compose ps nginx
curl -I http://localhost

echo "=== Application Instances ==="
for i in 1 2 3; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health)
  echo "app-$i: HTTP $STATUS"
done

echo "=== Database ==="
docker-compose exec db-primary psql -U postgres -c "SELECT 1;" > /dev/null && echo "Primary: OK" || echo "Primary: FAILED"
docker-compose exec db-replica psql -U postgres -c "SELECT 1;" > /dev/null && echo "Replica: OK" || echo "Replica: FAILED"

echo "=== Replication Lag ==="
docker-compose exec db-replica psql -U postgres -t -c "
SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) || ' seconds';
"
```

#### Automated Health Monitoring Script

```bash
# Create monitoring script
cat > scripts/health-check.sh <<'EOF'
#!/bin/bash
set -e

ALERT_THRESHOLD_ERROR_RATE=5.0
ALERT_THRESHOLD_LAG=60

# Check application instances
echo "Checking application instances..."
HEALTHY=0
for i in 1 2 3; do
  if docker-compose exec app-$i curl -sf http://localhost:8000/health > /dev/null; then
    HEALTHY=$((HEALTHY + 1))
  else
    echo "ALERT: app-$i is unhealthy"
  fi
done

if [ $HEALTHY -lt 2 ]; then
  echo "CRITICAL: Only $HEALTHY instances healthy"
  exit 1
fi

# Check error rate
echo "Checking error rate..."
ERROR_COUNT=$(docker-compose logs nginx --since 10m | grep -c " 5[0-9][0-9] " || echo 0)
TOTAL_COUNT=$(docker-compose logs nginx --since 10m | grep -c "HTTP/" || echo 1)
ERROR_RATE=$(echo "scale=2; 100 * $ERROR_COUNT / $TOTAL_COUNT" | bc)

if [ $(echo "$ERROR_RATE > $ALERT_THRESHOLD_ERROR_RATE" | bc) -eq 1 ]; then
  echo "ALERT: Error rate is ${ERROR_RATE}%"
fi

# Check replication lag
echo "Checking replication lag..."
LAG=$(docker-compose exec db-replica psql -U postgres -t -c "
SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()));
" | xargs)

if [ $(echo "$LAG > $ALERT_THRESHOLD_LAG" | bc) -eq 1 ]; then
  echo "ALERT: Replication lag is ${LAG} seconds"
fi

echo "Health check completed successfully"
EOF
chmod +x scripts/health-check.sh

# Run health check
./scripts/health-check.sh

# Schedule in cron (every 5 minutes)
# */5 * * * * /path/to/scripts/health-check.sh >> /var/log/ha-webapp-health.log 2>&1
```

---

## Incident Response

### Detection

**Automated Detection:**

- Health check monitoring failures
- NGINX upstream health check failures
- Database replication lag alerts
- High error rate alerts

**Manual Detection:**

```bash
# Check overall system status
docker-compose ps

# Check recent errors in logs
docker-compose logs nginx --since 30m | grep " 5[0-9][0-9] "

# Check instance health
for i in 1 2 3; do
  docker-compose exec app-$i curl -sf http://localhost:8000/health || echo "app-$i FAILED"
done

# Check database replication
docker-compose exec db-replica psql -U postgres -c "SELECT pg_is_in_recovery();"
```

### Triage

#### Severity Classification

### P0: Complete Outage

- All application instances down
- Load balancer down
- Primary database down (writes failing)

### P1: Degraded Service

- 2 of 3 app instances down (reduced capacity)
- Replication lag > 60 seconds
- Error rate > 5%
- Primary database issues (reads from replica OK)

### P2: Warning State

- Single app instance down
- Replication lag > 10 seconds
- Elevated error rate (1-5%)
- High resource usage

### P3: Informational

- Minor performance degradation
- Single instance restart
- Brief replication lag spike

### Incident Response Procedures

#### P0: All Application Instances Down

**Immediate Actions (0-5 minutes):**

```bash
# 1. Check instance status
docker-compose ps | grep app

# 2. Check instance logs
docker-compose logs app-1 app-2 app-3 --tail=50 | grep -i "error\|exception\|fatal"

# 3. Emergency: Restart all instances
docker-compose restart app-1 app-2 app-3

# 4. Wait for instances to be healthy
for i in 1 2 3; do
  until docker-compose exec app-$i curl -sf http://localhost:8000/health; do
    echo "Waiting for app-$i to be healthy..."
    sleep 5
  done
  echo "app-$i is healthy"
done

# 5. Verify load balancer is routing traffic
for i in {1..10}; do
  curl -s http://localhost/health | jq -r '.instance'
done | sort | uniq -c

# 6. Test application functionality
curl -X POST http://localhost/api/test \
  -H "Content-Type: application/json" \
  -d '{"test":"data"}'
```

**Investigation (5-30 minutes):**

```bash
# Check for common issues
# 1. Database connectivity
docker-compose exec app-1 curl -s http://localhost:8000/ready | jq .

# 2. Resource exhaustion
docker stats --no-stream

# 3. Recent changes/deployments
git log --oneline --since="1 hour ago"
docker-compose logs nginx --since 1h | grep -i "deploy\|restart\|config"

# 4. Application errors
docker-compose logs app-1 --since 1h | grep -i "error\|exception" | tail -20
```

**Root Cause Analysis:**

- Database connection pool exhausted
- Application code bug (recent deployment)
- Resource limits exceeded (memory/CPU)
- External dependency failure

---

#### P0: Load Balancer Down

**Immediate Actions (0-2 minutes):**

```bash
# 1. Check NGINX status
docker-compose ps nginx

# 2. Check NGINX logs
docker-compose logs nginx --tail=50 | grep -i "error\|fatal\|emergency"

# 3. Emergency: Restart NGINX
docker-compose restart nginx

# 4. Verify NGINX is running
docker-compose ps nginx
curl -I http://localhost

# 5. Test load balancing
for i in {1..10}; do
  curl -s http://localhost/health | jq -r '.instance'
done | sort | uniq -c
```

**Investigation (2-15 minutes):**

```bash
# Check NGINX configuration
docker-compose exec nginx nginx -t

# If config invalid, restore from backup
cp nginx/conf.d/default.conf.backup nginx/conf.d/default.conf
docker-compose restart nginx

# Check for resource issues
docker stats --no-stream nginx
docker-compose exec nginx ps aux

# Check system logs
dmesg | tail -50
```

---

#### P0: Primary Database Down

**Immediate Actions (0-10 minutes):**

```bash
# 1. Verify primary is down
docker-compose ps db-primary
docker-compose exec db-primary psql -U postgres -c "SELECT 1;" || echo "Primary FAILED"

# 2. Check replica status
docker-compose exec db-replica psql -U postgres -c "SELECT pg_is_in_recovery();"

# 3. Check replication lag (should be minimal)
docker-compose exec db-replica psql -U postgres -c "
SELECT pg_last_xact_replay_timestamp();
"

# 4. Decision: Promote replica or restart primary?
# If primary is unrecoverable, promote replica:

# Stop application writes
docker-compose stop app-1 app-2 app-3

# Promote replica to primary
docker-compose exec db-replica pg_ctl promote -D /var/lib/postgresql/data

# Verify promotion
docker-compose exec db-replica psql -U postgres -c "SELECT pg_is_in_recovery();"
# Should return 'f'

# Update app configuration to use new primary
# Edit docker-compose.yml or update DNS/config

# Restart applications
docker-compose up -d app-1 app-2 app-3

# 5. Test write operations
curl -X POST http://localhost/api/test \
  -H "Content-Type: application/json" \
  -d '{"test":"failover-success"}'
```

**Investigation (10-60 minutes):**

```bash
# Check old primary logs
docker-compose logs db-primary --tail=100 | grep -i "error\|fatal\|panic"

# Attempt to recover old primary
docker-compose restart db-primary

# If successful, configure as new replica
# Update replication configuration and restart
```

---

#### P1: Multiple App Instances Down

**Immediate Actions (0-5 minutes):**

```bash
# 1. Identify failed instances
docker-compose ps | grep app

# 2. Restart failed instances
for instance in app-1 app-2 app-3; do
  if ! docker-compose exec $instance curl -sf http://localhost:8000/health; then
    echo "Restarting $instance..."
    docker-compose restart $instance
    sleep 10
  fi
done

# 3. Verify health
for i in 1 2 3; do
  docker-compose exec app-$i curl -s http://localhost:8000/health || echo "app-$i still failing"
done

# 4. Check error rate
docker-compose logs nginx --since 10m | grep -c " 5[0-9][0-9] "
```

**Investigation (5-30 minutes):**

```bash
# Check for systemic issues
# 1. Database connectivity
docker-compose exec db-primary psql -U postgres -c "
SELECT count(*) as connections FROM pg_stat_activity WHERE datname='appdb';
"

# 2. Resource constraints
docker stats --no-stream

# 3. Application logs
for i in 1 2 3; do
  echo "=== app-$i logs ==="
  docker-compose logs app-$i --since 30m | grep -i "error" | tail -10
done
```

---

#### P1: High Replication Lag

**Investigation:**

```bash
# Check current lag
docker-compose exec db-replica psql -U postgres -c "
SELECT
  EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) AS lag_seconds,
  pg_last_xact_replay_timestamp() AS last_replay_time;
"

# Check replication status
docker-compose exec db-primary psql -U postgres -c "
SELECT * FROM pg_stat_replication;
"

# Check replica activity
docker-compose exec db-replica psql -U postgres -c "
SELECT * FROM pg_stat_wal_receiver;
"

# Check for blocking queries on primary
docker-compose exec db-primary psql -U postgres -c "
SELECT pid, now() - query_start as duration, state, query
FROM pg_stat_activity
WHERE datname='appdb' AND state='active'
ORDER BY duration DESC;
"
```

**Mitigation:**

```bash
# If replication is stuck, restart replica replication
docker-compose restart db-replica

# If primary is overloaded, optimize queries or scale reads to replica
# Update app config to use replica for read queries

# Monitor lag recovery
watch -n 5 'docker-compose exec db-replica psql -U postgres -t -c "
SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()));
"'
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### Load Balancer Troubleshooting

```bash
# Check NGINX configuration
docker-compose exec nginx nginx -t

# View full configuration
docker-compose exec nginx nginx -T

# Check upstream status
docker-compose exec nginx cat /etc/nginx/conf.d/upstream.conf

# Test upstream connectivity from NGINX
docker-compose exec nginx curl -s http://app-1:8000/health
docker-compose exec nginx curl -s http://app-2:8000/health
docker-compose exec nginx curl -s http://app-3:8000/health

# Check NGINX access logs
docker-compose logs nginx | grep -v "/health\|/ready" | tail -50

# Check NGINX error logs
docker-compose logs nginx | grep error | tail -20
```

#### Application Troubleshooting

```bash
# Check instance connectivity
for i in 1 2 3; do
  echo "Testing app-$i..."
  curl -v http://localhost/health -H "Host: app-$i"
done

# Execute commands inside container
docker-compose exec app-1 /bin/sh

# Check application processes
docker-compose exec app-1 ps aux

# Check network connectivity between containers
docker-compose exec app-1 ping db-primary
docker-compose exec app-1 nc -zv db-primary 5432

# Check environment variables
docker-compose exec app-1 env | grep -i db
```

#### Database Troubleshooting

```bash
# Check database connections
docker-compose exec db-primary psql -U postgres -c "
SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;
"

# Check active queries
docker-compose exec db-primary psql -U postgres -c "
SELECT pid, usename, application_name, client_addr, state, query
FROM pg_stat_activity
WHERE datname='appdb' AND state='active';
"

# Check for locks
docker-compose exec db-primary psql -U postgres -c "
SELECT l.pid, l.locktype, l.mode, a.query
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE NOT l.granted;
"

# Check database size
docker-compose exec db-primary psql -U postgres -c "
SELECT pg_size_pretty(pg_database_size('appdb'));
"

# Check table sizes
docker-compose exec db-primary psql -U postgres -d appdb -c "
SELECT tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname='public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
"
```

### Common Issues & Solutions

#### Issue: "502 Bad Gateway" from NGINX

**Symptoms:**

- Users receiving 502 errors
- NGINX logs show "upstream prematurely closed connection"

**Diagnosis:**

```bash
# Check if upstream instances are running
docker-compose ps | grep app

# Check upstream health
for i in 1 2 3; do
  docker-compose exec nginx curl -v http://app-$i:8000/health
done

# Check NGINX error logs
docker-compose logs nginx | grep "upstream\|502"
```

**Solution:**

```bash
# Restart failed app instances
docker-compose restart app-1 app-2 app-3

# Or if NGINX config issue, reload config
docker-compose exec nginx nginx -t
docker-compose exec nginx nginx -s reload
```

---

#### Issue: Uneven load distribution

**Symptoms:**

- One instance receiving significantly more traffic than others
- Uneven CPU/memory usage across instances

**Diagnosis:**

```bash
# Check request distribution
docker-compose logs nginx | grep -oP "app-[0-9]" | sort | uniq -c

# Check instance resource usage
docker stats --no-stream | grep app
```

**Solution:**

```bash
# Review NGINX load balancing algorithm
docker-compose exec nginx cat /etc/nginx/conf.d/upstream.conf

# Update to use least_conn or ip_hash if needed
# Edit nginx/conf.d/upstream.conf:
# upstream backend {
#     least_conn;  # or ip_hash
#     server app-1:8000;
#     server app-2:8000;
#     server app-3:8000;
# }

docker-compose exec nginx nginx -s reload
```

---

#### Issue: Database connection pool exhausted

**Symptoms:**

- Application errors: "could not open connection"
- Database has max connections reached

**Diagnosis:**

```bash
# Check current connections
docker-compose exec db-primary psql -U postgres -c "
SELECT count(*) as current,
  current_setting('max_connections')::int as max
FROM pg_stat_activity;
"

# Check connections by application
docker-compose exec db-primary psql -U postgres -c "
SELECT application_name, count(*)
FROM pg_stat_activity
WHERE datname='appdb'
GROUP BY application_name;
"
```

**Solution:**

```bash
# Increase max_connections in PostgreSQL
docker-compose exec db-primary psql -U postgres -c "
ALTER SYSTEM SET max_connections = 200;
SELECT pg_reload_conf();
"

# Or optimize application connection pooling
# Reduce pool size per instance
# Close idle connections more aggressively

# Restart database if needed
docker-compose restart db-primary
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 5 minutes (database replication + backups)
- **RTO** (Recovery Time Objective): 2 minutes (automatic failover to replica + app restart)

### Backup Strategy

**Database Backups:**

```bash
# Automated backup script
cat > scripts/backup-db.sh <<'EOF'
#!/bin/bash
BACKUP_DIR=/backups
DATE=$(date +%Y%m%d-%H%M%S)

# Backup from replica (no impact on primary)
docker-compose exec -T db-replica pg_dump -U postgres appdb | gzip > $BACKUP_DIR/appdb-$DATE.sql.gz

# Keep last 7 days
find $BACKUP_DIR -name "appdb-*.sql.gz" -mtime +7 -delete

echo "Backup completed: appdb-$DATE.sql.gz"
EOF
chmod +x scripts/backup-db.sh

# Schedule daily backups (crontab)
# 0 2 * * * /path/to/scripts/backup-db.sh
```

**Configuration Backups:**

```bash
# Backup NGINX configuration
tar -czf backup/nginx-config-$(date +%Y%m%d).tar.gz nginx/

# Backup docker-compose configuration
cp docker-compose.yml backup/docker-compose-$(date +%Y%m%d).yml

# Commit to Git
git add -A
git commit -m "backup: configuration $(date +%Y-%m-%d)"
git push
```

### Disaster Recovery Procedures

#### Complete System Loss

**Recovery Steps (10-15 minutes):**

```bash
# 1. Restore code from Git
git clone <repository-url>
cd p13-ha-webapp

# 2. Restore database
docker-compose up -d db-primary
sleep 10
gunzip -c backup/appdb-latest.sql.gz | \
  docker-compose exec -T db-primary psql -U postgres appdb

# 3. Start replica
docker-compose up -d db-replica
# Wait for replication to sync

# 4. Start application instances
docker-compose up -d app-1 app-2 app-3

# 5. Wait for instances to be healthy
for i in 1 2 3; do
  until docker-compose exec app-$i curl -sf http://localhost:8000/health; do
    sleep 5
  done
done

# 6. Start load balancer
docker-compose up -d nginx

# 7. Verify system is operational
curl -I http://localhost
./scripts/health-check.sh
```

#### Database Failover Procedure

**See "P0: Primary Database Down" in Incident Response section above**

### DR Drill Procedure

**Quarterly DR Drill (1 hour):**

```bash
# 1. Document current state
docker-compose ps > dr-drill-state-before.txt
./scripts/health-check.sh > dr-drill-health-before.txt

# 2. Create backup
./scripts/backup-db.sh

# 3. Announce drill
echo "DR drill starting at $(date)" | tee dr-drill-log.txt

# 4. Simulate disaster - Stop all services
docker-compose down -v

# 5. Start recovery timer
START_TIME=$(date +%s)

# 6. Execute recovery
docker-compose up -d db-primary
sleep 10
gunzip -c backup/appdb-latest.sql.gz | docker-compose exec -T db-primary psql -U postgres appdb
docker-compose up -d
sleep 30

# 7. Verify recovery
./scripts/health-check.sh

# 8. Calculate recovery time
END_TIME=$(date +%s)
RECOVERY_TIME=$((END_TIME - START_TIME))
echo "Recovery completed in $RECOVERY_TIME seconds" | tee -a dr-drill-log.txt
echo "Target RTO: 120 seconds (2 minutes)" | tee -a dr-drill-log.txt
echo "Actual recovery time: $RECOVERY_TIME seconds" | tee -a dr-drill-log.txt
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks

```bash
# Health check
./scripts/health-check.sh

# Check error rate
docker-compose logs nginx --since 24h | grep -c " 5[0-9][0-9] "

# Check replication lag
docker-compose exec db-replica psql -U postgres -t -c "
SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()));
"

# Check disk space
df -h
docker system df
```

#### Weekly Tasks

```bash
# Review logs for errors
docker-compose logs --since 7d | grep -i "error" | wc -l

# Check resource usage trends
docker stats --no-stream

# Database maintenance
docker-compose exec db-primary psql -U postgres -d appdb -c "VACUUM ANALYZE;"

# Clean up old logs
find logs/ -name "*.log" -mtime +30 -delete

# Backup database
./scripts/backup-db.sh
```

#### Monthly Tasks

```bash
# Review performance metrics
# - Average response time
# - Error rates
# - Resource utilization

# Update dependencies
docker-compose pull
docker-compose up -d --build

# Test DR procedures
# Run abbreviated DR drill

# Review and update documentation
```

---

## Quick Reference

### Common Commands

```bash
# Start system
make run

# Stop system
docker-compose down

# Restart app instance
docker-compose restart app-1

# Check health
./scripts/health-check.sh

# View logs
docker-compose logs -f nginx app-1 app-2 app-3

# Backup database
./scripts/backup-db.sh

# Rolling deployment
./scripts/rolling-deploy.sh
```

### Emergency Response

```bash
# P0: All apps down - Restart all
docker-compose restart app-1 app-2 app-3

# P0: NGINX down - Restart
docker-compose restart nginx

# P0: Primary DB down - Promote replica
docker-compose stop app-1 app-2 app-3
docker-compose exec db-replica pg_ctl promote -D /var/lib/postgresql/data
# Update app config, restart apps

# P1: High lag - Restart replica replication
docker-compose restart db-replica
```

---

**Document Metadata:**

- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Platform Engineering Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates

## Evidence & Verification

Verification summary: Evidence artifacts captured on 2025-11-14 to validate the quickstart configuration and document audit-ready supporting files.

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
