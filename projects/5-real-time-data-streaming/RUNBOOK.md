# Runbook — Project 5 (Real-time Data Streaming)

## Overview

Production operations runbook for Project 5 Real-time Data Streaming platform. This runbook covers Apache Kafka and Apache Flink operations for processing portfolio events with exactly-once semantics, including cluster management, stream processing, incident response, and troubleshooting.

**System Components:**
- Apache Kafka cluster (brokers, ZooKeeper/KRaft)
- Apache Flink cluster (JobManager, TaskManagers)
- Kafka Connect for data integration
- Stream processing jobs with exactly-once guarantees
- Monitoring via Prometheus and Grafana
- Schema Registry for message schemas
- State backends for checkpointing

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Event processing latency** | < 100ms (p99) | Time from event ingestion → processed output |
| **Kafka availability** | 99.95% | Broker uptime and reachability |
| **Flink job uptime** | 99.9% | Job running without failures |
| **Message delivery guarantee** | 100% exactly-once | No duplicates or lost messages |
| **Consumer lag** | < 1000 messages | Messages waiting to be processed |
| **Checkpoint success rate** | 99% | Flink checkpoint completion rate |
| **Throughput** | > 10,000 events/sec | Messages processed per second |

---

## Dashboards & Alerts

### Dashboards

#### Kafka Cluster Dashboard
```bash
# Check Kafka broker status
kafka-broker-api-versions --bootstrap-server localhost:9092

# Check topics
kafka-topics --list --bootstrap-server localhost:9092

# Check consumer groups
kafka-consumer-groups --bootstrap-server localhost:9092 --list

# Check broker metrics
kafka-run-class kafka.tools.JmxTool \
  --object-name kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec \
  --jmx-url service:jmx:rmi:///jndi/rmi://localhost:9999/jmxrmi
```

#### Flink Dashboard
- [Flink Web UI](http://localhost:8081)
- Job status and metrics
- Task execution timeline
- Checkpointing statistics
- Backpressure monitoring
- Exception history

#### Stream Processing Dashboard
```bash
# Check Flink job status
cd /home/user/Portfolio-Project/projects/5-real-time-data-streaming

# Check running jobs
flink list -r

# Check job details
flink info -j <job-id>

# Check consumer lag
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group flink-consumer-group \
  --describe
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Kafka cluster down (all brokers) | Immediate | Emergency restart |
| **P0** | Flink job failed | Immediate | Restart from checkpoint |
| **P0** | Data loss detected | Immediate | Investigate and recover |
| **P1** | High consumer lag (>10,000 messages) | 5 minutes | Scale consumers, investigate bottleneck |
| **P1** | Kafka broker down (one or more) | 15 minutes | Restart broker, check replication |
| **P1** | Checkpoint failure rate >5% | 15 minutes | Investigate state backend issues |
| **P2** | Slow event processing (>500ms p99) | 30 minutes | Investigate performance |
| **P2** | Disk usage >80% | 30 minutes | Clean up or scale storage |
| **P3** | Minor consumer lag (<1000 messages) | 1 hour | Monitor trends |

---

## Standard Operations

### Kafka Operations

#### Start Kafka Cluster
```bash
# Start ZooKeeper (if using ZooKeeper mode)
zookeeper-server-start /etc/kafka/zookeeper.properties &

# Start Kafka brokers
kafka-server-start /etc/kafka/server.properties &

# Or using systemd
systemctl start zookeeper
systemctl start kafka

# Verify cluster is up
kafka-broker-api-versions --bootstrap-server localhost:9092
```

#### Manage Kafka Topics
```bash
# List topics
kafka-topics --list --bootstrap-server localhost:9092

# Create topic
kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic portfolio-events \
  --partitions 10 \
  --replication-factor 3

# Describe topic
kafka-topics --describe \
  --bootstrap-server localhost:9092 \
  --topic portfolio-events

# Alter topic partitions
kafka-topics --alter \
  --bootstrap-server localhost:9092 \
  --topic portfolio-events \
  --partitions 20

# Delete topic
kafka-topics --delete \
  --bootstrap-server localhost:9092 \
  --topic old-topic
```

#### Monitor Consumer Groups
```bash
# List consumer groups
kafka-consumer-groups --bootstrap-server localhost:9092 --list

# Describe consumer group (check lag)
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group flink-consumer-group \
  --describe

# Reset consumer group offset
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group flink-consumer-group \
  --topic portfolio-events \
  --reset-offsets --to-earliest \
  --execute

# Reset to specific offset
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group flink-consumer-group \
  --topic portfolio-events:0 \
  --reset-offsets --to-offset 1000 \
  --execute
```

#### Produce and Consume Messages
```bash
# Produce test messages
echo "test message" | kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic portfolio-events

# Produce from file
cat events.json | kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic portfolio-events

# Consume messages
kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic portfolio-events \
  --from-beginning

# Consume with consumer group
kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic portfolio-events \
  --group test-consumer-group \
  --from-beginning
```

### Flink Operations

#### Start Flink Cluster
```bash
# Navigate to project directory
cd /home/user/Portfolio-Project/projects/5-real-time-data-streaming

# Start Flink cluster (standalone mode)
start-cluster.sh

# Or using YARN
flink run-application -t yarn-application \
  -Djobmanager.memory.process.size=2048m \
  -Dtaskmanager.memory.process.size=4096m \
  target/stream-processor.jar

# Verify cluster is up
curl http://localhost:8081/overview
```

#### Deploy Flink Job
```bash
# Submit job
flink run \
  -c com.example.StreamProcessor \
  -p 4 \
  target/stream-processor.jar \
  --kafka-bootstrap-servers localhost:9092 \
  --input-topic portfolio-events \
  --output-topic processed-events

# Submit with savepoint
flink run \
  -s hdfs:///flink/savepoints/savepoint-12345 \
  -c com.example.StreamProcessor \
  target/stream-processor.jar

# Submit to specific JobManager
flink run -m localhost:8081 \
  -c com.example.StreamProcessor \
  target/stream-processor.jar
```

#### Monitor Flink Jobs
```bash
# List running jobs
flink list -r

# List all jobs
flink list -a

# Get job status
flink info -j <job-id>

# Check job metrics
curl http://localhost:8081/jobs/<job-id>/metrics

# Check checkpoint statistics
curl http://localhost:8081/jobs/<job-id>/checkpoints
```

#### Manage Flink Jobs
```bash
# Stop job with savepoint
flink stop <job-id>

# Cancel job
flink cancel <job-id>

# Cancel with savepoint
flink cancel -s hdfs:///flink/savepoints <job-id>

# Restart from savepoint
flink run -s hdfs:///flink/savepoints/savepoint-12345 \
  -c com.example.StreamProcessor \
  target/stream-processor.jar
```

### Stream Processing Application

#### Run Local Simulation
```bash
# Navigate to project directory
cd /home/user/Portfolio-Project/projects/5-real-time-data-streaming

# Install dependencies
pip install -r requirements.txt

# Run event producer (generates test events)
python src/event_producer.py \
  --bootstrap-servers localhost:9092 \
  --topic portfolio-events \
  --rate 100

# Run event processor
python src/process_events.py \
  --bootstrap-servers localhost:9092 \
  --input-topic portfolio-events \
  --output-topic processed-events

# Run consumer to verify output
python src/event_consumer.py \
  --bootstrap-servers localhost:9092 \
  --topic processed-events
```

#### Scale Stream Processing
```bash
# Scale Kafka partitions
kafka-topics --alter \
  --bootstrap-server localhost:9092 \
  --topic portfolio-events \
  --partitions 20

# Scale Flink job parallelism
flink modify <job-id> -p 8

# Or redeploy with higher parallelism
flink cancel -s hdfs:///flink/savepoints <job-id>
flink run -s hdfs:///flink/savepoints/savepoint-latest \
  -p 8 \
  -c com.example.StreamProcessor \
  target/stream-processor.jar
```

---

## Incident Response

### Detection

**Automated Detection:**
- Kafka broker health checks fail
- Flink job failure alerts
- High consumer lag alerts
- Checkpoint failure alerts
- Prometheus alerts on latency thresholds

**Manual Detection:**
```bash
# Check Kafka cluster health
kafka-broker-api-versions --bootstrap-server localhost:9092

# Check Flink jobs
flink list -r

# Check consumer lag
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group flink-consumer-group \
  --describe

# Check recent Kafka logs
tail -100 /var/log/kafka/server.log | grep ERROR

# Check Flink logs
tail -100 /var/log/flink/flink-*-jobmanager-*.log | grep ERROR
```

### Triage

#### Severity Classification

### P0: Complete Outage
- Kafka cluster completely down
- All Flink jobs failed
- Data loss detected
- Zero message throughput

### P1: Degraded Service
- One or more Kafka brokers down
- Flink job repeatedly failing
- High consumer lag (>10,000 messages)
- Checkpoint failures (>5% failure rate)

### P2: Warning State
- Slow event processing (>500ms p99)
- Moderate consumer lag (1,000-10,000 messages)
- Occasional checkpoint failures
- High disk usage (>80%)

### P3: Informational
- Minor performance degradation
- Low consumer lag (<1,000 messages)
- Single checkpoint failure

### Incident Response Procedures

#### P0: Kafka Cluster Down

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check all brokers
for broker in broker1:9092 broker2:9092 broker3:9092; do
  kafka-broker-api-versions --bootstrap-server $broker 2>&1 | head -1
done

# 2. Check ZooKeeper (if applicable)
echo "ruok" | nc localhost 2181

# 3. Check broker logs
tail -200 /var/log/kafka/server.log | grep -E "ERROR|FATAL"

# 4. Attempt broker restart
systemctl restart kafka

# 5. Verify restart
kafka-broker-api-versions --bootstrap-server localhost:9092
```

**Investigation (5-20 minutes):**
```bash
# Check disk space
df -h /var/lib/kafka

# Check broker configuration
cat /etc/kafka/server.properties

# Check network connectivity
for broker in broker1 broker2 broker3; do
  nc -zv $broker 9092
done

# Check JVM heap
jstat -gc <kafka-pid>

# Check broker metrics
kafka-run-class kafka.tools.JmxTool \
  --object-name kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec \
  --jmx-url service:jmx:rmi:///jndi/rmi://localhost:9999/jmxrmi
```

**Resolution:**
```bash
# If disk full, clean up old segments
kafka-configs --bootstrap-server localhost:9092 \
  --entity-type topics \
  --entity-name old-topic \
  --alter \
  --add-config retention.ms=3600000

# If configuration issue, fix and restart
vi /etc/kafka/server.properties
systemctl restart kafka

# If broker corrupted, rebuild from replica
# Stop broker, delete data, restart, wait for replication
systemctl stop kafka
rm -rf /var/lib/kafka/data/*
systemctl start kafka
```

#### P0: Flink Job Failed

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check job status
flink list -a

# 2. Check job logs
flink log -j <job-id>

# 3. Check Flink cluster
curl http://localhost:8081/overview

# 4. Restart job from latest savepoint
SAVEPOINT=$(flink list -a | grep <job-id> | awk '{print $3}')
flink run -s $SAVEPOINT \
  -c com.example.StreamProcessor \
  target/stream-processor.jar
```

**Investigation (5-20 minutes):**
```bash
# Check JobManager logs
tail -200 /var/log/flink/flink-*-jobmanager-*.log | grep ERROR

# Check TaskManager logs
tail -200 /var/log/flink/flink-*-taskmanager-*.log | grep ERROR

# Check exception history in Flink UI
curl http://localhost:8081/jobs/<job-id>/exceptions

# Check checkpoint statistics
curl http://localhost:8081/jobs/<job-id>/checkpoints

# Common issues:
# - Out of memory
# - Checkpoint timeout
# - Kafka connectivity issues
# - State backend issues
# - Deserialization errors
```

**Resolution:**
```bash
# If out of memory, increase TaskManager memory
flink run \
  -Dtaskmanager.memory.process.size=8192m \
  -s hdfs:///flink/savepoints/savepoint-latest \
  -c com.example.StreamProcessor \
  target/stream-processor.jar

# If checkpoint timeout, increase timeout
flink run \
  -Dexecution.checkpointing.timeout=600000 \
  -s hdfs:///flink/savepoints/savepoint-latest \
  -c com.example.StreamProcessor \
  target/stream-processor.jar

# If state backend issue, check HDFS/S3
hdfs dfs -ls /flink/checkpoints
# Or: aws s3 ls s3://flink-checkpoints/

# If can't recover, start fresh without savepoint
flink run -c com.example.StreamProcessor target/stream-processor.jar
```

#### P1: High Consumer Lag

**Investigation (0-10 minutes):**
```bash
# Check consumer lag
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group flink-consumer-group \
  --describe

# Check producer rate
kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic portfolio-events \
  --time -1

# Check Flink throughput
curl http://localhost:8081/jobs/<job-id>/metrics | grep recordsReceivedPerSecond

# Check for backpressure
curl http://localhost:8081/jobs/<job-id>/vertices/<vertex-id>/backpressure
```

**Mitigation (10-30 minutes):**
```bash
# Option 1: Scale Flink job parallelism
flink modify <job-id> -p 8

# Option 2: Scale Kafka partitions
kafka-topics --alter \
  --bootstrap-server localhost:9092 \
  --topic portfolio-events \
  --partitions 20

# Option 3: Optimize Flink job
# - Increase buffer timeout
# - Tune checkpoint interval
# - Optimize state access

# Redeploy with optimizations
flink cancel -s hdfs:///flink/savepoints <job-id>
flink run \
  -s hdfs:///flink/savepoints/savepoint-latest \
  -p 8 \
  -Dexecution.buffer-timeout=100 \
  -Dexecution.checkpointing.interval=60000 \
  -c com.example.StreamProcessor \
  target/stream-processor.jar

# Monitor lag reduction
watch -n 5 'kafka-consumer-groups --bootstrap-server localhost:9092 --group flink-consumer-group --describe'
```

#### P1: Checkpoint Failures

**Investigation:**
```bash
# Check checkpoint statistics
curl http://localhost:8081/jobs/<job-id>/checkpoints | jq

# Check checkpoint history
curl http://localhost:8081/jobs/<job-id>/checkpoints/details/<checkpoint-id>

# Check state backend
# For RocksDB
grep -r "RocksDB" /var/log/flink/

# For HDFS
hdfs dfs -ls /flink/checkpoints/<job-id>

# For S3
aws s3 ls s3://flink-checkpoints/<job-id>/
```

**Resolution:**
```bash
# Increase checkpoint timeout
flink run \
  -Dexecution.checkpointing.timeout=600000 \
  -s hdfs:///flink/savepoints/savepoint-latest \
  -c com.example.StreamProcessor \
  target/stream-processor.jar

# Increase checkpoint interval
flink run \
  -Dexecution.checkpointing.interval=120000 \
  -s hdfs:///flink/savepoints/savepoint-latest \
  -c com.example.StreamProcessor \
  target/stream-processor.jar

# Check and fix state backend storage
# Verify HDFS/S3 is accessible and has space
df -h # for local storage
hdfs dfsadmin -report # for HDFS
aws s3api list-buckets # for S3
```

#### P2: Slow Event Processing

**Investigation:**
```bash
# Check Flink metrics
curl http://localhost:8081/jobs/<job-id>/metrics | grep latency

# Check operator metrics
curl http://localhost:8081/jobs/<job-id>/vertices/<vertex-id>/metrics

# Check backpressure
curl http://localhost:8081/jobs/<job-id>/vertices/<vertex-id>/backpressure

# Profile Flink job
# Use Flink profiler or Flame Graph
```

**Optimization:**
```bash
# Increase parallelism
flink modify <job-id> -p 8

# Tune buffer timeout
flink run \
  -Dexecution.buffer-timeout=50 \
  -c com.example.StreamProcessor \
  target/stream-processor.jar

# Optimize state access
# Use RocksDB for large state
# Enable incremental checkpoints

# Optimize operators
# Reduce expensive operations
# Use async I/O for external calls
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/streaming-incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Streaming Incident Report

**Date:** $(date)
**Severity:** P0/P1/P2
**Duration:** XX minutes
**Affected Component:** Kafka/Flink/Stream Processing

## Timeline
- HH:MM: Incident detected
- HH:MM: Investigation started
- HH:MM: Root cause identified
- HH:MM: Mitigation applied
- HH:MM: Service restored

## Root Cause
[Description of root cause]

## Impact
- Messages lost: None (exactly-once guarantees)
- Processing delay: XX minutes
- Consumer lag: Peak at XX,XXX messages

## Remediation
[Description of fix]

## Action Items
- [ ] Increase monitoring thresholds
- [ ] Optimize stream processing job
- [ ] Scale infrastructure
- [ ] Update runbook

EOF

# Update metrics
echo "$(date),P1,High Consumer Lag,45" >> metrics/streaming-incidents.csv

# Review and update configuration
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### Kafka Troubleshooting
```bash
# Check broker logs
tail -100 /var/log/kafka/server.log | grep ERROR

# Check topic details
kafka-topics --describe \
  --bootstrap-server localhost:9092 \
  --topic portfolio-events

# Check under-replicated partitions
kafka-topics --describe --under-replicated-partitions \
  --bootstrap-server localhost:9092

# Check broker metrics
kafka-run-class kafka.tools.JmxTool \
  --object-name kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec

# Test producer
echo "test" | kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic test-topic

# Test consumer
kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic test-topic \
  --from-beginning \
  --max-messages 1
```

#### Flink Troubleshooting
```bash
# Check Flink logs
tail -100 /var/log/flink/flink-*-jobmanager-*.log | grep ERROR
tail -100 /var/log/flink/flink-*-taskmanager-*.log | grep ERROR

# Check job status
flink list -a

# Check job metrics
curl http://localhost:8081/jobs/<job-id>/metrics | jq

# Check checkpoint statistics
curl http://localhost:8081/jobs/<job-id>/checkpoints | jq

# Check exception history
curl http://localhost:8081/jobs/<job-id>/exceptions | jq

# Check task execution
curl http://localhost:8081/jobs/<job-id>/vertices/<vertex-id>/metrics | jq

# Check backpressure
curl http://localhost:8081/jobs/<job-id>/vertices/<vertex-id>/backpressure | jq
```

#### Stream Processing Troubleshooting
```bash
# Check consumer lag
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group flink-consumer-group \
  --describe

# Check message rate
kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic portfolio-events

# Verify exactly-once semantics
# Check for duplicates in output
kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic processed-events \
  --from-beginning | sort | uniq -d

# Check event timestamps
kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic portfolio-events \
  --property print.timestamp=true \
  --max-messages 10
```

### Common Issues & Solutions

#### Issue: Kafka Broker Out of Disk Space

**Symptoms:**
- Broker stops accepting writes
- Log segments not being deleted

**Diagnosis:**
```bash
df -h /var/lib/kafka
du -sh /var/lib/kafka/data/*
```

**Solution:**
```bash
# Reduce retention for topics
kafka-configs --bootstrap-server localhost:9092 \
  --entity-type topics \
  --entity-name portfolio-events \
  --alter \
  --add-config retention.ms=3600000

# Manually delete old segments
kafka-delete-records --bootstrap-server localhost:9092 \
  --offset-json-file delete-records.json

# Add more disk space
# Resize volume or add new broker
```

---

#### Issue: Flink Job Out of Memory

**Symptoms:**
- Job fails with OutOfMemoryError
- TaskManager restarts frequently

**Diagnosis:**
```bash
# Check TaskManager logs
grep "OutOfMemoryError" /var/log/flink/flink-*-taskmanager-*.log

# Check heap usage
jstat -gc <flink-taskmanager-pid>
```

**Solution:**
```bash
# Increase TaskManager memory
flink run \
  -Dtaskmanager.memory.process.size=8192m \
  -Dtaskmanager.memory.managed.size=4096m \
  -c com.example.StreamProcessor \
  target/stream-processor.jar

# Use RocksDB for large state
flink run \
  -Dstate.backend=rocksdb \
  -Dstate.backend.rocksdb.memory.managed=true \
  -c com.example.StreamProcessor \
  target/stream-processor.jar

# Enable incremental checkpoints
flink run \
  -Dstate.backend.incremental=true \
  -c com.example.StreamProcessor \
  target/stream-processor.jar
```

---

#### Issue: Message Duplication

**Symptoms:**
- Same event processed multiple times
- Duplicate records in output

**Diagnosis:**
```bash
# Check exactly-once configuration
# Verify Flink job uses exactly-once mode

# Check for duplicates
kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic processed-events \
  --from-beginning | sort | uniq -d
```

**Solution:**
```bash
# Ensure exactly-once semantics in Flink job
flink run \
  -Dexecution.checkpointing.mode=EXACTLY_ONCE \
  -Dexecution.checkpointing.interval=60000 \
  -c com.example.StreamProcessor \
  target/stream-processor.jar

# Enable idempotent producer in Kafka
# In application code:
# properties.put("enable.idempotence", "true");
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 60 seconds (checkpoint interval)
- **RTO** (Recovery Time Objective): 5 minutes (restore from checkpoint)

### Backup Strategy

#### Kafka Data Backup
```bash
# Mirror topics to backup cluster
kafka-mirror-maker \
  --consumer.config source-consumer.properties \
  --producer.config backup-producer.properties \
  --whitelist 'portfolio-.*'

# Or use MirrorMaker 2
connect-mirror-maker.sh mm2.properties

# Backup topic configuration
kafka-configs --bootstrap-server localhost:9092 \
  --entity-type topics \
  --describe > backup/topic-configs-$(date +%Y%m%d).txt
```

#### Flink State Backup
```bash
# Create savepoint
flink savepoint <job-id> hdfs:///flink/savepoints

# List savepoints
hdfs dfs -ls /flink/savepoints

# Backup savepoints offsite
hdfs dfs -get /flink/savepoints/* /backup/flink-savepoints/
# Or: aws s3 sync /backup/flink-savepoints/ s3://backup-bucket/flink-savepoints/
```

### Recovery Procedures

#### Recover from Kafka Cluster Failure
```bash
# 1. Restore Kafka brokers
systemctl start kafka

# 2. Verify cluster is up
kafka-broker-api-versions --bootstrap-server localhost:9092

# 3. Restore topic configurations
kafka-topics --create --bootstrap-server localhost:9092 \
  --topic portfolio-events \
  --partitions 10 \
  --replication-factor 3

# 4. Restore data from backup cluster (if available)
kafka-mirror-maker \
  --consumer.config backup-consumer.properties \
  --producer.config source-producer.properties \
  --whitelist 'portfolio-.*'

# 5. Restart Flink jobs
flink run -s hdfs:///flink/savepoints/savepoint-latest \
  -c com.example.StreamProcessor \
  target/stream-processor.jar
```

#### Recover from Flink Failure
```bash
# 1. Find latest savepoint
LATEST_SAVEPOINT=$(hdfs dfs -ls /flink/savepoints/<job-id> | tail -1 | awk '{print $8}')

# 2. Restart job from savepoint
flink run -s $LATEST_SAVEPOINT \
  -c com.example.StreamProcessor \
  target/stream-processor.jar

# 3. Verify job is running
flink list -r

# 4. Check consumer lag
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group flink-consumer-group \
  --describe

# 5. Monitor recovery
watch -n 5 'curl -s http://localhost:8081/jobs/<job-id>/metrics | jq ".[] | select(.id==\"numRecordsInPerSecond\") | .value"'
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks
```bash
# Check Kafka cluster health
kafka-broker-api-versions --bootstrap-server localhost:9092

# Check Flink jobs
flink list -r

# Check consumer lag
kafka-consumer-groups --bootstrap-server localhost:9092 --all-groups --describe

# Check disk usage
df -h /var/lib/kafka

# Check logs for errors
tail -100 /var/log/kafka/server.log | grep ERROR
tail -100 /var/log/flink/flink-*-jobmanager-*.log | grep ERROR
```

#### Weekly Tasks
```bash
# Create Flink savepoint
flink savepoint <job-id> hdfs:///flink/savepoints

# Review checkpoint statistics
curl http://localhost:8081/jobs/<job-id>/checkpoints | jq

# Review consumer lag trends
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group flink-consumer-group \
  --describe

# Clean up old savepoints
hdfs dfs -rm -r /flink/savepoints/savepoint-old-*

# Review and archive logs
mkdir -p archives/$(date +%Y-%m)
mv /var/log/kafka/*.log.* archives/$(date +%Y-%m)/
mv /var/log/flink/*.log.* archives/$(date +%Y-%m)/
```

#### Monthly Tasks
```bash
# Update Kafka and Flink versions (in non-prod first)
# Download new versions
# Test in staging
# Rolling upgrade in production

# Review and optimize topic retention
kafka-configs --bootstrap-server localhost:9092 \
  --entity-type topics \
  --describe

# Review Flink job performance
# Analyze checkpoint durations
# Analyze backpressure
# Optimize parallelism

# Backup savepoints offsite
hdfs dfs -get /flink/savepoints/* /backup/flink-savepoints/
aws s3 sync /backup/flink-savepoints/ s3://backup-bucket/flink-savepoints/
```

---

## Quick Reference Card

### Most Common Operations

```bash
# Check Kafka cluster
kafka-broker-api-versions --bootstrap-server localhost:9092

# Check consumer lag
kafka-consumer-groups --bootstrap-server localhost:9092 --group flink-consumer-group --describe

# Check Flink jobs
flink list -r

# Create savepoint
flink savepoint <job-id> hdfs:///flink/savepoints

# Restart Flink job
flink cancel -s hdfs:///flink/savepoints <job-id>
flink run -s hdfs:///flink/savepoints/savepoint-latest -c com.example.StreamProcessor target/stream-processor.jar

# Run local simulation
cd /home/user/Portfolio-Project/projects/5-real-time-data-streaming
python src/process_events.py
```

### Emergency Response

```bash
# P0: Kafka cluster down
systemctl restart kafka
kafka-broker-api-versions --bootstrap-server localhost:9092

# P0: Flink job failed
flink run -s hdfs:///flink/savepoints/savepoint-latest -c com.example.StreamProcessor target/stream-processor.jar

# P1: High consumer lag
flink modify <job-id> -p 8
kafka-topics --alter --bootstrap-server localhost:9092 --topic portfolio-events --partitions 20

# P1: Checkpoint failures
flink run -Dexecution.checkpointing.timeout=600000 -s hdfs:///flink/savepoints/savepoint-latest -c com.example.StreamProcessor target/stream-processor.jar

# Check overall health
kafka-broker-api-versions --bootstrap-server localhost:9092 && \
flink list -r && \
kafka-consumer-groups --bootstrap-server localhost:9092 --group flink-consumer-group --describe
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Data Engineering Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates
