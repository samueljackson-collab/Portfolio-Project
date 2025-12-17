# Runbook — P12 (Data Pipeline - Airflow DAGs)

## Overview

Production operations runbook for the P12 Apache Airflow data pipeline platform. This runbook covers DAG management, task execution, scheduler operations, incident response, and troubleshooting for the Airflow-based ETL workflows.

**System Components:**

- Apache Airflow with Docker Compose
- PostgreSQL metadata database
- Scheduler and Executor services
- Web UI for monitoring and management
- Multiple DAGs (ETL, data quality, reporting)
- Task dependencies and scheduling logic

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **DAG success rate** | 95% | Successful DAG runs / total DAG runs |
| **Task execution latency (p95)** | < configured SLA | Task duration metrics |
| **Scheduler heartbeat** | < 10 seconds | Scheduler health check interval |
| **DAG parse time** | < 2 seconds | Time to parse DAG files |
| **Task queue latency** | < 30 seconds | Time from scheduled to running |
| **Database connection pool** | > 5 available | PostgreSQL connection pool metrics |

---

## Dashboards & Alerts

### Dashboards

#### Airflow Web UI Dashboard

```bash
# Access Web UI (default: http://localhost:8080)
# Username: admin / Password: admin

# Key metrics to monitor in UI:
# - DAGs: Active DAGs, paused DAGs
# - DAG Runs: Running, success, failed
# - Tasks: Running, queued, failed
# - Pools: Slot usage
# - Recent Tasks: Latest task executions
```

#### CLI Dashboard Commands

```bash
# Check Airflow status
docker-compose ps

# List all DAGs
docker-compose exec airflow-scheduler airflow dags list

# Show DAG run status
docker-compose exec airflow-scheduler airflow dags list-runs --dag-id etl_pipeline

# List failed tasks
docker-compose exec airflow-scheduler airflow tasks states-for-dag-run \
  etl_pipeline \
  $(docker-compose exec airflow-scheduler airflow dags list-runs --dag-id etl_pipeline --no-backfill --output json | jq -r '.[0].run_id')

# Check scheduler health
docker-compose exec airflow-scheduler airflow jobs check --job-type SchedulerJob --hostname $(hostname)

# Check database connections
docker-compose exec airflow-db psql -U airflow -c "SELECT count(*) FROM pg_stat_activity WHERE datname='airflow';"
```

#### Metrics and Monitoring

```bash
# Task duration stats
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT
  dag_id,
  task_id,
  AVG(duration) as avg_duration_sec,
  MAX(duration) as max_duration_sec
FROM task_instance
WHERE state='success'
  AND start_date > NOW() - INTERVAL '7 days'
GROUP BY dag_id, task_id
ORDER BY avg_duration_sec DESC
LIMIT 10;
"

# DAG run success rate
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT
  dag_id,
  COUNT(CASE WHEN state='success' THEN 1 END) as success_count,
  COUNT(CASE WHEN state='failed' THEN 1 END) as failed_count,
  ROUND(100.0 * COUNT(CASE WHEN state='success' THEN 1 END) / COUNT(*), 2) as success_rate
FROM dag_run
WHERE start_date > NOW() - INTERVAL '7 days'
GROUP BY dag_id;
"

# Task failure rate by DAG
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT
  dag_id,
  COUNT(CASE WHEN state='failed' THEN 1 END) as failed_tasks,
  COUNT(*) as total_tasks
FROM task_instance
WHERE start_date > NOW() - INTERVAL '24 hours'
GROUP BY dag_id
HAVING COUNT(CASE WHEN state='failed' THEN 1 END) > 0
ORDER BY failed_tasks DESC;
"
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Scheduler not running | Immediate | Restart scheduler, check logs |
| **P0** | Database connection failed | Immediate | Check PostgreSQL, restart services |
| **P0** | Critical DAG failed (SLA miss) | Immediate | Investigate failure, trigger manual run |
| **P1** | Task retry limit exceeded | 15 minutes | Review logs, fix root cause |
| **P1** | Executor queue full | 15 minutes | Scale executor, investigate slow tasks |
| **P2** | DAG parse errors | 30 minutes | Fix DAG syntax, validate changes |
| **P2** | Task duration > SLA warning | 30 minutes | Optimize task, investigate performance |
| **P3** | High task retry rate | 1 hour | Review error patterns, improve error handling |

#### Alert Queries

```bash
# Check for failed DAG runs
docker-compose exec airflow-scheduler airflow dags list-runs --state failed --output table

# Check for tasks in retry state
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT dag_id, task_id, try_number, state
FROM task_instance
WHERE state IN ('up_for_retry', 'failed')
  AND start_date > NOW() - INTERVAL '1 hour'
ORDER BY start_date DESC;
"

# Check scheduler heartbeat
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT job_type, hostname, latest_heartbeat,
  EXTRACT(EPOCH FROM (NOW() - latest_heartbeat)) as seconds_since_heartbeat
FROM job
WHERE job_type='SchedulerJob' AND state='running';
"

# Check for DAG parse errors
docker-compose logs airflow-scheduler | grep -i "Failed to import\|DagBag\|Parse error"
```

---

## Standard Operations

### Airflow Service Management

#### Start Airflow

```bash
# Start all services
make run

# Or manually with docker-compose
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs
docker-compose logs -f airflow-scheduler
docker-compose logs -f airflow-webserver

# Wait for services to be healthy
while [ "$(docker-compose ps airflow-scheduler | grep -c healthy)" -eq 0 ]; do
  echo "Waiting for scheduler to be healthy..."
  sleep 5
done

# Access Web UI
echo "Airflow Web UI: http://localhost:8080"
echo "Username: admin / Password: admin"
```

#### Stop Airflow

```bash
# Stop all services gracefully
docker-compose down

# Stop with volume cleanup (removes database!)
docker-compose down -v

# Stop and remove orphan containers
docker-compose down --remove-orphans
```

#### Restart Airflow Components

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart airflow-scheduler
docker-compose restart airflow-webserver
docker-compose restart airflow-worker

# Restart with rebuild (after code changes)
docker-compose up -d --build

# Verify restart
docker-compose ps
docker-compose logs --tail=50 airflow-scheduler
```

### DAG Management

#### Deploy New DAG

```bash
# 1. Add DAG file to dags/ directory
cp my-new-dag.py dags/

# 2. Validate DAG syntax
docker-compose exec airflow-scheduler python /opt/airflow/dags/my-new-dag.py

# 3. Wait for Airflow to detect new DAG (dag_dir_list_interval, default 5 min)
# Or force DAG refresh
docker-compose exec airflow-scheduler airflow dags reserialize

# 4. Verify DAG is loaded
docker-compose exec airflow-scheduler airflow dags list | grep my-new-dag

# 5. Test DAG without execution
docker-compose exec airflow-scheduler airflow dags test my-new-dag $(date +%Y-%m-%d)

# 6. Unpause DAG to enable scheduling
docker-compose exec airflow-scheduler airflow dags unpause my-new-dag

# 7. Trigger manual run to test
docker-compose exec airflow-scheduler airflow dags trigger my-new-dag
```

#### Update Existing DAG

```bash
# 1. Update DAG file in dags/
vim dags/etl_pipeline.py

# 2. Validate syntax
make test-dags

# 3. Wait for Airflow to pick up changes (or restart scheduler)
docker-compose restart airflow-scheduler

# 4. Verify changes
docker-compose exec airflow-scheduler airflow dags show etl_pipeline

# 5. Test updated DAG
docker-compose exec airflow-scheduler airflow dags test etl_pipeline $(date +%Y-%m-%d)
```

#### Pause/Unpause DAG

```bash
# Pause DAG (stops scheduled runs)
docker-compose exec airflow-scheduler airflow dags pause etl_pipeline

# Unpause DAG (enables scheduled runs)
docker-compose exec airflow-scheduler airflow dags unpause etl_pipeline

# Check DAG pause state
docker-compose exec airflow-scheduler airflow dags list | grep etl_pipeline
```

#### Delete DAG

```bash
# 1. Pause DAG
docker-compose exec airflow-scheduler airflow dags pause etl_pipeline

# 2. Delete DAG metadata from database
docker-compose exec airflow-scheduler airflow dags delete etl_pipeline --yes

# 3. Remove DAG file
rm dags/etl_pipeline.py

# 4. Verify deletion
docker-compose exec airflow-scheduler airflow dags list | grep etl_pipeline
```

### Task Management

#### Manually Trigger DAG Run

```bash
# Trigger DAG with default config
docker-compose exec airflow-scheduler airflow dags trigger etl_pipeline

# Trigger with specific execution date
docker-compose exec airflow-scheduler airflow dags trigger etl_pipeline \
  --exec-date "2025-11-10T00:00:00+00:00"

# Trigger with custom config
docker-compose exec airflow-scheduler airflow dags trigger etl_pipeline \
  --conf '{"source":"s3","destination":"redshift"}'

# Get run ID from output
# Monitor run progress
docker-compose exec airflow-scheduler airflow dags list-runs --dag-id etl_pipeline --output table
```

#### Run Single Task

```bash
# Test single task without dependencies
docker-compose exec airflow-scheduler airflow tasks test \
  etl_pipeline \
  extract_data \
  2025-11-10

# Run task with dependencies (marks as success)
docker-compose exec airflow-scheduler airflow tasks run \
  etl_pipeline \
  extract_data \
  2025-11-10

# Run task ignoring dependencies
docker-compose exec airflow-scheduler airflow tasks run \
  etl_pipeline \
  extract_data \
  2025-11-10 \
  --ignore-all-dependencies
```

#### Clear Task State

```bash
# Clear task instance to re-run
docker-compose exec airflow-scheduler airflow tasks clear \
  etl_pipeline \
  --task-ids extract_data \
  --start-date 2025-11-10 \
  --end-date 2025-11-10 \
  --yes

# Clear all tasks in DAG run
docker-compose exec airflow-scheduler airflow tasks clear \
  etl_pipeline \
  --start-date 2025-11-10 \
  --end-date 2025-11-10 \
  --yes

# Clear failed tasks only
docker-compose exec airflow-scheduler airflow tasks clear \
  etl_pipeline \
  --start-date 2025-11-10 \
  --end-date 2025-11-10 \
  --only-failed \
  --yes

# Clear downstream tasks
docker-compose exec airflow-scheduler airflow tasks clear \
  etl_pipeline \
  --task-ids extract_data \
  --start-date 2025-11-10 \
  --end-date 2025-11-10 \
  --downstream \
  --yes
```

#### Mark Task Success/Failed

```bash
# Mark task as success (skip execution)
docker-compose exec airflow-db psql -U airflow -d airflow -c "
UPDATE task_instance
SET state='success'
WHERE dag_id='etl_pipeline'
  AND task_id='extract_data'
  AND execution_date='2025-11-10 00:00:00';
"

# Mark task as failed
docker-compose exec airflow-db psql -U airflow -d airflow -c "
UPDATE task_instance
SET state='failed'
WHERE dag_id='etl_pipeline'
  AND task_id='extract_data'
  AND execution_date='2025-11-10 00:00:00';
"
```

### Database Operations

#### Access Database

```bash
# Connect to PostgreSQL
docker-compose exec airflow-db psql -U airflow -d airflow

# Run query from command line
docker-compose exec airflow-db psql -U airflow -d airflow -c "SELECT version();"

# Backup database
docker-compose exec airflow-db pg_dump -U airflow airflow > backup/airflow-$(date +%Y%m%d-%H%M%S).sql

# Restore database
docker-compose exec -T airflow-db psql -U airflow -d airflow < backup/airflow-20251110-120000.sql
```

#### Common Database Queries

```bash
# Show all DAGs
docker-compose exec airflow-db psql -U airflow -d airflow -c "SELECT dag_id, is_paused FROM dag;"

# Show recent DAG runs
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT dag_id, execution_date, state, start_date, end_date
FROM dag_run
ORDER BY start_date DESC
LIMIT 20;
"

# Show failed tasks in last 24 hours
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT dag_id, task_id, execution_date, state, try_number
FROM task_instance
WHERE state='failed' AND start_date > NOW() - INTERVAL '24 hours'
ORDER BY start_date DESC;
"

# Show task duration statistics
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT
  dag_id,
  task_id,
  ROUND(AVG(EXTRACT(EPOCH FROM (end_date - start_date))), 2) as avg_duration_sec
FROM task_instance
WHERE state='success' AND start_date > NOW() - INTERVAL '7 days'
GROUP BY dag_id, task_id
ORDER BY avg_duration_sec DESC
LIMIT 10;
"
```

### Monitoring and Logging

#### View Logs

```bash
# View scheduler logs
docker-compose logs -f airflow-scheduler

# View webserver logs
docker-compose logs -f airflow-webserver

# View worker logs (if using CeleryExecutor)
docker-compose logs -f airflow-worker

# View task logs for specific DAG run
docker-compose exec airflow-scheduler airflow tasks logs \
  etl_pipeline \
  extract_data \
  2025-11-10

# View all container logs
docker-compose logs --tail=100 -f

# Search logs for errors
docker-compose logs airflow-scheduler | grep -i "error\|exception\|failed"
```

#### Export Logs

```bash
# Export scheduler logs
docker-compose logs airflow-scheduler > logs/scheduler-$(date +%Y%m%d).log

# Export all logs
docker-compose logs > logs/all-services-$(date +%Y%m%d).log

# Export task logs from database
docker-compose exec airflow-db psql -U airflow -d airflow -c "
COPY (
  SELECT dag_id, task_id, execution_date, state, log_url
  FROM task_instance
  WHERE start_date > NOW() - INTERVAL '7 days'
) TO STDOUT WITH CSV HEADER" > logs/task-history.csv
```

---

## Incident Response

### Detection

**Automated Detection:**

- DAG run failures
- Task retry limit exceeded
- Scheduler heartbeat missing
- Database connection errors

**Manual Detection:**

```bash
# Check overall system health
docker-compose ps | grep -v "Up (healthy)"

# Check for failed DAG runs
docker-compose exec airflow-scheduler airflow dags list-runs --state failed --no-backfill

# Check scheduler status
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT job_type, state, latest_heartbeat,
  EXTRACT(EPOCH FROM (NOW() - latest_heartbeat)) as seconds_since_heartbeat
FROM job
WHERE job_type='SchedulerJob';
"

# Check for stuck tasks
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT dag_id, task_id, state, start_date,
  EXTRACT(EPOCH FROM (NOW() - start_date)) as running_seconds
FROM task_instance
WHERE state='running' AND start_date < NOW() - INTERVAL '1 hour';
"
```

### Triage

#### Severity Classification

**P0: Critical Pipeline Failure**

- Scheduler not running
- Database connection failed
- Critical SLA-bound DAG failed
- All DAG runs failing

**P1: Degraded Service**

- Individual DAG failing repeatedly
- Tasks exceeding retry limits
- Executor queue backed up
- Slow task execution impacting downstream

**P2: Warning State**

- DAG parse errors
- Individual task failures (with retries remaining)
- Task duration warnings
- High retry rates

**P3: Informational**

- Single task failure (recovered)
- DAG run delays
- Performance degradation

### Incident Response Procedures

#### P0: Scheduler Not Running

**Immediate Actions (0-5 minutes):**

```bash
# 1. Check scheduler status
docker-compose ps airflow-scheduler

# 2. Check scheduler logs
docker-compose logs --tail=100 airflow-scheduler | grep -i "error\|exception\|fatal"

# 3. Check database connectivity
docker-compose exec airflow-scheduler airflow db check

# 4. Restart scheduler
docker-compose restart airflow-scheduler

# 5. Verify scheduler is running
docker-compose ps airflow-scheduler
docker-compose logs --tail=50 -f airflow-scheduler

# 6. Check heartbeat
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT job_type, state, latest_heartbeat
FROM job
WHERE job_type='SchedulerJob'
ORDER BY latest_heartbeat DESC
LIMIT 1;
"
```

**Investigation (5-30 minutes):**

```bash
# Check for zombie jobs
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT * FROM job
WHERE state='running'
  AND latest_heartbeat < NOW() - INTERVAL '5 minutes';
"

# Clean up zombie jobs if found
docker-compose exec airflow-db psql -U airflow -d airflow -c "
UPDATE job SET state='failed'
WHERE state='running'
  AND latest_heartbeat < NOW() - INTERVAL '5 minutes';
"

# Check for database locks
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT pid, usename, application_name, state, query
FROM pg_stat_activity
WHERE datname='airflow' AND state='active';
"

# Check resource usage
docker stats --no-stream
```

**Recovery:**

```bash
# Full service restart if needed
docker-compose restart

# Or complete rebuild
docker-compose down
docker-compose up -d --build

# Verify all services healthy
docker-compose ps
```

---

#### P0: Database Connection Failed

**Immediate Actions (0-5 minutes):**

```bash
# 1. Check database container
docker-compose ps airflow-db

# 2. Check database logs
docker-compose logs --tail=100 airflow-db

# 3. Test database connection
docker-compose exec airflow-db psql -U airflow -d airflow -c "SELECT 1;"

# 4. Restart database (last resort - causes downtime!)
docker-compose restart airflow-db

# 5. Wait for database to be ready
sleep 10

# 6. Restart dependent services
docker-compose restart airflow-scheduler airflow-webserver

# 7. Verify connection
docker-compose exec airflow-scheduler airflow db check
```

**Investigation (5-30 minutes):**

```bash
# Check connection pool exhaustion
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT count(*) as connections, state
FROM pg_stat_activity
WHERE datname='airflow'
GROUP BY state;
"

# Check for long-running queries
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT pid, now() - query_start as duration, state, query
FROM pg_stat_activity
WHERE datname='airflow' AND state='active'
ORDER BY duration DESC;
"

# Kill long-running queries if needed
# docker-compose exec airflow-db psql -U airflow -d airflow -c "SELECT pg_terminate_backend(<pid>);"
```

---

#### P1: Critical DAG Failed (SLA Miss)

**Immediate Actions (0-15 minutes):**

```bash
# 1. Identify failed DAG run
docker-compose exec airflow-scheduler airflow dags list-runs \
  --dag-id etl_pipeline \
  --state failed \
  --output table

# 2. Get DAG run details
RUN_ID=$(docker-compose exec airflow-scheduler airflow dags list-runs \
  --dag-id etl_pipeline \
  --state failed \
  --output json | jq -r '.[0].run_id')

# 3. Identify failed tasks
docker-compose exec airflow-scheduler airflow tasks states-for-dag-run \
  etl_pipeline $RUN_ID

# 4. Check logs for failed task
FAILED_TASK=$(docker-compose exec airflow-db psql -U airflow -d airflow -t -c "
SELECT task_id FROM task_instance
WHERE dag_id='etl_pipeline' AND run_id='$RUN_ID' AND state='failed'
LIMIT 1;
" | xargs)

docker-compose exec airflow-scheduler airflow tasks logs \
  etl_pipeline $FAILED_TASK $RUN_ID

# 5. Fix issue and clear task to re-run
# After identifying and fixing the root cause:
docker-compose exec airflow-scheduler airflow tasks clear \
  etl_pipeline \
  --task-ids $FAILED_TASK \
  --dag-run-id $RUN_ID \
  --yes

# 6. Or trigger new DAG run
docker-compose exec airflow-scheduler airflow dags trigger etl_pipeline
```

**Common Failure Scenarios:**

**Data Source Unavailable:**

```bash
# Check if source is accessible
docker-compose exec airflow-scheduler curl -I https://data-source.example.com

# If temporary issue, clear and retry
docker-compose exec airflow-scheduler airflow tasks clear \
  etl_pipeline --task-ids extract_data --only-failed --yes
```

**Transformation Error:**

```bash
# Check logs for data quality issues
docker-compose exec airflow-scheduler airflow tasks logs \
  etl_pipeline transform_data $RUN_ID | grep -i "error\|exception"

# If data issue, fix source and re-run from extract
docker-compose exec airflow-scheduler airflow tasks clear \
  etl_pipeline --task-ids extract_data --downstream --yes
```

**Destination Load Failure:**

```bash
# Check destination database/storage
# Verify credentials, capacity, permissions

# If temporary issue, retry just the load task
docker-compose exec airflow-scheduler airflow tasks clear \
  etl_pipeline --task-ids load_data --only-failed --yes
```

---

#### P1: Executor Queue Full

**Investigation:**

```bash
# Check task queue
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT state, COUNT(*) as count
FROM task_instance
WHERE state IN ('queued', 'running')
GROUP BY state;
"

# Check pool usage
docker-compose exec airflow-scheduler airflow pools list

# Check long-running tasks
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT dag_id, task_id, state,
  EXTRACT(EPOCH FROM (NOW() - start_date)) / 60 as running_minutes
FROM task_instance
WHERE state='running'
ORDER BY start_date ASC;
"
```

**Mitigation:**

```bash
# Option 1: Increase pool slots
docker-compose exec airflow-scheduler airflow pools set default_pool 32 "Default pool"

# Option 2: Scale workers (if using CeleryExecutor)
docker-compose up -d --scale airflow-worker=3

# Option 3: Kill stuck tasks
# Identify and kill long-running tasks if appropriate
docker-compose exec airflow-db psql -U airflow -d airflow -c "
UPDATE task_instance
SET state='failed'
WHERE state='running'
  AND start_date < NOW() - INTERVAL '4 hours'
  AND dag_id='problematic_dag';
"

# Clear failed tasks to reschedule
docker-compose exec airflow-scheduler airflow tasks clear \
  problematic_dag --only-failed --yes
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### DAG Issues

```bash
# List all DAGs with status
docker-compose exec airflow-scheduler airflow dags list

# Show DAG structure
docker-compose exec airflow-scheduler airflow dags show etl_pipeline

# Show DAG dependencies
docker-compose exec airflow-scheduler airflow tasks list etl_pipeline --tree

# Check DAG import errors
docker-compose exec airflow-scheduler airflow dags list-import-errors

# Parse specific DAG file
docker-compose exec airflow-scheduler python /opt/airflow/dags/etl_pipeline.py
```

#### Task Issues

```bash
# List all tasks in DAG
docker-compose exec airflow-scheduler airflow tasks list etl_pipeline

# Get task details
docker-compose exec airflow-scheduler airflow tasks state \
  etl_pipeline extract_data 2025-11-10

# Test task execution
docker-compose exec airflow-scheduler airflow tasks test \
  etl_pipeline extract_data 2025-11-10

# View task logs
docker-compose exec airflow-scheduler airflow tasks logs \
  etl_pipeline extract_data 2025-11-10

# View task rendered template
docker-compose exec airflow-scheduler airflow tasks render \
  etl_pipeline extract_data 2025-11-10
```

#### System Health

```bash
# Check all service status
docker-compose ps

# Check service health
docker inspect --format='{{.State.Health.Status}}' $(docker-compose ps -q airflow-scheduler)

# Check resource usage
docker stats --no-stream

# Check disk space
df -h

# Check database size
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT pg_size_pretty(pg_database_size('airflow')) as database_size;
"

# Check table sizes
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname='public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
"
```

### Common Issues & Solutions

#### Issue: DAG not appearing in Web UI

**Symptoms:**

- DAG file added to dags/ directory
- DAG not visible in Web UI

**Diagnosis:**

```bash
# Check if DAG file is in correct location
ls -la dags/

# Check for DAG import errors
docker-compose exec airflow-scheduler airflow dags list-import-errors

# Check scheduler logs for parse errors
docker-compose logs airflow-scheduler | grep -i "Failed to import"

# Try parsing DAG file manually
docker-compose exec airflow-scheduler python /opt/airflow/dags/my-dag.py
```

**Solution:**

```bash
# Fix syntax errors in DAG file
# Restart scheduler to force re-parse
docker-compose restart airflow-scheduler

# Or trigger DAG reserialization
docker-compose exec airflow-scheduler airflow dags reserialize
```

---

#### Issue: Task stuck in "running" state

**Symptoms:**

- Task shows as running for extended period
- No recent log updates

**Diagnosis:**

```bash
# Check task status
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT dag_id, task_id, state, start_date,
  EXTRACT(EPOCH FROM (NOW() - start_date)) / 60 as running_minutes
FROM task_instance
WHERE state='running' AND dag_id='etl_pipeline';
"

# Check for zombie tasks
docker-compose exec airflow-scheduler airflow tasks states-for-dag-run \
  etl_pipeline <run-id>

# Check logs
docker-compose exec airflow-scheduler airflow tasks logs \
  etl_pipeline extract_data 2025-11-10
```

**Solution:**

```bash
# Mark task as failed to reschedule
docker-compose exec airflow-db psql -U airflow -d airflow -c "
UPDATE task_instance
SET state='failed'
WHERE dag_id='etl_pipeline'
  AND task_id='extract_data'
  AND execution_date='2025-11-10 00:00:00';
"

# Clear and re-run
docker-compose exec airflow-scheduler airflow tasks clear \
  etl_pipeline --task-ids extract_data --yes
```

---

#### Issue: "Broken DAG" error

**Symptoms:**

- DAG shows as "Broken" in UI
- DAG won't execute

**Diagnosis:**

```bash
# Check import errors
docker-compose exec airflow-scheduler airflow dags list-import-errors

# Check specific DAG
docker-compose exec airflow-scheduler python /opt/airflow/dags/broken-dag.py
```

**Solution:**

```bash
# Fix errors in DAG file (syntax, imports, etc.)
vim dags/broken-dag.py

# Validate fix
docker-compose exec airflow-scheduler python /opt/airflow/dags/broken-dag.py

# Restart scheduler
docker-compose restart airflow-scheduler
```

---

#### Issue: "Connection refused" to database

**Symptoms:**

- Scheduler or webserver can't connect to PostgreSQL
- "connection refused" errors in logs

**Diagnosis:**

```bash
# Check database container
docker-compose ps airflow-db

# Check database logs
docker-compose logs airflow-db

# Test connection
docker-compose exec airflow-db psql -U airflow -d airflow -c "SELECT 1;"
```

**Solution:**

```bash
# Restart database
docker-compose restart airflow-db

# Wait for database to be ready
sleep 10

# Restart dependent services
docker-compose restart airflow-scheduler airflow-webserver

# Verify connection
docker-compose exec airflow-scheduler airflow db check
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 1 hour (database backups)
- **RTO** (Recovery Time Objective): 30 minutes (service restart + DB restore)

### Backup Strategy

**Database Backups:**

```bash
# Create database backup
docker-compose exec airflow-db pg_dump -U airflow airflow > backup/airflow-$(date +%Y%m%d-%H%M%S).sql

# Create compressed backup
docker-compose exec airflow-db pg_dump -U airflow airflow | gzip > backup/airflow-$(date +%Y%m%d-%H%M%S).sql.gz

# Automated daily backup script (add to cron)
cat > backup-airflow.sh <<'EOF'
#!/bin/bash
BACKUP_DIR=/path/to/backups
DATE=$(date +%Y%m%d-%H%M%S)
docker-compose exec -T airflow-db pg_dump -U airflow airflow | gzip > $BACKUP_DIR/airflow-$DATE.sql.gz
# Keep last 30 days
find $BACKUP_DIR -name "airflow-*.sql.gz" -mtime +30 -delete
EOF
chmod +x backup-airflow.sh

# Add to crontab for daily backups at 2 AM
# 0 2 * * * /path/to/backup-airflow.sh
```

**DAG Code Backups:**

```bash
# DAG files in Git
git add dags/
git commit -m "backup: DAG files $(date +%Y-%m-%d)"
git push

# Create tarball backup
tar -czf backup/dags-$(date +%Y%m%d).tar.gz dags/
```

### Disaster Recovery Procedures

#### Complete System Loss

**Recovery Steps (30-45 minutes):**

```bash
# 1. Restore code from Git
git clone <repository-url>
cd p12-data-pipeline

# 2. Restore database backup
# Start PostgreSQL
docker-compose up -d airflow-db
sleep 10

# Restore database
gunzip -c backup/airflow-20251110-020000.sql.gz | \
  docker-compose exec -T airflow-db psql -U airflow -d airflow

# 3. Start all services
docker-compose up -d

# 4. Verify services
docker-compose ps

# 5. Check DAGs loaded
docker-compose exec airflow-scheduler airflow dags list

# 6. Verify Web UI accessible
curl -I http://localhost:8080

# 7. Test critical DAG
docker-compose exec airflow-scheduler airflow dags test etl_pipeline $(date +%Y-%m-%d)
```

#### Database Corruption

**Recovery Steps (15-30 minutes):**

```bash
# 1. Stop all services
docker-compose down

# 2. Remove corrupted database volume
docker volume rm p12-data-pipeline_postgres-db-volume

# 3. Recreate database
docker-compose up -d airflow-db
sleep 10

# 4. Initialize Airflow database
docker-compose run --rm airflow-scheduler airflow db init

# 5. Restore from backup
gunzip -c backup/airflow-20251110-020000.sql.gz | \
  docker-compose exec -T airflow-db psql -U airflow -d airflow

# 6. Start all services
docker-compose up -d

# 7. Verify restoration
docker-compose exec airflow-scheduler airflow dags list
```

### DR Drill Procedure

**Monthly DR Drill (1 hour):**

```bash
# 1. Create backup
docker-compose exec airflow-db pg_dump -U airflow airflow > dr-drill-backup.sql

# 2. Document current state
docker-compose exec airflow-scheduler airflow dags list > dr-drill-dags-before.txt
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT dag_id, COUNT(*) FROM dag_run GROUP BY dag_id;
" > dr-drill-stats-before.txt

# 3. Announce drill
echo "DR drill starting at $(date)" | tee dr-drill-log.txt

# 4. Simulate disaster
docker-compose down -v

# 5. Start recovery timer
START_TIME=$(date +%s)

# 6. Execute recovery
docker-compose up -d airflow-db
sleep 10
docker-compose exec -T airflow-db psql -U airflow -d airflow < dr-drill-backup.sql
docker-compose up -d

# 7. Verify recovery
docker-compose ps
docker-compose exec airflow-scheduler airflow dags list > dr-drill-dags-after.txt
diff dr-drill-dags-before.txt dr-drill-dags-after.txt

# 8. Calculate recovery time
END_TIME=$(date +%s)
RECOVERY_TIME=$((END_TIME - START_TIME))
echo "Recovery completed in $RECOVERY_TIME seconds" | tee -a dr-drill-log.txt

# 9. Document results
echo "Target RTO: 1800 seconds (30 minutes)" | tee -a dr-drill-log.txt
echo "Actual recovery time: $RECOVERY_TIME seconds" | tee -a dr-drill-log.txt

# 10. Clean up
rm dr-drill-backup.sql dr-drill-dags-*.txt dr-drill-stats-*.txt
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks

```bash
# Check DAG run status
docker-compose exec airflow-scheduler airflow dags list-runs --state failed --no-backfill

# Check task failures
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT dag_id, COUNT(*) as failures
FROM task_instance
WHERE state='failed' AND start_date > NOW() - INTERVAL '24 hours'
GROUP BY dag_id;
"

# Check service health
docker-compose ps

# Check disk space
df -h
```

#### Weekly Tasks

```bash
# Review DAG performance
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT
  dag_id,
  AVG(EXTRACT(EPOCH FROM (end_date - start_date)) / 60) as avg_duration_min
FROM dag_run
WHERE start_date > NOW() - INTERVAL '7 days' AND state='success'
GROUP BY dag_id
ORDER BY avg_duration_min DESC;
"

# Review task retry rates
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT dag_id, task_id, AVG(try_number) as avg_retries
FROM task_instance
WHERE start_date > NOW() - INTERVAL '7 days'
GROUP BY dag_id, task_id
HAVING AVG(try_number) > 1
ORDER BY avg_retries DESC;
"

# Clean up old log files
find logs/ -name "*.log" -mtime +30 -delete

# Backup database
docker-compose exec airflow-db pg_dump -U airflow airflow | gzip > backup/weekly-backup-$(date +%Y%m%d).sql.gz
```

#### Monthly Tasks

```bash
# Clean up old task instances and DAG runs
docker-compose exec airflow-scheduler airflow db clean --clean-before-timestamp "$(date -d '90 days ago' +%Y-%m-%d)" --yes

# Vacuum database
docker-compose exec airflow-db psql -U airflow -d airflow -c "VACUUM ANALYZE;"

# Review and optimize slow DAGs
# Check DAG run durations and optimize
docker-compose exec airflow-db psql -U airflow -d airflow -c "
SELECT dag_id,
  AVG(EXTRACT(EPOCH FROM (end_date - start_date))) as avg_duration,
  MAX(EXTRACT(EPOCH FROM (end_date - start_date))) as max_duration
FROM dag_run
WHERE start_date > NOW() - INTERVAL '30 days'
GROUP BY dag_id
ORDER BY max_duration DESC;
"

# Archive old backups
mkdir -p backup/archive/$(date +%Y-%m)
mv backup/airflow-$(date -d '60 days ago' +%Y%m)*.sql.gz backup/archive/$(date +%Y-%m)/ 2>/dev/null || true

# Update Airflow (if new version available)
# Test in dev environment first!
```

### Upgrade Procedures

#### Update Airflow Version

```bash
# 1. Backup current database
docker-compose exec airflow-db pg_dump -U airflow airflow > backup/pre-upgrade-$(date +%Y%m%d).sql

# 2. Update Airflow version in docker-compose.yml or Dockerfile
vim docker-compose.yml
# Change: apache/airflow:2.7.0 to apache/airflow:2.8.0

# 3. Rebuild containers
docker-compose down
docker-compose build

# 4. Run database migration
docker-compose run --rm airflow-scheduler airflow db upgrade

# 5. Start services
docker-compose up -d

# 6. Verify upgrade
docker-compose exec airflow-scheduler airflow version

# 7. Test DAGs
docker-compose exec airflow-scheduler airflow dags test etl_pipeline $(date +%Y-%m-%d)
```

---

## Quick Reference

### Common Commands

```bash
# Start Airflow
make run

# Stop Airflow
docker-compose down

# View logs
docker-compose logs -f airflow-scheduler

# Trigger DAG
docker-compose exec airflow-scheduler airflow dags trigger etl_pipeline

# List DAGs
docker-compose exec airflow-scheduler airflow dags list

# Clear failed tasks
docker-compose exec airflow-scheduler airflow tasks clear etl_pipeline --only-failed --yes

# Backup database
docker-compose exec airflow-db pg_dump -U airflow airflow > backup/airflow-$(date +%Y%m%d).sql
```

### Emergency Response

```bash
# P0: Scheduler down - Restart
docker-compose restart airflow-scheduler

# P0: Database down - Restart
docker-compose restart airflow-db && sleep 10 && docker-compose restart airflow-scheduler airflow-webserver

# P1: DAG failed - Clear and retry
docker-compose exec airflow-scheduler airflow tasks clear etl_pipeline --only-failed --yes

# P1: Queue full - Increase pool
docker-compose exec airflow-scheduler airflow pools set default_pool 64 "Default pool"
```

---

**Document Metadata:**

- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Data Engineering Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates
