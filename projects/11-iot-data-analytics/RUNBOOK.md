# Runbook — Project 11 (IoT Data Ingestion & Analytics)

## Overview

Production operations runbook for the IoT Data Ingestion & Analytics platform. This runbook covers MQTT telemetry ingestion, AWS IoT Core operations, stream processing, TimescaleDB management, and monitoring for edge-to-cloud IoT workloads.

**System Components:**
- Device simulator (MQTT telemetry generation)
- AWS IoT Core (message broker and rules engine)
- Kinesis Data Firehose (stream processing)
- TimescaleDB (time-series database)
- Grafana (visualization and analytics)
- IoT Rules (message routing and transformation)

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Message ingestion rate** | > 1000 msg/sec | AWS IoT Core metrics |
| **End-to-end latency** | < 5 seconds | Device → TimescaleDB timestamp delta |
| **Data loss rate** | < 0.01% | Sent vs stored message count |
| **Device connectivity** | 99.5% | Connected devices / total devices |
| **Query performance (p95)** | < 2 seconds | TimescaleDB query duration |
| **Anomaly detection latency** | < 30 seconds | Event time → alert time |
| **Dashboard refresh time** | < 3 seconds | Grafana panel load time |

---

## Dashboards & Alerts

### Dashboards

#### System Health Dashboard
```bash
# Check AWS IoT Core status
aws iot describe-endpoint --endpoint-type iot:Data-ATS

# Check active connections
aws iot list-things --thing-type-name IoTDevice --max-results 100

# Check message broker statistics
aws cloudwatch get-metric-statistics \
  --namespace AWS/IoT \
  --metric-name PublishIn.Success \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Check device simulator status
ps aux | grep device_simulator.py
tail -f logs/device_simulator.log
```

#### Data Ingestion Dashboard
```bash
# Check Kinesis Firehose delivery stream
aws firehose describe-delivery-stream \
  --delivery-stream-name iot-telemetry-stream

# Check delivery success rate
aws cloudwatch get-metric-statistics \
  --namespace AWS/Firehose \
  --metric-name DeliveryToS3.Success \
  --dimensions Name=DeliveryStreamName,Value=iot-telemetry-stream \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Check data freshness in TimescaleDB
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT device_id, MAX(timestamp) as last_reading,
   NOW() - MAX(timestamp) as staleness
   FROM telemetry
   GROUP BY device_id
   ORDER BY staleness DESC
   LIMIT 10;"
```

#### Device Health Dashboard
```bash
# Check device telemetry patterns
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT device_id,
   COUNT(*) as message_count,
   AVG(temperature) as avg_temp,
   AVG(humidity) as avg_humidity
   FROM telemetry
   WHERE timestamp > NOW() - INTERVAL '1 hour'
   GROUP BY device_id
   ORDER BY message_count DESC;"

# Check anomaly detection results
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT * FROM anomalies
   WHERE detected_at > NOW() - INTERVAL '24 hours'
   ORDER BY detected_at DESC
   LIMIT 20;"
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | AWS IoT Core unreachable | Immediate | Check AWS status, verify credentials |
| **P0** | No messages ingested > 5 min | Immediate | Check devices, IoT rules, Firehose |
| **P1** | Firehose delivery failures > 5% | 15 minutes | Check S3 permissions, Firehose config |
| **P1** | TimescaleDB connection lost | 15 minutes | Restart database, check resources |
| **P1** | > 50% devices offline | 30 minutes | Investigate network, device issues |
| **P2** | High ingestion latency (> 10s) | 1 hour | Check Kinesis throughput, optimize |
| **P2** | Anomaly detection not running | 1 hour | Restart detection job, check logs |
| **P3** | Individual device offline > 1 hour | 4 hours | Investigate specific device |

#### Alert Queries

```bash
# Check message ingestion rate
MESSAGE_RATE=$(aws cloudwatch get-metric-statistics \
  --namespace AWS/IoT \
  --metric-name PublishIn.Success \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum \
  --query 'Datapoints[0].Sum' \
  --output text)

if [ "$MESSAGE_RATE" == "None" ] || [ "$MESSAGE_RATE" -eq 0 ]; then
  echo "ALERT: No messages ingested in last 5 minutes"
fi

# Check Firehose delivery failures
DELIVERY_FAILURES=$(aws cloudwatch get-metric-statistics \
  --namespace AWS/Firehose \
  --metric-name DeliveryToS3.DataFreshness \
  --dimensions Name=DeliveryStreamName,Value=iot-telemetry-stream \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Maximum \
  --query 'Datapoints[0].Maximum' \
  --output text)

if [ "$DELIVERY_FAILURES" != "None" ] && [ $(echo "$DELIVERY_FAILURES > 300" | bc) -eq 1 ]; then
  echo "ALERT: Firehose delivery latency > 5 minutes"
fi

# Check database connectivity
if ! psql -h localhost -U postgres -d iot_analytics -c "SELECT 1" > /dev/null 2>&1; then
  echo "ALERT: Cannot connect to TimescaleDB"
  exit 1
fi

# Check stale data
STALE_DEVICES=$(psql -h localhost -U postgres -d iot_analytics -t -c \
  "SELECT COUNT(DISTINCT device_id)
   FROM telemetry
   WHERE device_id NOT IN (
     SELECT device_id FROM telemetry
     WHERE timestamp > NOW() - INTERVAL '10 minutes'
   );")

if [ "$STALE_DEVICES" -gt 10 ]; then
  echo "ALERT: $STALE_DEVICES devices have no recent data"
fi
```

---

## Standard Operations

### Device Simulator Operations

#### Start Device Simulator
```bash
# Start simulator with default settings (10 devices, 5s interval)
cd /home/user/Portfolio-Project/projects/11-iot-data-analytics
source venv/bin/activate
python src/device_simulator.py

# Start with custom configuration
python src/device_simulator.py \
  --device-count 50 \
  --interval 2 \
  --mqtt-broker ssl://iot.us-east-1.amazonaws.com:8883 \
  --topic iot/telemetry

# Run in background with logging
nohup python src/device_simulator.py --device-count 100 --interval 5 \
  > logs/device_simulator.log 2>&1 &
echo $! > simulator.pid

# Verify simulator is running
ps -p $(cat simulator.pid) && echo "Simulator running" || echo "Simulator not running"
tail -f logs/device_simulator.log
```

#### Stop Device Simulator
```bash
# Stop gracefully
kill $(cat simulator.pid)
rm simulator.pid

# Force stop if needed
pkill -f device_simulator.py

# Verify stopped
ps aux | grep device_simulator.py
```

#### Adjust Simulator Configuration
```bash
# Edit configuration
vim config/simulator_config.yaml

# Configuration example:
cat > config/simulator_config.yaml << 'EOF'
devices:
  count: 100
  prefix: "device-"

telemetry:
  interval_seconds: 5
  temperature_range: [15, 35]
  humidity_range: [30, 80]

mqtt:
  broker: ssl://iot.us-east-1.amazonaws.com:8883
  topic: iot/telemetry
  qos: 1

anomaly:
  probability: 0.05
  spike_factor: 2.5
EOF

# Restart simulator with new config
kill $(cat simulator.pid) 2>/dev/null
python src/device_simulator.py --config config/simulator_config.yaml &
echo $! > simulator.pid
```

### AWS IoT Core Operations

#### Manage IoT Things (Devices)
```bash
# Create new IoT thing
aws iot create-thing --thing-name device-101

# List all things
aws iot list-things --max-results 100

# Get thing details
aws iot describe-thing --thing-name device-101

# Update thing attributes
aws iot update-thing --thing-name device-101 \
  --attribute-payload '{"attributes":{"location":"warehouse-1","firmware":"v2.1"}}'

# Delete thing
aws iot delete-thing --thing-name device-101
```

#### Manage IoT Rules
```bash
# List IoT rules
aws iot list-topic-rules

# Get rule details
aws iot get-topic-rule --rule-name TelemetryToFirehose

# Create new rule
aws iot create-topic-rule --rule-name TelemetryToFirehose --topic-rule-payload '{
  "sql": "SELECT * FROM \"iot/telemetry\"",
  "actions": [{
    "firehose": {
      "deliveryStreamName": "iot-telemetry-stream",
      "roleArn": "arn:aws:iam::ACCOUNT:role/IoTFirehoseRole"
    }
  }],
  "ruleDisabled": false
}'

# Enable/disable rule
aws iot enable-topic-rule --rule-name TelemetryToFirehose
aws iot disable-topic-rule --rule-name TelemetryToFirehose

# Update rule
aws iot replace-topic-rule --rule-name TelemetryToFirehose --topic-rule-payload '{
  "sql": "SELECT *, timestamp() as ts FROM \"iot/telemetry\" WHERE temperature > 30",
  "actions": [{
    "firehose": {
      "deliveryStreamName": "iot-telemetry-stream",
      "roleArn": "arn:aws:iam::ACCOUNT:role/IoTFirehoseRole"
    }
  }]
}'

# Delete rule
aws iot delete-topic-rule --rule-name TelemetryToFirehose
```

#### Monitor MQTT Traffic
```bash
# Subscribe to MQTT topic for testing
aws iot-data publish \
  --topic iot/telemetry/test \
  --payload '{"device_id":"test-001","temperature":25.5,"humidity":60}'

# Monitor messages (requires mosquitto-clients)
mosquitto_sub \
  -h $(aws iot describe-endpoint --endpoint-type iot:Data-ATS --query endpointAddress --output text) \
  -p 8883 \
  --cafile certs/AmazonRootCA1.pem \
  --cert certs/device-cert.pem \
  --key certs/device-private.key \
  -t "iot/telemetry/#" \
  -v

# Check message publish metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/IoT \
  --metric-name PublishIn.Success \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum,Average
```

### Kinesis Firehose Operations

#### Manage Delivery Stream
```bash
# Check delivery stream status
aws firehose describe-delivery-stream \
  --delivery-stream-name iot-telemetry-stream

# Update delivery stream configuration
aws firehose update-destination \
  --delivery-stream-name iot-telemetry-stream \
  --current-delivery-stream-version-id 1 \
  --destination-id destinationId-1 \
  --extended-s3-destination-update '{
    "BufferHints": {
      "SizeInMBs": 5,
      "IntervalInSeconds": 300
    },
    "CompressionFormat": "GZIP"
  }'

# Check delivery metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Firehose \
  --metric-name IncomingRecords \
  --dimensions Name=DeliveryStreamName,Value=iot-telemetry-stream \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Put test record
aws firehose put-record \
  --delivery-stream-name iot-telemetry-stream \
  --record '{"Data":"eyJkZXZpY2VfaWQiOiJ0ZXN0LTAwMSIsInRlbXBlcmF0dXJlIjoyNS41fQo="}'
```

### TimescaleDB Operations

#### Database Management
```bash
# Connect to database
psql -h localhost -U postgres -d iot_analytics

# Check database size
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT pg_size_pretty(pg_database_size('iot_analytics'));"

# Check table sizes
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT tablename,
   pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
   FROM pg_tables
   WHERE schemaname = 'public'
   ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# Vacuum and analyze
psql -h localhost -U postgres -d iot_analytics -c "VACUUM ANALYZE telemetry;"

# Check chunk status (TimescaleDB hypertables)
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT chunk_name, range_start, range_end
   FROM timescaledb_information.chunks
   WHERE hypertable_name = 'telemetry'
   ORDER BY range_start DESC
   LIMIT 20;"
```

#### Data Queries and Analysis
```bash
# Get recent telemetry data
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT * FROM telemetry
   ORDER BY timestamp DESC
   LIMIT 100;"

# Aggregate by device
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT device_id,
   COUNT(*) as readings,
   AVG(temperature) as avg_temp,
   MIN(temperature) as min_temp,
   MAX(temperature) as max_temp
   FROM telemetry
   WHERE timestamp > NOW() - INTERVAL '24 hours'
   GROUP BY device_id
   ORDER BY readings DESC;"

# Time-series aggregation
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT time_bucket('5 minutes', timestamp) AS bucket,
   device_id,
   AVG(temperature) as avg_temp
   FROM telemetry
   WHERE timestamp > NOW() - INTERVAL '1 hour'
   GROUP BY bucket, device_id
   ORDER BY bucket DESC, device_id;"

# Export data to CSV
psql -h localhost -U postgres -d iot_analytics -c \
  "COPY (SELECT * FROM telemetry WHERE timestamp > NOW() - INTERVAL '1 day')
   TO STDOUT WITH CSV HEADER" > telemetry_export_$(date +%Y%m%d).csv
```

#### Data Retention Management
```bash
# Drop old data (older than 30 days)
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT drop_chunks('telemetry', INTERVAL '30 days');"

# Set retention policy
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT add_retention_policy('telemetry', INTERVAL '30 days');"

# Check retention policy
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT * FROM timescaledb_information.jobs
   WHERE proc_name = 'policy_retention';"

# Remove retention policy
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT remove_retention_policy('telemetry');"
```

### Grafana Dashboard Operations

#### Access and Manage Dashboards
```bash
# Access Grafana UI
# Navigate to: http://localhost:3000
# Default credentials: admin / admin

# Import dashboard from JSON
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboards/iot-overview.json

# Export dashboard
DASHBOARD_UID="iot-overview"
curl -s http://admin:admin@localhost:3000/api/dashboards/uid/$DASHBOARD_UID | \
  jq '.dashboard' > dashboards/iot-overview-backup.json

# List dashboards
curl -s http://admin:admin@localhost:3000/api/search | \
  jq '.[] | {title: .title, uid: .uid, tags: .tags}'

# Create alert notification channel
curl -X POST http://admin:admin@localhost:3000/api/alert-notifications \
  -H "Content-Type: application/json" \
  -d '{
    "name": "IoT Alerts",
    "type": "email",
    "isDefault": true,
    "settings": {
      "addresses": "ops@example.com"
    }
  }'
```

---

## Incident Response

### Detection

**Automated Detection:**
- AWS CloudWatch alarms
- TimescaleDB connection monitoring
- Grafana alert rules
- Device heartbeat monitoring

**Manual Detection:**
```bash
# Check system health
./scripts/health_check.sh

# Review recent errors
tail -100 logs/device_simulator.log | grep ERROR
aws logs tail /aws/iot/rules/TelemetryToFirehose --since 10m | grep ERROR

# Check data pipeline
aws firehose describe-delivery-stream --delivery-stream-name iot-telemetry-stream
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT COUNT(*) FROM telemetry WHERE timestamp > NOW() - INTERVAL '5 minutes';"
```

### Triage

#### Severity Classification

**P0: Complete Data Loss**
- AWS IoT Core unreachable
- All devices disconnected
- No data flowing to TimescaleDB
- Critical system component failure

**P1: Partial Data Loss**
- Firehose delivery stream stopped
- TimescaleDB connection lost
- > 50% devices offline
- High message loss rate (> 5%)

**P2: Degraded Performance**
- High ingestion latency (> 10 seconds)
- Some devices offline (< 50%)
- Slow database queries
- Anomaly detection delayed

**P3: Minor Issues**
- Individual device offline
- Grafana dashboard slow
- Non-critical alerts

### Incident Response Procedures

#### P0: No Data Ingestion

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check AWS IoT Core status
aws iot describe-endpoint --endpoint-type iot:Data-ATS

# 2. Check device simulator
ps aux | grep device_simulator.py
tail -20 logs/device_simulator.log

# 3. Check IoT rule status
aws iot get-topic-rule --rule-name TelemetryToFirehose

# 4. Check Firehose stream
aws firehose describe-delivery-stream --delivery-stream-name iot-telemetry-stream

# 5. Test end-to-end connectivity
python src/test_connectivity.py
```

**Investigation (5-20 minutes):**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check IoT policy and certificates
aws iot list-attached-policies --target arn:aws:iot:us-east-1:ACCOUNT:cert/CERT_ID

# Check CloudWatch logs for errors
aws logs tail /aws/iot/rules/TelemetryToFirehose --since 30m --follow

# Check S3 bucket for recent data
aws s3 ls s3://iot-telemetry-bucket/year=$(date +%Y)/month=$(date +%m)/day=$(date +%d)/

# Check TimescaleDB for recent inserts
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT MAX(timestamp) as last_insert FROM telemetry;"
```

**Recovery:**
```bash
# Restart device simulator
kill $(cat simulator.pid) 2>/dev/null
python src/device_simulator.py --device-count 100 --interval 5 &
echo $! > simulator.pid

# Enable IoT rule if disabled
aws iot enable-topic-rule --rule-name TelemetryToFirehose

# Restart Firehose if needed (recreate)
./scripts/recreate_firehose.sh

# Verify data flowing
watch -n 5 'psql -h localhost -U postgres -d iot_analytics -t -c \
  "SELECT COUNT(*) FROM telemetry WHERE timestamp > NOW() - INTERVAL \"1 minute\";"'
```

#### P1: High Message Loss Rate

**Investigation:**
```bash
# Check message publish vs storage counts
PUBLISHED=$(aws cloudwatch get-metric-statistics \
  --namespace AWS/IoT \
  --metric-name PublishIn.Success \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum \
  --query 'Datapoints[0].Sum' \
  --output text)

STORED=$(psql -h localhost -U postgres -d iot_analytics -t -c \
  "SELECT COUNT(*) FROM telemetry WHERE timestamp > NOW() - INTERVAL '1 hour';")

LOSS_RATE=$(echo "scale=2; (1 - $STORED / $PUBLISHED) * 100" | bc)
echo "Message loss rate: ${LOSS_RATE}%"

# Check Firehose delivery failures
aws cloudwatch get-metric-statistics \
  --namespace AWS/Firehose \
  --metric-name DeliveryToS3.Records \
  --dimensions Name=DeliveryStreamName,Value=iot-telemetry-stream \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Check S3 processing errors
