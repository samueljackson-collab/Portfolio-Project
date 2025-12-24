# Runbook — Project 2 (Database Migration Platform)

## Overview

Production operations runbook for Project 2 Database Migration Platform. This runbook covers zero-downtime PostgreSQL database migrations using Debezium CDC (Change Data Capture), migration orchestration, cutover procedures, validation, and rollback operations.

**System Components:**
- Debezium CDC connector for PostgreSQL
- Apache Kafka for change data streaming
- Kafka Connect for connector management
- Python migration orchestrator
- Source PostgreSQL database (legacy)
- Target PostgreSQL database (new)
- Schema validation and data comparison tools

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Migration downtime** | 0 seconds (zero-downtime) | Application availability during migration |
| **Data replication lag** | < 5 seconds | Time between source write → target write |
| **Migration success rate** | 99% | Successful migrations without data loss |
| **Cutover time** | < 5 minutes | Time to switch from source → target |
| **Data consistency validation** | 100% | Source vs. target row count match |
| **Rollback time (RTO)** | < 2 minutes | Time to revert to source database |

---

## Dashboards & Alerts

### Dashboards

#### Migration Overview Dashboard
```bash
# Check Debezium connector status
curl http://localhost:8083/connectors/postgres-source-connector/status | jq

# Check Kafka topics for CDC events
kafka-topics --list --bootstrap-server localhost:9092 | grep dbserver

# Check replication lag
python src/migration_orchestrator.py status --migration-id <migration-id>
```

#### Kafka Connect Dashboard
- Connector health and task status
- Throughput metrics (messages/sec)
- Error rates and DLQ (Dead Letter Queue) messages
- Consumer lag per topic

#### Database Health Dashboard
```bash
# Source database metrics
psql -h source-db -U postgres -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"

# Target database metrics
psql -h target-db -U postgres -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"

# Replication slot status (source)
psql -h source-db -U postgres -c "SELECT * FROM pg_replication_slots;"
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Debezium connector failed | Immediate | Restart connector, investigate |
| **P0** | Data loss detected | Immediate | Halt migration, rollback |
| **P0** | Cutover failed | Immediate | Emergency rollback |
| **P1** | Replication lag > 60 seconds | 5 minutes | Investigate bottleneck |
| **P1** | Data validation mismatch | 15 minutes | Compare schemas, fix inconsistencies |
| **P2** | Kafka disk usage >80% | 30 minutes | Increase retention settings |
| **P2** | Connector task restarted | 30 minutes | Check logs for errors |
| **P3** | Slow query on source DB | 1 hour | Optimize query or add index |

---

## Standard Operations

### Migration Setup

#### Initialize Migration Environment
```bash
# Navigate to project directory
cd /home/user/Portfolio-Project/projects/2-database-migration

# Install dependencies
pip install -r requirements.txt

# Verify Kafka is running
kafka-broker-api-versions --bootstrap-server localhost:9092

# Verify Kafka Connect is running
curl http://localhost:8083/ | jq
```

#### Configure Debezium Connector
```bash
# Create connector configuration
cat > config/postgres-source-connector.json << 'EOF'
{
  "name": "postgres-source-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "source-db.example.com",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "${DEBEZIUM_PASSWORD}",
    "database.dbname": "production",
    "database.server.name": "dbserver1",
    "table.include.list": "public.*",
    "plugin.name": "pgoutput",
    "publication.autocreate.mode": "filtered",
    "slot.name": "debezium_slot",
    "snapshot.mode": "initial"
  }
}
EOF

# Deploy connector
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @config/postgres-source-connector.json

# Verify connector is running
curl http://localhost:8083/connectors/postgres-source-connector/status | jq
```

#### Create Target Database
```bash
# Connect to target database
psql -h target-db.example.com -U postgres

# Create database
CREATE DATABASE production_new;

# Create schema from source
pg_dump -h source-db.example.com -U postgres -s production | \
  psql -h target-db.example.com -U postgres production_new

# Verify schema
psql -h target-db.example.com -U postgres production_new -c "\dt"
```

### Migration Execution

#### Start Migration (Initial Snapshot)
```bash
# Initialize migration
python src/migration_orchestrator.py init \
  --source-host source-db.example.com \
  --source-db production \
  --target-host target-db.example.com \
  --target-db production_new \
  --migration-id migration-20251110

# Start initial snapshot
python src/migration_orchestrator.py snapshot \
  --migration-id migration-20251110 \
  --tables "users,orders,products"

# Monitor snapshot progress
python src/migration_orchestrator.py status --migration-id migration-20251110
```

#### Monitor Replication Lag
```bash
# Check replication lag continuously
watch -n 5 'python src/migration_orchestrator.py lag --migration-id migration-20251110'

# Check Kafka consumer lag
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group migration-consumer-group \
  --describe

# Check replication slot lag on source
psql -h source-db.example.com -U postgres -c "
  SELECT slot_name,
         pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS lag
  FROM pg_replication_slots
  WHERE slot_name = 'debezium_slot';
"
```

#### Validate Data Consistency
```bash
# Run validation script
python src/migration_orchestrator.py validate \
  --migration-id migration-20251110 \
  --check-row-counts \
  --check-checksums \
  --sample-size 10000

# Compare specific table
python src/migration_orchestrator.py compare \
  --migration-id migration-20251110 \
  --table users \
  --verbose

# Generate validation report
python src/migration_orchestrator.py report \
  --migration-id migration-20251110 \
  --output reports/validation-$(date +%Y%m%d-%H%M).html
```

### Cutover Operations

#### Pre-Cutover Checklist
```bash
# 1. Verify replication lag is minimal
python src/migration_orchestrator.py lag --migration-id migration-20251110
# Expected: < 5 seconds

# 2. Run final validation
python src/migration_orchestrator.py validate --migration-id migration-20251110
# Expected: 100% match

# 3. Create backup of source database
pg_dump -h source-db.example.com -U postgres production > backups/source-pre-cutover-$(date +%Y%m%d-%H%M).sql

# 4. Notify stakeholders
echo "Migration cutover scheduled for $(date -d '+15 minutes')" | mail -s "DB Migration Alert" team@example.com
```

#### Execute Cutover
```bash
# 1. Start cutover procedure
python src/migration_orchestrator.py cutover \
  --migration-id migration-20251110 \
  --maintenance-mode \
  --timeout 300

# This will:
# - Enable maintenance mode on applications
# - Wait for replication lag to reach 0
# - Perform final validation
# - Update connection strings
# - Disable maintenance mode

# 2. Monitor cutover progress
tail -f logs/cutover-migration-20251110.log

# 3. Verify application connectivity to target
psql -h target-db.example.com -U postgres production_new -c "SELECT version();"

# 4. Test application functionality
curl https://api.example.com/health
curl https://app.example.com/api/users/1
```

#### Post-Cutover Validation
```bash
# 1. Check application logs for errors
tail -f /var/log/application/app.log | grep -i "database\|error"

# 2. Verify no connections to old database
psql -h source-db.example.com -U postgres -c "
  SELECT count(*) FROM pg_stat_activity
  WHERE datname = 'production' AND usename NOT IN ('postgres', 'debezium');
"
# Expected: 0

# 3. Monitor target database performance
psql -h target-db.example.com -U postgres -c "
  SELECT state, count(*)
  FROM pg_stat_activity
  WHERE datname = 'production_new'
  GROUP BY state;
"

# 4. Check for errors in application metrics
# Review application dashboard for increased error rates
```

### Rollback Operations

#### Emergency Rollback
```bash
# 1. Initiate immediate rollback
python src/migration_orchestrator.py rollback \
  --migration-id migration-20251110 \
  --force \
  --reason "Data inconsistency detected"

# This will:
# - Switch connection strings back to source
# - Restart application services
# - Stop Debezium connector
# - Log rollback event

# 2. Verify rollback
psql -h source-db.example.com -U postgres production -c "SELECT count(*) FROM users;"

# 3. Check application connectivity
curl https://api.example.com/health

# 4. Document rollback reason
cat > incidents/rollback-$(date +%Y%m%d-%H%M).md << 'EOF'
# Migration Rollback Report

**Date:** $(date)
**Migration ID:** migration-20251110
**Reason:** Data inconsistency detected

## Details
[Describe what went wrong]

## Action Items
- [ ] Fix data inconsistency issue
- [ ] Update validation procedures
- [ ] Reschedule migration

EOF
```

---

## Incident Response

### Detection

**Automated Detection:**
- Debezium connector status alerts
- Replication lag threshold alerts
- Data validation failure alerts
- Kafka Connect health checks

**Manual Detection:**
```bash
# Check connector health
curl http://localhost:8083/connectors/postgres-source-connector/status | jq '.connector.state'

# Check for Kafka Connect errors
curl http://localhost:8083/connectors/postgres-source-connector/status | jq '.tasks[].trace'

# Check replication lag
python src/migration_orchestrator.py lag --migration-id migration-20251110

# Check data consistency
python src/migration_orchestrator.py validate --migration-id migration-20251110
```

### Triage

#### Severity Classification

**P0: Critical Migration Failure**
- Data loss detected
- Debezium connector failed during cutover
- Cutover failed, applications down
- Significant data inconsistency (>1% mismatch)

**P1: Degraded Migration**
- High replication lag (>60 seconds)
- Connector restarting frequently
- Schema mismatch detected
- Performance degradation on target

**P2: Warning State**
- Moderate replication lag (5-60 seconds)
- Connector task restarted once
- Minor data validation warnings
- Kafka disk usage high

**P3: Informational**
- Slow query on source database
- Kafka consumer lag increasing slowly
- Non-critical connector configuration issues

### Incident Response Procedures

#### P0: Debezium Connector Failed During Cutover

**Immediate Actions (0-2 minutes):**
```bash
# 1. Check connector status
curl http://localhost:8083/connectors/postgres-source-connector/status | jq

# 2. Initiate emergency rollback
python src/migration_orchestrator.py rollback \
  --migration-id migration-20251110 \
  --force

# 3. Verify source database is serving traffic
psql -h source-db.example.com -U postgres production -c "SELECT 1;"

# 4. Notify team
echo "Migration failed, rollback initiated" | mail -s "P0: Migration Failure" team@example.com
```

**Investigation (2-15 minutes):**
```bash
# Check connector logs
curl http://localhost:8083/connectors/postgres-source-connector/status | jq '.tasks[].trace'

# Check Kafka Connect logs
docker logs kafka-connect | tail -100

# Check database connectivity
psql -h source-db.example.com -U postgres -c "SELECT * FROM pg_replication_slots WHERE slot_name = 'debezium_slot';"

# Check for network issues
ping -c 5 source-db.example.com
telnet source-db.example.com 5432
```

**Resolution:**
```bash
# If connector can be restarted
curl -X POST http://localhost:8083/connectors/postgres-source-connector/restart

# If connector is corrupt, recreate
curl -X DELETE http://localhost:8083/connectors/postgres-source-connector
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @config/postgres-source-connector.json

# Reinitialize migration
python src/migration_orchestrator.py init --migration-id migration-20251110-retry
```

#### P0: Data Loss Detected

**Immediate Actions (0-2 minutes):**
```bash
# 1. Halt migration immediately
python src/migration_orchestrator.py halt --migration-id migration-20251110

# 2. Stop Debezium connector
curl -X PUT http://localhost:8083/connectors/postgres-source-connector/pause

# 3. Document current state
python src/migration_orchestrator.py status --migration-id migration-20251110 > incident-dataloss-$(date +%Y%m%d-%H%M).log

# 4. Emergency rollback if already cutover
python src/migration_orchestrator.py rollback --migration-id migration-20251110 --force
```

**Investigation (2-30 minutes):**
```bash
# Compare row counts
python src/migration_orchestrator.py compare \
  --migration-id migration-20251110 \
  --table users \
  --detailed

# Check for missing records
psql -h source-db.example.com -U postgres production -c "SELECT count(*) FROM users;"
psql -h target-db.example.com -U postgres production_new -c "SELECT count(*) FROM users;"

# Check Kafka topics for missing messages
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic dbserver1.public.users \
  --from-beginning \
  --max-messages 100

# Check Debezium connector offset
curl http://localhost:8083/connectors/postgres-source-connector/offsets | jq
```

**Recovery:**
```bash
# Restore missing data from source
pg_dump -h source-db.example.com -U postgres production -t users | \
  psql -h target-db.example.com -U postgres production_new

# Or perform full data resync
python src/migration_orchestrator.py resync \
  --migration-id migration-20251110 \
  --table users

# Verify data integrity
python src/migration_orchestrator.py validate --migration-id migration-20251110
```

#### P1: High Replication Lag

**Investigation:**
```bash
# Check replication lag
python src/migration_orchestrator.py lag --migration-id migration-20251110

# Check source database load
psql -h source-db.example.com -U postgres -c "
  SELECT pid, usename, state, query
  FROM pg_stat_activity
  WHERE state = 'active'
  ORDER BY query_start;
"

# Check Kafka consumer lag
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group migration-consumer-group \
  --describe

# Check target database performance
psql -h target-db.example.com -U postgres -c "
  SELECT wait_event_type, wait_event, count(*)
  FROM pg_stat_activity
  WHERE state = 'active'
  GROUP BY wait_event_type, wait_event;
"
```

**Mitigation:**
```bash
# Increase Kafka Connect workers
# Edit connect-distributed.properties
# tasks.max=8

# Restart Kafka Connect with new config
docker restart kafka-connect

# Increase target database resources (if bottleneck)
# Scale RDS instance or adjust connection pool

# Pause non-critical write operations on source
# Temporarily disable batch jobs
```

#### P1: Schema Mismatch Detected

**Investigation:**
```bash
# Export schemas for comparison
pg_dump -h source-db.example.com -U postgres -s production > /tmp/source-schema.sql
pg_dump -h target-db.example.com -U postgres -s production_new > /tmp/target-schema.sql

# Compare schemas
diff /tmp/source-schema.sql /tmp/target-schema.sql

# Check for missing tables
psql -h target-db.example.com -U postgres production_new -c "
  SELECT table_name
  FROM information_schema.tables
  WHERE table_schema = 'public'
"
```

**Resolution:**
```bash
# Apply schema changes to target
psql -h target-db.example.com -U postgres production_new < schema-updates.sql

# Or regenerate schema
pg_dump -h source-db.example.com -U postgres -s production | \
  psql -h target-db.example.com -U postgres production_new

# Restart migration with updated schema
python src/migration_orchestrator.py restart --migration-id migration-20251110
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Migration Incident Report

**Date:** $(date)
**Severity:** P0/P1/P2
**Duration:** XX minutes
**Migration ID:** migration-20251110
**Affected Component:** Debezium/Kafka/Database

## Timeline
- HH:MM: Incident detected
- HH:MM: Investigation started
- HH:MM: Root cause identified
- HH:MM: Mitigation applied
- HH:MM: Migration resumed/rolled back

## Root Cause
[Description of root cause]

## Action Items
- [ ] Update connector configuration
- [ ] Add monitoring for similar issues
- [ ] Update migration procedures

EOF

# Update runbook with lessons learned
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### Debezium Connector Issues
```bash
# Check connector status
curl http://localhost:8083/connectors/postgres-source-connector/status | jq

# Check connector configuration
curl http://localhost:8083/connectors/postgres-source-connector | jq

# Restart connector
curl -X POST http://localhost:8083/connectors/postgres-source-connector/restart

# Restart failed task
curl -X POST http://localhost:8083/connectors/postgres-source-connector/tasks/0/restart

# Delete and recreate connector
curl -X DELETE http://localhost:8083/connectors/postgres-source-connector
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @config/postgres-source-connector.json
```

#### Kafka Issues
```bash
# List topics
kafka-topics --list --bootstrap-server localhost:9092

# Describe topic
kafka-topics --describe --bootstrap-server localhost:9092 \
  --topic dbserver1.public.users

# Check consumer group lag
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group migration-consumer-group \
  --describe

# Consume messages from topic
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic dbserver1.public.users \
  --from-beginning \
  --max-messages 10
```

#### Database Replication Issues
```bash
# Check replication slots on source
psql -h source-db.example.com -U postgres -c "
  SELECT slot_name,
         slot_type,
         active,
         pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS lag
  FROM pg_replication_slots;
"

# Check active connections
psql -h source-db.example.com -U postgres -c "
  SELECT datname, usename, state, count(*)
  FROM pg_stat_activity
  GROUP BY datname, usename, state;
"

# Check for locks
psql -h target-db.example.com -U postgres production_new -c "
  SELECT relation::regclass, mode, granted
  FROM pg_locks
  WHERE NOT granted;
"
```

### Common Issues & Solutions

#### Issue: Connector Stuck in FAILED State

**Symptoms:**
```bash
$ curl http://localhost:8083/connectors/postgres-source-connector/status | jq '.connector.state'
"FAILED"
```

**Diagnosis:**
```bash
# Check error message
curl http://localhost:8083/connectors/postgres-source-connector/status | jq '.connector.trace'

# Check Kafka Connect logs
docker logs kafka-connect | grep ERROR
```

**Solution:**
```bash
# Restart connector
curl -X POST http://localhost:8083/connectors/postgres-source-connector/restart

# If that doesn't work, delete and recreate
curl -X DELETE http://localhost:8083/connectors/postgres-source-connector
sleep 5
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @config/postgres-source-connector.json
```

---

#### Issue: Replication Slot Not Advancing

**Symptoms:**
- Replication lag continuously increasing
- WAL disk usage growing on source database

**Diagnosis:**
```bash
# Check replication slot status
psql -h source-db.example.com -U postgres -c "
  SELECT slot_name, active, restart_lsn, confirmed_flush_lsn
  FROM pg_replication_slots
  WHERE slot_name = 'debezium_slot';
"

# Check if connector is consuming
curl http://localhost:8083/connectors/postgres-source-connector/status | jq '.tasks[].state'
```

**Solution:**
```bash
# If connector is not active, restart it
curl -X POST http://localhost:8083/connectors/postgres-source-connector/restart

# If slot is orphaned, drop and recreate
psql -h source-db.example.com -U postgres -c "SELECT pg_drop_replication_slot('debezium_slot');"

# Recreate connector (will create new slot)
curl -X DELETE http://localhost:8083/connectors/postgres-source-connector
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @config/postgres-source-connector.json
```

---

#### Issue: Data Inconsistency Between Source and Target

**Symptoms:**
- Row count mismatch
- Checksum validation failures
- Missing records

**Diagnosis:**
```bash
# Compare row counts
python src/migration_orchestrator.py compare \
  --migration-id migration-20251110 \
  --table users

# Find missing records
psql -h source-db.example.com -U postgres production -c "
  SELECT id FROM users
  EXCEPT
  SELECT id FROM dblink('host=target-db.example.com dbname=production_new user=postgres', 'SELECT id FROM users') AS t(id int);
"
```

**Solution:**
```bash
# Resync specific table
python src/migration_orchestrator.py resync \
  --migration-id migration-20251110 \
  --table users

# Or copy missing records
pg_dump -h source-db.example.com -U postgres production -t users --data-only | \
  psql -h target-db.example.com -U postgres production_new

# Verify sync
python src/migration_orchestrator.py validate --migration-id migration-20251110 --table users
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 0 seconds (real-time replication via CDC)
- **RTO** (Recovery Time Objective): 2 minutes (rollback to source database)

### Backup Strategy

#### Pre-Migration Backups
```bash
# Backup source database
pg_dump -h source-db.example.com -U postgres production > backups/source-pre-migration-$(date +%Y%m%d).sql

# Backup target database
pg_dump -h target-db.example.com -U postgres production_new > backups/target-pre-migration-$(date +%Y%m%d).sql

# Backup connector configuration
cp config/postgres-source-connector.json backups/connector-config-$(date +%Y%m%d).json

# Backup application configuration
cp /etc/app/database.conf backups/app-database-conf-$(date +%Y%m%d).conf
```

#### Continuous Backups During Migration
```bash
# Source database automated snapshots (AWS RDS)
aws rds create-db-snapshot \
  --db-instance-identifier source-db \
  --db-snapshot-identifier source-db-migration-$(date +%Y%m%d-%H%M)

# Export Kafka topics for recovery
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic dbserver1.public.users \
  --from-beginning > backups/kafka-users-$(date +%Y%m%d).jsonl
```

### Recovery Procedures

#### Recover Failed Migration
```bash
# 1. Rollback to source
python src/migration_orchestrator.py rollback --migration-id migration-20251110

# 2. Restore source from backup if corrupted
psql -h source-db.example.com -U postgres -c "DROP DATABASE production;"
psql -h source-db.example.com -U postgres -c "CREATE DATABASE production;"
psql -h source-db.example.com -U postgres production < backups/source-pre-migration-20251110.sql

# 3. Restart applications
systemctl restart application

# 4. Verify functionality
curl https://api.example.com/health
```

#### Recover from Kafka Data Loss
```bash
# Restore Kafka topic from backup
kafka-console-producer --bootstrap-server localhost:9092 \
  --topic dbserver1.public.users < backups/kafka-users-20251110.jsonl

# Reset consumer group offset
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group migration-consumer-group \
  --reset-offsets \
  --to-earliest \
  --topic dbserver1.public.users \
  --execute

# Restart migration consumer
python src/migration_orchestrator.py restart --migration-id migration-20251110
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks
```bash
# Check migration progress
python src/migration_orchestrator.py status --migration-id migration-20251110

# Check replication lag
python src/migration_orchestrator.py lag --migration-id migration-20251110

# Check connector health
curl http://localhost:8083/connectors/postgres-source-connector/status | jq '.connector.state'

# Review logs for errors
tail -100 logs/migration-orchestrator.log | grep ERROR
```

#### Weekly Tasks
```bash
# Run data validation
python src/migration_orchestrator.py validate --migration-id migration-20251110

# Review Kafka disk usage
df -h /var/lib/kafka

# Check replication slot size
psql -h source-db.example.com -U postgres -c "
  SELECT slot_name,
         pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS lag_size
  FROM pg_replication_slots;
"

# Archive old migration logs
mkdir -p archives/$(date +%Y-%m)
mv logs/migration-*.log archives/$(date +%Y-%m)/ 2>/dev/null || true
```

#### Monthly Tasks
```bash
# Clean up old Kafka topics
kafka-topics --delete --bootstrap-server localhost:9092 \
  --topic dbserver1.public.old_table

# Review and optimize database performance
psql -h target-db.example.com -U postgres production_new -c "ANALYZE;"
psql -h target-db.example.com -U postgres production_new -c "VACUUM ANALYZE;"

# Update Debezium version if needed
docker pull debezium/connect:latest
# Restart Kafka Connect with new image
```

---

## Quick Reference Card

### Most Common Operations

```bash
# Initialize migration
python src/migration_orchestrator.py init --source-host <source> --target-host <target> --migration-id <id>

# Start migration
python src/migration_orchestrator.py snapshot --migration-id <id>

# Check status
python src/migration_orchestrator.py status --migration-id <id>

# Check replication lag
python src/migration_orchestrator.py lag --migration-id <id>

# Validate data
python src/migration_orchestrator.py validate --migration-id <id>

# Execute cutover
python src/migration_orchestrator.py cutover --migration-id <id>

# Rollback
python src/migration_orchestrator.py rollback --migration-id <id> --force

# Check connector status
curl http://localhost:8083/connectors/postgres-source-connector/status | jq
```

### Emergency Response

```bash
# P0: Emergency rollback
python src/migration_orchestrator.py rollback --migration-id <id> --force

# P0: Stop all migration activity
python src/migration_orchestrator.py halt --migration-id <id>
curl -X PUT http://localhost:8083/connectors/postgres-source-connector/pause

# P1: Restart failed connector
curl -X POST http://localhost:8083/connectors/postgres-source-connector/restart

# P1: Resync specific table
python src/migration_orchestrator.py resync --migration-id <id> --table <table-name>

# Check data consistency
python src/migration_orchestrator.py compare --migration-id <id> --table <table-name>
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Data Engineering Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates
