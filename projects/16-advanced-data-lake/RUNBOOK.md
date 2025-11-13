# Runbook — Project 16 (Advanced Data Lake & Analytics)

## Overview

Production operations runbook for the Advanced Data Lake platform built on Databricks with Delta Lake, implementing a medallion architecture (Bronze/Silver/Gold) for data processing and analytics.

**System Components:**
- Databricks workspace with Delta Live Tables
- Apache Kafka for streaming ingestion
- Delta Lake with ACID transactions
- dbt for data transformations
- Structured streaming for real-time processing
- BI tool integrations (Power BI, Tableau)
- S3/ADLS for data storage

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Data pipeline availability** | 99.5% | Pipeline execution success rate |
| **Bronze ingestion latency** | < 5 minutes | Time from Kafka → Bronze table |
| **Silver transformation latency** | < 15 minutes | Bronze → Silver completion time |
| **Gold aggregation latency** | < 30 minutes | Silver → Gold completion time |
| **Data quality checks pass rate** | 99% | Quality validation success |
| **Query performance (p95)** | < 10 seconds | Gold table query response time |
| **Data freshness** | < 1 hour | Time since last successful update |

---

## Dashboards & Alerts

### Dashboards

#### Data Pipeline Health Dashboard
```sql
-- Check pipeline status
SELECT
  pipeline_name,
  state,
  last_update_time,
  DATEDIFF(NOW(), last_update_time) as hours_since_update
FROM system.pipelines
ORDER BY last_update_time DESC;

-- Check data freshness
SELECT
  table_name,
  MAX(ingestion_timestamp) as last_ingestion,
  COUNT(*) as record_count
FROM bronze_layer.metadata
GROUP BY table_name;
```

#### Data Quality Dashboard
```sql
-- Quality check summary
SELECT
  check_date,
  layer,
  SUM(passed) as passed_checks,
  SUM(failed) as failed_checks,
  ROUND(100.0 * SUM(passed) / (SUM(passed) + SUM(failed)), 2) as pass_rate
FROM data_quality.check_results
WHERE check_date >= CURRENT_DATE - 7
GROUP BY check_date, layer
ORDER BY check_date DESC;
```

#### Streaming Job Monitoring
```bash
# Check Spark streaming jobs
databricks jobs list --output json | jq '.jobs[] | select(.settings.name | contains("streaming"))'

# Check job runs
databricks runs list --active-only --output json | jq '.runs[] | {job_id, state, start_time}'
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Pipeline failed for > 2 hours | Immediate | Restart pipeline, investigate root cause |
| **P0** | Data corruption detected | Immediate | Stop ingestion, restore from checkpoint |
| **P1** | Bronze ingestion delayed > 30 min | 15 minutes | Check Kafka lag, investigate bottleneck |
| **P1** | Data quality failure rate > 5% | 15 minutes | Review failing records, fix transformations |
| **P2** | High storage cost (> budget) | 24 hours | Review retention policy, vacuum old data |
| **P2** | Slow query performance | 1 hour | Optimize queries, check table statistics |

#### Alert Queries

```sql
-- Pipeline failure detection
SELECT pipeline_id, pipeline_name, state, error_message
FROM system.pipelines
WHERE state = 'FAILED'
  AND last_update_time > CURRENT_TIMESTAMP - INTERVAL 2 HOURS;

-- Data freshness alert
SELECT
  table_name,
  MAX(ingestion_timestamp) as last_update,
  TIMESTAMPDIFF(MINUTE, MAX(ingestion_timestamp), NOW()) as minutes_since_update
FROM bronze_layer.metadata
GROUP BY table_name
HAVING minutes_since_update > 60;

-- Quality check failures
SELECT
  layer,
  table_name,
  check_type,
  COUNT(*) as failure_count
FROM data_quality.check_results
WHERE status = 'FAILED'
  AND check_date >= CURRENT_DATE
GROUP BY layer, table_name, check_type
HAVING failure_count > 0;
```

---

## Standard Operations

### Pipeline Management

#### Start Data Pipeline
```bash
# Start Delta Live Tables pipeline
databricks pipelines start --pipeline-id <pipeline-id>

# Start streaming job
databricks jobs run-now --job-id <job-id>

# Verify pipeline is running
databricks pipelines get --pipeline-id <pipeline-id> | jq '.state'
```

#### Stop Data Pipeline
```bash
# Stop pipeline gracefully
databricks pipelines stop --pipeline-id <pipeline-id>

# Cancel running job
databricks runs cancel --run-id <run-id>

# Verify pipeline stopped
databricks pipelines get --pipeline-id <pipeline-id> | jq '.state'
```

#### Monitor Pipeline Progress
```python
# Python script to monitor pipeline
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
pipeline = w.pipelines.get(pipeline_id="<pipeline-id>")

print(f"Pipeline: {pipeline.name}")
print(f"State: {pipeline.state}")
print(f"Latest Update: {pipeline.latest_updates[0].state if pipeline.latest_updates else 'N/A'}")

# Check streaming metrics
for update in pipeline.latest_updates[:5]:
    print(f"Update ID: {update.update_id}, State: {update.state}")
```

### Data Quality Operations

#### Run Data Quality Checks
```python
# quality_check.py
from pyspark.sql.functions import *

def validate_bronze_data(df, table_name):
    """Validate Bronze layer data quality"""
    checks = {}

    # Check for nulls in critical fields
    critical_fields = ['id', 'timestamp', 'event_type']
    for field in critical_fields:
        null_count = df.filter(col(field).isNull()).count()
        checks[f'{field}_null_check'] = null_count == 0

    # Check for duplicates
    total_count = df.count()
    distinct_count = df.select('id').distinct().count()
    checks['duplicate_check'] = total_count == distinct_count

    # Check data freshness
    max_timestamp = df.agg(max('timestamp')).collect()[0][0]
    hours_old = (datetime.now() - max_timestamp).total_seconds() / 3600
    checks['freshness_check'] = hours_old < 2

    # Log results
    for check, passed in checks.items():
        status = 'PASSED' if passed else 'FAILED'
        print(f"{table_name}.{check}: {status}")

        # Record to quality table
        spark.sql(f"""
            INSERT INTO data_quality.check_results
            VALUES ('{table_name}', '{check}', '{status}', current_timestamp())
        """)

    return all(checks.values())

# Run checks
bronze_df = spark.table("bronze_layer.events")
is_valid = validate_bronze_data(bronze_df, "bronze_layer.events")

if not is_valid:
    raise Exception("Data quality checks failed!")
```

#### Handle Data Quality Failures
```sql
-- Review failed quality checks
SELECT
  table_name,
  check_type,
  error_message,
  check_timestamp
FROM data_quality.check_results
WHERE status = 'FAILED'
  AND check_timestamp >= CURRENT_DATE
ORDER BY check_timestamp DESC;

-- Quarantine bad data
CREATE TABLE bronze_layer.events_quarantine AS
SELECT *, current_timestamp() as quarantine_timestamp
FROM bronze_layer.events
WHERE id IS NULL OR event_type IS NULL;

-- Remove bad data from bronze
DELETE FROM bronze_layer.events
WHERE id IS NULL OR event_type IS NULL;
```

### Data Lifecycle Management

#### Optimize Delta Tables
```sql
-- Optimize tables for query performance
OPTIMIZE bronze_layer.events;
OPTIMIZE silver_layer.events_cleaned;
OPTIMIZE gold_layer.events_aggregated;

-- Z-order by commonly filtered columns
OPTIMIZE gold_layer.events_aggregated
ZORDER BY (date, user_id, event_type);

-- Check table statistics
DESCRIBE DETAIL bronze_layer.events;
```

#### Vacuum Old Data
```sql
-- Vacuum tables (remove old versions beyond retention)
-- Default retention is 7 days; adjust as needed

-- Disable retention check (USE WITH CAUTION)
SET spark.databricks.delta.retentionDurationCheck.enabled = false;

-- Vacuum Bronze (keep 7 days)
VACUUM bronze_layer.events RETAIN 168 HOURS;

-- Vacuum Silver (keep 30 days)
VACUUM silver_layer.events_cleaned RETAIN 720 HOURS;

-- Vacuum Gold (keep 90 days)
VACUUM gold_layer.events_aggregated RETAIN 2160 HOURS;

-- Re-enable retention check
SET spark.databricks.delta.retentionDurationCheck.enabled = true;
```

#### Manage Kafka Consumers
```bash
# Check consumer lag
kafka-consumer-groups --bootstrap-server kafka:9092 \
  --group databricks-bronze-ingestion \
  --describe

# Reset consumer offset (if needed)
kafka-consumer-groups --bootstrap-server kafka:9092 \
  --group databricks-bronze-ingestion \
  --topic events \
  --reset-offsets --to-earliest --execute

# Monitor Kafka topics
kafka-topics --bootstrap-server kafka:9092 --list
kafka-topics --bootstrap-server kafka:9092 --describe --topic events
```

---

## Incident Response

### P0: Pipeline Failure

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check pipeline status
databricks pipelines get --pipeline-id <pipeline-id>

# 2. Check recent job runs
databricks runs list --job-id <job-id> --limit 5 --output json | \
  jq '.runs[] | {run_id, state, start_time, end_time}'

# 3. Check error logs
databricks runs get-output --run-id <run-id> | jq '.error'

# 4. Attempt restart
databricks pipelines start --pipeline-id <pipeline-id>
```

**Investigation (5-20 minutes):**
```python
# Check cluster logs
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
run = w.jobs.get_run(run_id=<run-id>)

# Get cluster ID from run
cluster_id = run.cluster_instance.cluster_id

# Download driver logs
logs = w.clusters.get_events(cluster_id=cluster_id, limit=100)
for event in logs.events:
    if event.type == 'ERROR':
        print(f"{event.timestamp}: {event.details}")
```

**Common Causes & Fixes:**

**Kafka Connection Issue:**
```python
# Check Kafka connectivity
from kafka import KafkaConsumer

try:
    consumer = KafkaConsumer(
        'events',
        bootstrap_servers='kafka:9092',
        auto_offset_reset='latest'
    )
    print("Kafka connection OK")
except Exception as e:
    print(f"Kafka connection failed: {e}")
    # Fix: Check network, credentials, restart Kafka
```

**Schema Mismatch:**
```sql
-- Check for schema changes
DESCRIBE bronze_layer.events;

-- If schema changed, update table
ALTER TABLE bronze_layer.events
ADD COLUMNS (new_field STRING);

-- Or merge schema on read
spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")
```

**Resource Exhaustion:**
```bash
# Check cluster resources
databricks clusters get --cluster-id <cluster-id> | \
  jq '.state, .cluster_cores, .cluster_memory_mb'

# Scale up cluster if needed
databricks clusters edit --json-file updated-cluster-config.json
```

### P0: Data Corruption Detected

**Immediate Actions:**
```sql
-- Stop ingestion immediately
-- (Stop all pipelines feeding affected tables)

-- Check corruption extent
SELECT COUNT(*) as total_records,
       COUNT(DISTINCT id) as unique_ids,
       COUNT(*) - COUNT(DISTINCT id) as duplicate_count
FROM bronze_layer.events
WHERE ingestion_date = CURRENT_DATE;

-- Restore from last known good version
RESTORE TABLE bronze_layer.events TO VERSION AS OF <version-number>;

-- Or restore from timestamp
RESTORE TABLE bronze_layer.events TO TIMESTAMP AS OF '2025-11-10 14:00:00';
```

**Verification:**
```sql
-- Verify restoration
SELECT
  COUNT(*) as record_count,
  MIN(ingestion_timestamp) as earliest,
  MAX(ingestion_timestamp) as latest
FROM bronze_layer.events;

-- Check table history
DESCRIBE HISTORY bronze_layer.events;
```

### P1: High Bronze Ingestion Lag

**Investigation:**
```bash
# Check Kafka consumer lag
kafka-consumer-groups --bootstrap-server kafka:9092 \
  --group databricks-bronze-ingestion \
  --describe | awk '{print $1, $5, $6}' | column -t

# Check streaming query progress
databricks clusters spark-ui --cluster-id <cluster-id>
# Navigate to Streaming tab
```

**Mitigation:**
```python
# Increase parallelism
spark.conf.set("spark.sql.shuffle.partitions", "200")
spark.conf.set("spark.sql.streaming.statefulOperator.checkCorrectness.enabled", "false")

# Adjust trigger interval
streamingQuery = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "events")
    .load()
    .writeStream
    .format("delta")
    .option("checkpointLocation", "/checkpoints/bronze")
    .trigger(processingTime='30 seconds')  # Reduce from 1 minute
    .table("bronze_layer.events")
)
```

### P1: Data Quality Check Failures

**Investigation:**
```sql
-- Identify failing records
SELECT *
FROM bronze_layer.events
WHERE id IS NULL
   OR timestamp IS NULL
   OR event_type NOT IN ('click', 'view', 'purchase')
LIMIT 100;

-- Analyze failure patterns
SELECT
  event_type,
  COUNT(*) as failure_count,
  COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as failure_pct
FROM bronze_layer.events
WHERE ingestion_date = CURRENT_DATE
  AND (id IS NULL OR timestamp IS NULL)
GROUP BY event_type;
```

**Mitigation:**
```sql
-- Option 1: Quarantine bad data
INSERT INTO bronze_layer.events_quarantine
SELECT *, current_timestamp() as quarantine_timestamp
FROM bronze_layer.events
WHERE ingestion_date = CURRENT_DATE
  AND (id IS NULL OR timestamp IS NULL);

DELETE FROM bronze_layer.events
WHERE ingestion_date = CURRENT_DATE
  AND (id IS NULL OR timestamp IS NULL);

-- Option 2: Fix data with defaults
UPDATE bronze_layer.events
SET id = uuid()
WHERE id IS NULL AND ingestion_date = CURRENT_DATE;
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: "Delta table not found"

**Symptoms:**
```
AnalysisException: Table or view not found: bronze_layer.events
```

**Diagnosis:**
```sql
-- Check if database exists
SHOW DATABASES LIKE 'bronze_layer';

-- Check tables in database
SHOW TABLES IN bronze_layer;

-- Check Delta location
DESCRIBE DETAIL bronze_layer.events;
```

**Solution:**
```sql
-- Create missing database
CREATE DATABASE IF NOT EXISTS bronze_layer;

-- Restore table from location
CREATE TABLE bronze_layer.events
USING DELTA
LOCATION 's3://datalake/bronze/events';
```

---

#### Issue: "Concurrent transaction conflict"

**Symptoms:**
```
ConcurrentAppendException: Files were added to the table by a concurrent update
```

**Diagnosis:**
```sql
-- Check active streams writing to table
SHOW STREAMS ON bronze_layer.events;

-- Check recent table history
DESCRIBE HISTORY bronze_layer.events LIMIT 10;
```

**Solution:**
```python
# Add retry logic to writes
from delta.tables import DeltaTable
from pyspark.sql.utils import ConcurrentAppendException

max_retries = 3
for attempt in range(max_retries):
    try:
        df.write.format("delta").mode("append").saveAsTable("bronze_layer.events")
        break
    except ConcurrentAppendException as e:
        if attempt < max_retries - 1:
            print(f"Retry {attempt + 1} due to concurrent write")
            time.sleep(5)
        else:
            raise
```

---

#### Issue: "Out of memory during aggregation"

**Symptoms:**
```
OutOfMemoryError: Java heap space
Executor lost due to memory pressure
```

**Diagnosis:**
```python
# Check data volume
df = spark.table("silver_layer.events_cleaned")
print(f"Record count: {df.count()}")
print(f"Partitions: {df.rdd.getNumPartitions()}")

# Check partition skew
df.groupBy(spark_partition_id()).count().show()
```

**Solution:**
```python
# Repartition data
df_repartitioned = df.repartition(200, "event_date", "user_id")

# Use salting for skewed joins
from pyspark.sql.functions import rand

df_salted = df.withColumn("salt", (rand() * 10).cast("int"))
result = df_salted.join(other_df, ["join_key", "salt"])

# Increase executor memory
# Edit cluster configuration:
# spark.executor.memory = 8g
# spark.executor.memoryOverhead = 2g
```

---

#### Issue: "Streaming query terminated unexpectedly"

**Diagnosis:**
```bash
# Check streaming query status
databricks pipelines get --pipeline-id <pipeline-id> | \
  jq '.latest_updates[0].state'

# Check checkpoint location
databricks fs ls dbfs:/checkpoints/bronze/

# Check query progress
# In Spark UI → Streaming tab
```

**Solution:**
```python
# Clear corrupted checkpoint and restart
dbutils.fs.rm("dbfs:/checkpoints/bronze/", True)

# Restart streaming with new checkpoint
streamingQuery = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "events")
    .option("startingOffsets", "latest")  # or "earliest"
    .load()
    .writeStream
    .format("delta")
    .option("checkpointLocation", "/checkpoints/bronze_new")
    .table("bronze_layer.events")
)
```

---

## Maintenance Procedures

### Daily Tasks

```bash
# Morning health check
# 1. Check pipeline status
databricks pipelines list --output json | \
  jq '.[] | {name: .name, state: .state}'

# 2. Verify data freshness
databricks sql execute --query-id <query-id>

# 3. Review quality check results
databricks sql execute --query "
  SELECT layer, pass_rate
  FROM data_quality.daily_summary
  WHERE check_date = CURRENT_DATE"

# 4. Check storage usage
databricks fs du -h s3://datalake/
```

### Weekly Tasks

```sql
-- 1. Optimize frequently queried tables
OPTIMIZE gold_layer.events_aggregated
ZORDER BY (event_date, user_id);

ANALYZE TABLE gold_layer.events_aggregated COMPUTE STATISTICS;

-- 2. Review and vacuum old data
VACUUM bronze_layer.events RETAIN 168 HOURS;

-- 3. Review pipeline performance
SELECT
  pipeline_name,
  AVG(duration_seconds) as avg_duration,
  MAX(duration_seconds) as max_duration,
  COUNT(*) as execution_count
FROM system.pipeline_runs
WHERE start_time >= CURRENT_DATE - 7
GROUP BY pipeline_name;

-- 4. Review data quality trends
SELECT
  check_date,
  layer,
  AVG(pass_rate) as avg_pass_rate
FROM data_quality.daily_summary
WHERE check_date >= CURRENT_DATE - 7
GROUP BY check_date, layer
ORDER BY check_date DESC;
```

### Monthly Tasks

```bash
# 1. Review and optimize storage costs
databricks sql execute --query "
  SELECT
    table_schema,
    SUM(size_bytes) / 1024 / 1024 / 1024 as size_gb,
    SUM(size_bytes * cost_per_gb) as monthly_cost
  FROM system.table_storage
  GROUP BY table_schema
  ORDER BY monthly_cost DESC"

# 2. Update table statistics
databricks sql execute --query "
  ANALYZE TABLE bronze_layer.events COMPUTE STATISTICS FOR ALL COLUMNS;
  ANALYZE TABLE silver_layer.events_cleaned COMPUTE STATISTICS FOR ALL COLUMNS;
  ANALYZE TABLE gold_layer.events_aggregated COMPUTE STATISTICS FOR ALL COLUMNS"

# 3. Review and update data retention policies
# Document in retention_policy.md

# 4. Conduct disaster recovery drill
# Follow DR procedures below

# 5. Review and update dbt models
cd dbt/
dbt test
dbt run
dbt docs generate
```

### Disaster Recovery

**Backup Strategy:**
```bash
# 1. Export table schemas
databricks tables list --catalog main --output json > backup/schemas.json

# 2. Backup Delta table metadata
for table in bronze_layer.events silver_layer.events_cleaned gold_layer.events_aggregated; do
  databricks sql execute --query "DESCRIBE HISTORY $table" > backup/${table}_history.txt
done

# 3. Document checkpoint locations
databricks fs ls -R dbfs:/checkpoints/ > backup/checkpoints.txt

# 4. Backup job definitions
databricks jobs list --output json > backup/jobs.json
```

**Recovery Procedures:**
```sql
-- Restore table from backup location
CREATE TABLE bronze_layer.events
USING DELTA
LOCATION 's3://datalake-backup/bronze/events';

-- Restore to specific version
RESTORE TABLE silver_layer.events_cleaned
TO VERSION AS OF 42;

-- Restore to timestamp
RESTORE TABLE gold_layer.events_aggregated
TO TIMESTAMP AS OF '2025-11-10T00:00:00';
```

---

## Quick Reference

### Common Commands

```bash
# Check pipeline status
databricks pipelines get --pipeline-id <id>

# Start pipeline
databricks pipelines start --pipeline-id <id>

# Stop pipeline
databricks pipelines stop --pipeline-id <id>

# Run job now
databricks jobs run-now --job-id <id>

# Check job status
databricks runs get --run-id <id>

# Query data
databricks sql execute --query "SELECT COUNT(*) FROM bronze_layer.events"
```

### Emergency Response

```bash
# P0: Pipeline failed - Quick restart
databricks pipelines start --pipeline-id <id>

# P0: Data corruption - Restore table
databricks sql execute --query "RESTORE TABLE bronze_layer.events TO VERSION AS OF <version>"

# P1: High lag - Check Kafka
kafka-consumer-groups --bootstrap-server kafka:9092 --group databricks-bronze-ingestion --describe

# P1: Quality failures - Quarantine bad data
databricks sql execute --query "INSERT INTO bronze_layer.events_quarantine SELECT * FROM bronze_layer.events WHERE id IS NULL"
```

### Key Metrics to Monitor

```sql
-- Pipeline health
SELECT state, COUNT(*) FROM system.pipelines GROUP BY state;

-- Data freshness
SELECT table_name, MAX(ingestion_timestamp) FROM bronze_layer.metadata GROUP BY table_name;

-- Quality pass rate
SELECT layer, AVG(pass_rate) FROM data_quality.daily_summary WHERE check_date = CURRENT_DATE GROUP BY layer;

-- Storage usage
SELECT table_schema, SUM(size_bytes) / 1024 / 1024 / 1024 as size_gb FROM system.table_storage GROUP BY table_schema;
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Data Engineering Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Submit PR with updates