aws logs tail /aws/lambda/iot-telemetry-processor --since 1h | grep ERROR
```

**Mitigation:**
```bash
# Increase Firehose buffer size (if buffering issues)
aws firehose update-destination \
  --delivery-stream-name iot-telemetry-stream \
  --current-delivery-stream-version-id 1 \
  --destination-id destinationId-1 \
  --extended-s3-destination-update '{
    "BufferHints": {
      "SizeInMBs": 10,
      "IntervalInSeconds": 60
    }
  }'

# Scale TimescaleDB if write throughput is issue
# Optimize database writes
psql -h localhost -U postgres -d iot_analytics -c \
  "ALTER TABLE telemetry SET (fillfactor = 90);"
psql -h localhost -U postgres -d iot_analytics -c \
  "ALTER TABLE telemetry SET (autovacuum_vacuum_scale_factor = 0.05);"

# Batch inserts if using Lambda
# Update Lambda configuration for higher concurrency
aws lambda put-function-concurrency \
  --function-name iot-telemetry-processor \
  --reserved-concurrent-executions 100
```

#### P1: TimescaleDB Connection Lost

**Investigation:**
```bash
# Check PostgreSQL service
sudo systemctl status postgresql

# Check connections
psql -h localhost -U postgres -c \
  "SELECT count(*) FROM pg_stat_activity;"

# Check database logs
sudo tail -100 /var/log/postgresql/postgresql-*.log

# Check disk space
df -h /var/lib/postgresql
```

**Recovery:**
```bash
# Restart PostgreSQL
sudo systemctl restart postgresql

# Verify TimescaleDB extension
psql -h localhost -U postgres -d iot_analytics -c "\dx"

# Reconnect and verify
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT 1;"

# If data corruption, restore from backup
./scripts/restore_timescaledb.sh backup/latest.dump
```

#### P2: High Ingestion Latency

**Investigation:**
```bash
# Check end-to-end latency
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT device_id,
   timestamp as sent_time,
   NOW() as received_time,
   NOW() - timestamp as latency
   FROM telemetry
   ORDER BY timestamp DESC
   LIMIT 20;"

# Check Firehose data freshness
aws cloudwatch get-metric-statistics \
  --namespace AWS/Firehose \
  --metric-name DeliveryToS3.DataFreshness \
  --dimensions Name=DeliveryStreamName,Value=iot-telemetry-stream \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average

# Check database write performance
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT schemaname, tablename,
   n_tup_ins as inserts,
   n_tup_upd as updates
   FROM pg_stat_user_tables
   WHERE tablename = 'telemetry';"
```

**Optimization:**
```bash
# Reduce Firehose buffering interval
aws firehose update-destination \
  --delivery-stream-name iot-telemetry-stream \
  --current-delivery-stream-version-id 1 \
  --destination-id destinationId-1 \
  --extended-s3-destination-update '{
    "BufferHints": {
      "SizeInMBs": 1,
      "IntervalInSeconds": 60
    }
  }'

# Optimize TimescaleDB
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT set_chunk_time_interval('telemetry', INTERVAL '6 hours');"

# Add indexes for common queries
psql -h localhost -U postgres -d iot_analytics -c \
  "CREATE INDEX IF NOT EXISTS idx_telemetry_device_time
   ON telemetry (device_id, timestamp DESC);"

# Increase database connections
sudo sed -i 's/max_connections = 100/max_connections = 200/' /etc/postgresql/*/main/postgresql.conf
sudo systemctl restart postgresql
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/iot-incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# IoT Platform Incident Report

**Date:** $(date)
**Severity:** P1
**Duration:** 45 minutes
**Component:** Kinesis Firehose delivery

## Timeline
- 14:00: Alert triggered - no data in TimescaleDB
- 14:05: Identified Firehose delivery stream stopped
- 14:10: Found IAM role permission issue
- 14:20: Updated IAM policy
- 14:30: Firehose delivery resumed
- 14:45: Verified data backlog processed

## Root Cause
IAM role for Firehose lost S3 write permissions due to policy update

## Action Items
- [ ] Implement IAM policy change alerts
- [ ] Add automated IAM permission validation
- [ ] Create Firehose delivery monitoring dashboard
- [ ] Document IAM role requirements

EOF

# Update monitoring
# Add new CloudWatch alarm for Firehose failures
aws cloudwatch put-metric-alarm \
  --alarm-name iot-firehose-delivery-failures \
  --alarm-description "Alert on Firehose delivery failures" \
  --metric-name DeliveryToS3.Success \
  --namespace AWS/Firehose \
  --statistic Sum \
  --period 300 \
  --threshold 0 \
  --comparison-operator LessThanThreshold \
  --evaluation-periods 2
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: Device Simulator Not Publishing Messages

**Symptoms:**
```bash
$ python src/device_simulator.py
ConnectionError: Unable to connect to AWS IoT endpoint
```

**Diagnosis:**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify IoT endpoint
aws iot describe-endpoint --endpoint-type iot:Data-ATS

# Check certificates
ls -la certs/
openssl x509 -in certs/device-cert.pem -noout -text

# Test MQTT connection
mosquitto_pub \
  -h $(aws iot describe-endpoint --endpoint-type iot:Data-ATS --query endpointAddress --output text) \
  -p 8883 \
  --cafile certs/AmazonRootCA1.pem \
  --cert certs/device-cert.pem \
  --key certs/device-private.key \
  -t "iot/test" \
  -m "test message"
```

**Solution:**
```bash
# Regenerate certificates if expired
aws iot create-keys-and-certificate \
  --set-as-active \
  --certificate-pem-outfile certs/device-cert.pem \
  --private-key-outfile certs/device-private.key

# Attach policy to certificate
CERT_ARN=$(aws iot list-certificates --query 'certificates[0].certificateArn' --output text)
aws iot attach-policy --policy-name IoTDevicePolicy --target $CERT_ARN

# Update configuration with new endpoint
aws iot describe-endpoint --endpoint-type iot:Data-ATS > config/iot_endpoint.json

# Restart simulator
python src/device_simulator.py
```

---

#### Issue: Data Not Appearing in TimescaleDB

**Symptoms:**
- IoT Core receiving messages
- Firehose showing delivery success
- No data in TimescaleDB

**Diagnosis:**
```bash
# Check S3 bucket for data files
aws s3 ls s3://iot-telemetry-bucket/ --recursive | tail -20

# Check if Lambda processor is running
aws lambda get-function --function-name iot-telemetry-processor

# Check Lambda logs for errors
aws logs tail /aws/lambda/iot-telemetry-processor --since 30m

# Verify database connection from Lambda
psql -h database-host -U postgres -d iot_analytics -c "SELECT 1;"
```

**Solution:**
```bash
# If S3 files exist but not processed, trigger Lambda manually
aws lambda invoke \
  --function-name iot-telemetry-processor \
  --payload '{"Records":[{"s3":{"bucket":{"name":"iot-telemetry-bucket"},"object":{"key":"year=2025/month=11/day=10/file.gz"}}}]}' \
  response.json

# Update Lambda environment variables if database connection fails
aws lambda update-function-configuration \
  --function-name iot-telemetry-processor \
  --environment Variables="{DB_HOST=new-host,DB_NAME=iot_analytics,DB_USER=postgres}"

# Manually process S3 file
aws s3 cp s3://iot-telemetry-bucket/year=2025/month=11/day=10/file.gz - | \
  gunzip | \
  psql -h localhost -U postgres -d iot_analytics -c \
    "COPY telemetry(device_id, timestamp, temperature, humidity) FROM STDIN CSV HEADER;"
```

---

#### Issue: High Query Latency in Grafana

**Symptoms:**
- Dashboards taking > 10 seconds to load
- Timeout errors on complex queries

**Diagnosis:**
```bash
# Check slow queries
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT query, calls, total_time, mean_time
   FROM pg_stat_statements
   ORDER BY mean_time DESC
   LIMIT 10;"

# Check table statistics
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT schemaname, tablename, n_live_tup, n_dead_tup
   FROM pg_stat_user_tables
   WHERE tablename = 'telemetry';"

# Check chunk count
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT COUNT(*) FROM timescaledb_information.chunks
   WHERE hypertable_name = 'telemetry';"
```

**Solution:**
```bash
# Create indexes for common query patterns
psql -h localhost -U postgres -d iot_analytics << 'EOF'
CREATE INDEX IF NOT EXISTS idx_telemetry_device_id ON telemetry (device_id);
CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_telemetry_device_timestamp ON telemetry (device_id, timestamp DESC);
EOF

# Create continuous aggregates for common time ranges
psql -h localhost -U postgres -d iot_analytics << 'EOF'
CREATE MATERIALIZED VIEW telemetry_hourly
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 hour', timestamp) AS bucket,
       device_id,
       AVG(temperature) AS avg_temp,
       AVG(humidity) AS avg_humidity,
       COUNT(*) AS reading_count
FROM telemetry
GROUP BY bucket, device_id;
EOF

# Refresh continuous aggregate
psql -h localhost -U postgres -d iot_analytics -c \
  "CALL refresh_continuous_aggregate('telemetry_hourly', NULL, NULL);"

# Vacuum and analyze
psql -h localhost -U postgres -d iot_analytics -c "VACUUM ANALYZE telemetry;"

# Adjust chunk interval
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT set_chunk_time_interval('telemetry', INTERVAL '12 hours');"
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 1 hour (backup frequency)
- **RTO** (Recovery Time Objective): 30 minutes (infrastructure recreation)

### Backup Strategy

**TimescaleDB Backup:**
```bash
# Full database backup
pg_dump -h localhost -U postgres -d iot_analytics -F c -f backup/iot_analytics_$(date +%Y%m%d).dump

# Backup to S3
pg_dump -h localhost -U postgres -d iot_analytics | \
  gzip | \
  aws s3 cp - s3://iot-backups/database/iot_analytics_$(date +%Y%m%d).sql.gz

# Automated backup script
cat > /etc/cron.daily/iot-db-backup << 'EOF'
#!/bin/bash
BACKUP_DATE=$(date +%Y%m%d-%H%M)
pg_dump -h localhost -U postgres -d iot_analytics | gzip > /backups/iot_analytics_$BACKUP_DATE.sql.gz
aws s3 cp /backups/iot_analytics_$BACKUP_DATE.sql.gz s3://iot-backups/database/
find /backups -name "iot_analytics_*.sql.gz" -mtime +7 -delete
EOF
chmod +x /etc/cron.daily/iot-db-backup
```

**Infrastructure Backup:**
```bash
# Backup Terraform state
cd infrastructure/
terraform state pull > backup/terraform_state_$(date +%Y%m%d).json
aws s3 cp backup/terraform_state_$(date +%Y%m%d).json s3://iot-backups/terraform/

# Backup AWS IoT configurations
aws iot list-topic-rules | \
  jq . > backup/iot_rules_$(date +%Y%m%d).json

aws iot list-things | \
  jq . > backup/iot_things_$(date +%Y%m%d).json

# Backup Grafana dashboards
./scripts/backup_grafana_dashboards.sh
```

**S3 Data Backup:**
```bash
# Enable S3 versioning
aws s3api put-bucket-versioning \
  --bucket iot-telemetry-bucket \
  --versioning-configuration Status=Enabled

# Set up S3 lifecycle for archiving
aws s3api put-bucket-lifecycle-configuration \
  --bucket iot-telemetry-bucket \
  --lifecycle-configuration '{
    "Rules": [{
      "Id": "ArchiveOldData",
      "Status": "Enabled",
      "Transitions": [{
        "Days": 30,
        "StorageClass": "GLACIER"
      }],
      "Expiration": {
        "Days": 365
      }
    }]
  }'

# Cross-region replication
aws s3api put-bucket-replication \
  --bucket iot-telemetry-bucket \
  --replication-configuration file://replication-config.json
```

### Disaster Recovery Procedures

#### Complete Infrastructure Loss

**Recovery Steps (30-60 minutes):**
```bash
# 1. Clone infrastructure repository
git clone https://github.com/org/iot-platform-infra.git
cd iot-platform-infra

# 2. Deploy infrastructure with Terraform
cd infrastructure/
terraform init
terraform plan -out=tfplan
terraform apply tfplan

# 3. Restore TimescaleDB
aws s3 cp s3://iot-backups/database/latest.sql.gz - | \
  gunzip | \
  psql -h new-database-host -U postgres -d iot_analytics

# 4. Verify database restoration
psql -h new-database-host -U postgres -d iot_analytics -c \
  "SELECT COUNT(*) FROM telemetry;"

# 5. Update AWS IoT rules with new endpoints
aws iot replace-topic-rule --rule-name TelemetryToFirehose \
  --topic-rule-payload file://iot_rules/telemetry_to_firehose.json

# 6. Restore Grafana dashboards
cd dashboards/
for file in *.json; do
  curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
    -H "Content-Type: application/json" \
    -d @$file
done

# 7. Restart device simulator
python src/device_simulator.py --device-count 100 --interval 5 &

# 8. Verify end-to-end data flow
./scripts/verify_data_flow.sh
```

#### Database Restoration

**Recovery Steps (15-20 minutes):**
```bash
# 1. Stop device simulator to prevent new data
kill $(cat simulator.pid) 2>/dev/null

# 2. Download latest backup
aws s3 cp s3://iot-backups/database/latest.sql.gz .

# 3. Drop and recreate database
psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS iot_analytics;"
psql -h localhost -U postgres -c "CREATE DATABASE iot_analytics;"

# 4. Restore from backup
gunzip < latest.sql.gz | psql -h localhost -U postgres -d iot_analytics

# 5. Verify restoration
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT COUNT(*), MAX(timestamp) FROM telemetry;"

# 6. Restart simulator
python src/device_simulator.py --device-count 100 --interval 5 &
echo $! > simulator.pid
```

---

## Maintenance Procedures

### Daily Tasks
```bash
# Check system health
./scripts/health_check.sh

# Verify device connectivity
CONNECTED=$(aws iot list-things --thing-type-name IoTDevice | jq '.things | length')
echo "Connected devices: $CONNECTED"

# Check data freshness
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT MAX(timestamp) as last_data, NOW() - MAX(timestamp) as age FROM telemetry;"

# Review Grafana alerts
curl -s http://admin:admin@localhost:3000/api/alerts | \
  jq '.[] | select(.state=="alerting")'

# Check CloudWatch alarms
aws cloudwatch describe-alarms --state-value ALARM
```

### Weekly Tasks
```bash
# Analyze data patterns
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT date_trunc('day', timestamp) as day,
   COUNT(*) as messages,
   COUNT(DISTINCT device_id) as active_devices
   FROM telemetry
   WHERE timestamp > NOW() - INTERVAL '7 days'
   GROUP BY day
   ORDER BY day;"

# Review anomaly detection results
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT device_id, COUNT(*) as anomaly_count
   FROM anomalies
   WHERE detected_at > NOW() - INTERVAL '7 days'
   GROUP BY device_id
   ORDER BY anomaly_count DESC;"

# Optimize database
psql -h localhost -U postgres -d iot_analytics -c "VACUUM ANALYZE;"

# Update Grafana dashboards
git pull origin main
cd dashboards/
./import_all.sh

# Review costs
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=SERVICE
```

### Monthly Tasks
```bash
# Review and adjust retention policies
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT * FROM timescaledb_information.jobs WHERE proc_name = 'policy_retention';"

# Compress old chunks
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT compress_chunk(c) FROM show_chunks('telemetry', older_than => INTERVAL '7 days') c;"

# Update device firmware (if applicable)
aws iot create-job \
  --job-id firmware-update-$(date +%Y%m%d) \
  --targets "arn:aws:iot:us-east-1:ACCOUNT:thinggroup/production-devices" \
  --document file://jobs/firmware_update_v2.1.json

# Security audit
aws iot list-attached-policies --target arn:aws:iot:us-east-1:ACCOUNT:cert/*
aws iam get-role-policy --role-name IoTFirehoseRole --policy-name FirehosePolicy

# Update infrastructure
cd infrastructure/
terraform plan
# Review changes, then apply if needed
terraform apply

# Archive old data
./scripts/archive_old_data.sh --older-than 90days

# DR drill
./scripts/disaster_recovery_drill.sh
```

---

## Quick Reference

### Most Common Operations
```bash
# Start device simulator
python src/device_simulator.py --device-count 100 --interval 5

# Check data flow
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT COUNT(*) FROM telemetry WHERE timestamp > NOW() - INTERVAL '1 minute';"

# Check AWS IoT metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/IoT \
  --metric-name PublishIn.Success \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# View recent telemetry
psql -h localhost -U postgres -d iot_analytics -c \
  "SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT 20;"

# Check Grafana dashboards
# http://localhost:3000 (admin/admin)

# Export data
psql -h localhost -U postgres -d iot_analytics -c \
  "COPY (SELECT * FROM telemetry WHERE timestamp > NOW() - INTERVAL '1 day')
   TO STDOUT CSV HEADER" > export.csv
```

### Emergency Response
```bash
# P0: No data ingestion
python src/test_connectivity.py
kill $(cat simulator.pid) 2>/dev/null
python src/device_simulator.py --device-count 100 --interval 5 &
echo $! > simulator.pid

# P1: Firehose delivery failures
aws firehose describe-delivery-stream --delivery-stream-name iot-telemetry-stream
aws iot enable-topic-rule --rule-name TelemetryToFirehose

# P1: Database connection lost
sudo systemctl restart postgresql
psql -h localhost -U postgres -d iot_analytics -c "SELECT 1;"

# P2: High latency
./scripts/optimize_database.sh
aws firehose update-destination --delivery-stream-name iot-telemetry-stream \
  --current-delivery-stream-version-id 1 \
  --destination-id destinationId-1 \
  --extended-s3-destination-update '{"BufferHints":{"SizeInMBs":1,"IntervalInSeconds":60}}'
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** IoT Platform Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates
