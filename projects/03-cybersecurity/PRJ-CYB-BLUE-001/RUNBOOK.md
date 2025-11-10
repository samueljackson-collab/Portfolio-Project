# Runbook — PRJ-CYB-BLUE-001 (AWS SIEM Pipeline with OpenSearch)

## Overview

Production operations runbook for AWS-based Security Information and Event Management (SIEM) pipeline. This runbook covers centralized log aggregation, real-time threat detection, security monitoring, incident response, and threat hunting operations for blue team defensive security.

**System Components:**
- AWS OpenSearch Service (3-node cluster)
- Kinesis Data Firehose (log ingestion)
- Lambda log transformers (normalization)
- AWS GuardDuty (threat detection)
- VPC Flow Logs (network monitoring)
- AWS CloudTrail (API audit logging)
- OpenSearch Dashboards (visualization)
- SNS alerting (notifications)
- CloudWatch monitoring (metrics/logs)

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Log ingestion latency** | < 5 minutes | CloudWatch → OpenSearch lag |
| **SIEM availability** | 99.9% | OpenSearch cluster uptime |
| **Alert detection time** | < 2 minutes | Event occurrence → alert trigger |
| **Critical alert response time** | < 15 minutes | Alert → analyst acknowledgment |
| **Log transformation success rate** | 99.5% | Successful Lambda transformations |
| **Dashboard load time** | < 3 seconds | Dashboard render performance |
| **Index health** | 100% green | OpenSearch cluster health |
| **Data retention compliance** | 100% | Logs retained per policy (90 days) |

---

## Dashboards & Alerts

### Dashboards

#### Security Overview Dashboard
```bash
# Access OpenSearch Dashboards
OPENSEARCH_ENDPOINT=$(aws opensearch describe-domain --domain-name security-siem --query 'DomainStatus.Endpoint' --output text)
echo "https://${OPENSEARCH_ENDPOINT}/_dashboards"

# Check current security posture
curl -X GET "https://${OPENSEARCH_ENDPOINT}/security-events-*/_count" \
  -H 'Content-Type: application/json' \
  -d '{"query": {"range": {"severity": {"gte": 7}}}}'

# View findings by severity (last 24h)
curl -X GET "https://${OPENSEARCH_ENDPOINT}/guardduty-findings-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 0,
    "query": {"range": {"@timestamp": {"gte": "now-24h"}}},
    "aggs": {"severity": {"terms": {"field": "severity"}}}
  }'

# Top affected resources
curl -X GET "https://${OPENSEARCH_ENDPOINT}/security-events-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 0,
    "aggs": {"resources": {"terms": {"field": "resource_id", "size": 10}}}
  }'
```

#### GuardDuty Threat Analysis Dashboard
```bash
# View threat types distribution
aws opensearch search \
  --index-name "guardduty-findings-*" \
  --body '{
    "size": 0,
    "aggs": {
      "threat_types": {
        "terms": {"field": "type.keyword", "size": 20}
      }
    }
  }'

# High-severity findings (last 7 days)
aws opensearch search \
  --index-name "guardduty-findings-*" \
  --body '{
    "query": {
      "bool": {
        "must": [
          {"range": {"severity": {"gte": 7}}},
          {"range": {"@timestamp": {"gte": "now-7d"}}}
        ]
      }
    },
    "sort": [{"severity": "desc"}, {"@timestamp": "desc"}],
    "size": 50
  }'

# Findings by service (EC2, S3, IAM)
aws opensearch search \
  --index-name "guardduty-findings-*" \
  --body '{
    "size": 0,
    "aggs": {"services": {"terms": {"field": "resource.resource_type.keyword"}}}
  }'
```

#### Network Activity Dashboard
```bash
# Top source IPs (last hour)
curl -X GET "https://${OPENSEARCH_ENDPOINT}/network-logs-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 0,
    "query": {"range": {"@timestamp": {"gte": "now-1h"}}},
    "aggs": {"top_sources": {"terms": {"field": "src_ip", "size": 20}}}
  }'

# Rejected connections analysis
curl -X GET "https://${OPENSEARCH_ENDPOINT}/network-logs-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {"term": {"action": "REJECT"}},
    "aggs": {
      "by_port": {"terms": {"field": "dst_port"}},
      "by_protocol": {"terms": {"field": "protocol"}}
    }
  }'

# Bandwidth usage timeline
curl -X GET "https://${OPENSEARCH_ENDPOINT}/network-logs-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 0,
    "aggs": {
      "bandwidth_over_time": {
        "date_histogram": {"field": "@timestamp", "interval": "1h"},
        "aggs": {"total_bytes": {"sum": {"field": "bytes"}}}
      }
    }
  }'
```

#### CloudTrail Audit Dashboard
```bash
# Failed authentication attempts
curl -X GET "https://${OPENSEARCH_ENDPOINT}/cloudtrail-events-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"term": {"errorCode.keyword": "UnauthorizedOperation"}},
          {"range": {"@timestamp": {"gte": "now-24h"}}}
        ]
      }
    },
    "size": 100,
    "sort": [{"@timestamp": "desc"}]
  }'

# Root account activity
curl -X GET "https://${OPENSEARCH_ENDPOINT}/cloudtrail-events-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "term": {"userIdentity.type.keyword": "Root"}
    },
    "size": 50,
    "sort": [{"@timestamp": "desc"}]
  }'

# Top API calls (last 24h)
curl -X GET "https://${OPENSEARCH_ENDPOINT}/cloudtrail-events-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 0,
    "query": {"range": {"@timestamp": {"gte": "now-24h"}}},
    "aggs": {"api_calls": {"terms": {"field": "eventName.keyword", "size": 10}}}
  }'
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | GuardDuty severity ≥ 8 (Critical) | Immediate | Emergency response, isolate resources |
| **P0** | Root account API calls | Immediate | Verify legitimacy, investigate |
| **P0** | GuardDuty/CloudTrail disabled | Immediate | Re-enable, investigate cause |
| **P1** | GuardDuty severity 7 (High) | 15 minutes | Investigate, contain if needed |
| **P1** | Failed logins > 5 in 10 min | 15 minutes | Check for brute force attack |
| **P1** | Security group 0.0.0.0/0 added | 30 minutes | Review change, remediate if unauthorized |
| **P2** | Data exfiltration > 10 GB | 1 hour | Investigate unusual data transfer |
| **P3** | Unauthorized access attempts | 4 hours | Review and document |

#### Alert Monitoring
```bash
# Check OpenSearch alerting monitors
aws opensearch describe-domain --domain-name security-siem \
  --query 'DomainStatus.AdvancedSecurityOptions'

# List recent SNS notifications
aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:security-alerts

# View recent CloudWatch alarms
aws cloudwatch describe-alarms \
  --alarm-name-prefix "SIEM-" \
  --state-value ALARM

# Check Lambda transformation errors
aws logs tail /aws/lambda/siem-log-transformer \
  --follow \
  --filter-pattern "ERROR"
```

---

## Standard Operations

### SIEM Pipeline Health Checks

#### Verify OpenSearch Cluster Status
```bash
# Check cluster health
OPENSEARCH_ENDPOINT=$(aws opensearch describe-domain --domain-name security-siem --query 'DomainStatus.Endpoint' --output text)

curl -X GET "https://${OPENSEARCH_ENDPOINT}/_cluster/health?pretty"

# Expected: status should be "green" or "yellow"
# Green = all primary and replica shards allocated
# Yellow = all primary shards allocated, some replicas missing
# Red = some primary shards not allocated (CRITICAL)

# Check node status
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_cat/nodes?v"

# Check index health
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_cat/indices?v&s=index"

# View cluster stats
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_cluster/stats?pretty"
```

#### Monitor Log Ingestion Pipeline
```bash
# Check Kinesis Firehose status
aws firehose describe-delivery-stream \
  --delivery-stream-name security-logs-stream \
  --query 'DeliveryStreamDescription.DeliveryStreamStatus'

# View Firehose metrics (last 5 minutes)
aws cloudwatch get-metric-statistics \
  --namespace AWS/Firehose \
  --metric-name IncomingRecords \
  --dimensions Name=DeliveryStreamName,Value=security-logs-stream \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Sum

# Check Lambda transformer health
aws lambda get-function \
  --function-name siem-log-transformer \
  --query 'Configuration.[State,LastUpdateStatus]'

# View Lambda errors (last 1 hour)
aws logs filter-log-events \
  --log-group-name /aws/lambda/siem-log-transformer \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --filter-pattern "ERROR"

# Check S3 backup bucket for failed records
aws s3 ls s3://siem-failed-records-bucket/ --recursive \
  --human-readable --summarize
```

#### Verify Log Sources
```bash
# Check GuardDuty status
aws guardduty list-detectors --query 'DetectorIds[0]' --output text | \
  xargs -I {} aws guardduty get-detector --detector-id {}

# List recent GuardDuty findings
DETECTOR_ID=$(aws guardduty list-detectors --query 'DetectorIds[0]' --output text)
aws guardduty list-findings \
  --detector-id $DETECTOR_ID \
  --finding-criteria '{
    "Criterion": {
      "updatedAt": {"gte": '$(date -d '24 hours ago' +%s)000'}
    }
  }'

# Check VPC Flow Logs status
aws ec2 describe-flow-logs \
  --filter "Name=resource-type,Values=VPC" \
  --query 'FlowLogs[*].[ResourceId,FlowLogStatus,DeliverLogsStatus]'

# Verify CloudTrail logging
aws cloudtrail get-trail-status --name security-trail \
  --query 'IsLogging'

# Check CloudTrail recent events
aws cloudtrail lookup-events \
  --max-results 10 \
  --query 'Events[*].[EventTime,EventName,Username]'
```

### Log Analysis & Threat Hunting

#### Search for Specific Threats
```bash
# Search for crypto mining indicators
curl -X GET "https://${OPENSEARCH_ENDPOINT}/guardduty-findings-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "should": [
          {"match": {"type": "CryptoCurrency"}},
          {"match": {"description": "mining"}}
        ]
      }
    }
  }'

# Search for data exfiltration patterns
curl -X GET "https://${OPENSEARCH_ENDPOINT}/network-logs-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "range": {"bytes": {"gte": 10737418240}}
    },
    "size": 50,
    "sort": [{"bytes": "desc"}]
  }'

# Search for unusual API activity
curl -X GET "https://${OPENSEARCH_ENDPOINT}/cloudtrail-events-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "should": [
          {"match": {"eventName": "DeleteBucket"}},
          {"match": {"eventName": "PutBucketPolicy"}},
          {"match": {"eventName": "ModifyInstanceAttribute"}}
        ]
      }
    },
    "size": 100,
    "sort": [{"@timestamp": "desc"}]
  }'

# Search for specific IP address activity
TARGET_IP="192.0.2.1"
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_search" \
  -H 'Content-Type: application/json' \
  -d "{
    \"query\": {
      \"multi_match\": {
        \"query\": \"${TARGET_IP}\",
        \"fields\": [\"src_ip\", \"dst_ip\", \"sourceIPAddress\"]
      }
    },
    \"size\": 100
  }"
```

#### Correlation Analysis
```bash
# Correlate GuardDuty findings with network logs
# Find instance with GuardDuty finding
INSTANCE_ID=$(curl -s -X GET "https://${OPENSEARCH_ENDPOINT}/guardduty-findings-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 1,
    "query": {"range": {"severity": {"gte": 7}}},
    "_source": ["resource.instanceDetails.instanceId"]
  }' | jq -r '.hits.hits[0]._source.resource.instanceDetails.instanceId')

# Search network logs for that instance
curl -X GET "https://${OPENSEARCH_ENDPOINT}/network-logs-*/_search" \
  -H 'Content-Type: application/json' \
  -d "{
    \"query\": {
      \"term\": {\"interface_id\": \"${INSTANCE_ID}\"}
    },
    \"size\": 100,
    \"sort\": [{\"@timestamp\": \"desc\"}]
  }"

# Correlate with CloudTrail events
curl -X GET "https://${OPENSEARCH_ENDPOINT}/cloudtrail-events-*/_search" \
  -H 'Content-Type: application/json' \
  -d "{
    \"query\": {
      \"match\": {\"resources.instanceId\": \"${INSTANCE_ID}\"}
    },
    \"size\": 50,
    \"sort\": [{\"@timestamp\": \"desc\"}]
  }"
```

#### Create Custom Searches
```bash
# Save a search query
curl -X POST "https://${OPENSEARCH_ENDPOINT}/.kibana/_doc/search:high-severity-threats" \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "search",
    "search": {
      "title": "High Severity Threats",
      "query": {
        "query": {
          "bool": {
            "must": [
              {"range": {"severity": {"gte": 7}}},
              {"range": {"@timestamp": {"gte": "now-24h"}}}
            ]
          }
        }
      }
    }
  }'

# Create aggregation for threat trend analysis
curl -X GET "https://${OPENSEARCH_ENDPOINT}/guardduty-findings-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 0,
    "query": {"range": {"@timestamp": {"gte": "now-30d"}}},
    "aggs": {
      "threats_over_time": {
        "date_histogram": {
          "field": "@timestamp",
          "interval": "day"
        },
        "aggs": {
          "severity_breakdown": {
            "terms": {"field": "severity"}
          }
        }
      }
    }
  }'
```

### Index Management

#### Monitor Index Size and Performance
```bash
# View all security indices
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_cat/indices/security-*,guardduty-*,network-*,cloudtrail-*?v&s=index"

# Check specific index details
curl -X GET "https://${OPENSEARCH_ENDPOINT}/guardduty-findings-*/_stats?pretty"

# View index mappings
curl -X GET "https://${OPENSEARCH_ENDPOINT}/guardduty-findings-*/_mapping?pretty"

# Check index settings
curl -X GET "https://${OPENSEARCH_ENDPOINT}/guardduty-findings-*/_settings?pretty"
```

#### Index Lifecycle Management
```bash
# Create index template for rotation
curl -X PUT "https://${OPENSEARCH_ENDPOINT}/_index_template/security-events-template" \
  -H 'Content-Type: application/json' \
  -d '{
    "index_patterns": ["security-events-*"],
    "template": {
      "settings": {
        "number_of_shards": 3,
        "number_of_replicas": 2,
        "refresh_interval": "5s"
      },
      "mappings": {
        "properties": {
          "@timestamp": {"type": "date"},
          "severity": {"type": "integer"},
          "source": {"type": "keyword"},
          "message": {"type": "text"}
        }
      }
    }
  }'

# Delete old indices (older than 90 days)
CUTOFF_DATE=$(date -d '90 days ago' +%Y.%m.%d)
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_cat/indices?h=index" | \
  grep -E "security-events-[0-9]{4}\.[0-9]{2}\.[0-9]{2}" | \
  while read index; do
    INDEX_DATE=$(echo $index | grep -oE "[0-9]{4}\.[0-9]{2}\.[0-9]{2}")
    if [[ "$INDEX_DATE" < "$CUTOFF_DATE" ]]; then
      echo "Deleting old index: $index"
      curl -X DELETE "https://${OPENSEARCH_ENDPOINT}/${index}"
    fi
  done

# Force merge old indices (optimize storage)
curl -X POST "https://${OPENSEARCH_ENDPOINT}/guardduty-findings-$(date -d '7 days ago' +%Y.%m.%d)/_forcemerge?max_num_segments=1"
```

#### Snapshot and Restore
```bash
# Create manual snapshot
curl -X PUT "https://${OPENSEARCH_ENDPOINT}/_snapshot/siem-snapshots/snapshot-$(date +%Y%m%d-%H%M%S)?wait_for_completion=false" \
  -H 'Content-Type: application/json' \
  -d '{
    "indices": "security-events-*,guardduty-findings-*,network-logs-*,cloudtrail-events-*",
    "ignore_unavailable": true,
    "include_global_state": false
  }'

# List snapshots
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_snapshot/siem-snapshots/_all?pretty"

# Check snapshot status
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_snapshot/siem-snapshots/snapshot-20251110-120000?pretty"

# Restore from snapshot
curl -X POST "https://${OPENSEARCH_ENDPOINT}/_snapshot/siem-snapshots/snapshot-20251110-120000/_restore" \
  -H 'Content-Type: application/json' \
  -d '{
    "indices": "guardduty-findings-2025.11.10",
    "ignore_unavailable": true,
    "include_global_state": false
  }'
```

### Alert Tuning and Management

#### Review and Adjust Alert Thresholds
```bash
# List all OpenSearch monitors
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_plugins/_alerting/monitors?pretty"

# Get specific monitor details
MONITOR_ID="high-severity-guardduty-monitor"
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_plugins/_alerting/monitors/${MONITOR_ID}?pretty"

# Update monitor threshold (e.g., reduce false positives)
curl -X PUT "https://${OPENSEARCH_ENDPOINT}/_plugins/_alerting/monitors/${MONITOR_ID}" \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "monitor",
    "name": "High Severity GuardDuty Findings",
    "enabled": true,
    "schedule": {
      "period": {
        "interval": 5,
        "unit": "MINUTES"
      }
    },
    "inputs": [{
      "search": {
        "indices": ["guardduty-findings-*"],
        "query": {
          "bool": {
            "must": [
              {"range": {"severity": {"gte": 8}}},
              {"range": {"@timestamp": {"gte": "now-10m"}}}
            ]
          }
        }
      }
    }],
    "triggers": [{
      "name": "Critical GuardDuty Finding",
      "severity": "1",
      "condition": {
        "script": {
          "source": "ctx.results[0].hits.total.value > 0"
        }
      },
      "actions": [{
        "name": "Send SNS notification",
        "destination_id": "sns-security-alerts",
        "message_template": {
          "source": "Critical GuardDuty finding detected: {{ctx.results.0.hits.hits.0._source.title}}"
        }
      }]
    }]
  }'

# Disable noisy monitor temporarily
curl -X PUT "https://${OPENSEARCH_ENDPOINT}/_plugins/_alerting/monitors/${MONITOR_ID}/_execute" \
  -H 'Content-Type: application/json' \
  -d '{"enabled": false}'
```

#### Create New Alert Rules
```bash
# Create monitor for failed authentication attempts
curl -X POST "https://${OPENSEARCH_ENDPOINT}/_plugins/_alerting/monitors" \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "monitor",
    "name": "Failed Authentication Attempts",
    "enabled": true,
    "schedule": {"period": {"interval": 10, "unit": "MINUTES"}},
    "inputs": [{
      "search": {
        "indices": ["cloudtrail-events-*"],
        "query": {
          "bool": {
            "must": [
              {"term": {"errorCode.keyword": "UnauthorizedOperation"}},
              {"range": {"@timestamp": {"gte": "now-10m"}}}
            ]
          }
        }
      }
    }],
    "triggers": [{
      "name": "Multiple Failed Logins",
      "severity": "2",
      "condition": {
        "script": {
          "source": "ctx.results[0].hits.total.value > 5"
        }
      },
      "actions": [{
        "name": "Alert Security Team",
        "destination_id": "sns-security-alerts",
        "message_template": {
          "source": "{{ctx.results.0.hits.total.value}} failed authentication attempts detected in the last 10 minutes"
        }
      }]
    }]
  }'

# Create monitor for data exfiltration
curl -X POST "https://${OPENSEARCH_ENDPOINT}/_plugins/_alerting/monitors" \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "monitor",
    "name": "Potential Data Exfiltration",
    "enabled": true,
    "schedule": {"period": {"interval": 15, "unit": "MINUTES"}},
    "inputs": [{
      "search": {
        "indices": ["network-logs-*"],
        "query": {
          "bool": {
            "must": [
              {"range": {"bytes": {"gte": 10737418240}}},
              {"range": {"@timestamp": {"gte": "now-15m"}}}
            ]
          }
        }
      }
    }],
    "triggers": [{
      "name": "Large Data Transfer Detected",
      "severity": "2",
      "condition": {
        "script": {
          "source": "ctx.results[0].hits.total.value > 0"
        }
      },
      "actions": [{
        "name": "Investigate Data Transfer",
        "destination_id": "sns-security-alerts",
        "message_template": {
          "source": "Large data transfer detected (>10GB): {{ctx.results.0.hits.hits.0._source.src_ip}} -> {{ctx.results.0.hits.hits.0._source.dst_ip}}"
        }
      }]
    }]
  }'
```

---

## Incident Response

### Detection

**Automated Detection Sources:**
- GuardDuty threat intelligence findings
- OpenSearch alert monitors
- CloudWatch alarms
- SNS notifications
- Lambda transformation failures
- Anomalous network traffic patterns
- Failed authentication attempts
- Unusual API activity

**Manual Detection:**
```bash
# Check for security incidents (last 24h)
curl -X GET "https://${OPENSEARCH_ENDPOINT}/guardduty-findings-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"range": {"severity": {"gte": 7}}},
          {"range": {"@timestamp": {"gte": "now-24h"}}}
        ]
      }
    },
    "size": 50,
    "sort": [{"severity": "desc"}, {"@timestamp": "desc"}]
  }'

# Review recent SNS alerts
aws sns list-subscriptions --query 'Subscriptions[?TopicArn==`arn:aws:sns:us-east-1:ACCOUNT_ID:security-alerts`]'

# Check CloudWatch alarms
aws cloudwatch describe-alarms --state-value ALARM --query 'MetricAlarms[*].[AlarmName,StateReason,StateUpdatedTimestamp]'

# Analyze failed Lambda transformations
aws logs filter-log-events \
  --log-group-name /aws/lambda/siem-log-transformer \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --filter-pattern "ERROR" \
  --query 'events[*].[timestamp,message]'
```

### Triage

#### Severity Classification

**P0: Critical Security Incident**
- GuardDuty severity ≥ 8 with confirmed exploitation
- Ransomware or malware detected
- Data breach confirmed (sensitive data exposed)
- Root account compromise
- Complete SIEM pipeline failure
- Critical infrastructure compromise

**P1: High Severity Security Event**
- GuardDuty severity 7 (high-severity threat)
- Suspected data exfiltration
- Brute force attack in progress
- Privilege escalation attempt
- Security group widely opened (0.0.0.0/0)
- GuardDuty or CloudTrail disabled

**P2: Medium Severity Security Event**
- GuardDuty severity 4-6
- Failed authentication attempts (< 10)
- Suspicious API activity
- Unauthorized resource access attempts
- Configuration drift from baseline
- Log ingestion delays

**P3: Low Severity Security Event**
- GuardDuty severity 0-3
- Informational findings
- Policy violations (non-critical)
- Performance degradation
- Index health issues (yellow status)

### Incident Response Procedures

#### P0: Ransomware or Malware Detection

**Immediate Actions (0-5 minutes):**
```bash
# 1. Identify infected resources from GuardDuty
DETECTOR_ID=$(aws guardduty list-detectors --query 'DetectorIds[0]' --output text)
FINDING_IDS=$(aws guardduty list-findings \
  --detector-id $DETECTOR_ID \
  --finding-criteria '{
    "Criterion": {
      "type": {"Eq": ["Backdoor:EC2/C&CActivity.B"]},
      "severity": {"Gte": 8}
    }
  }' --query 'FindingIds' --output text)

aws guardduty get-findings \
  --detector-id $DETECTOR_ID \
  --finding-ids $FINDING_IDS \
  --query 'Findings[*].Resource.InstanceDetails.InstanceId'

# 2. IMMEDIATELY isolate infected instances
for instance_id in $(aws guardduty get-findings --detector-id $DETECTOR_ID --finding-ids $FINDING_IDS --query 'Findings[*].Resource.InstanceDetails.InstanceId' --output text); do
  echo "Isolating instance: $instance_id"

  # Create isolation security group if not exists
  ISOLATION_SG=$(aws ec2 describe-security-groups \
    --filters Name=group-name,Values=isolation-quarantine \
    --query 'SecurityGroups[0].GroupId' --output text)

  if [ "$ISOLATION_SG" == "None" ]; then
    ISOLATION_SG=$(aws ec2 create-security-group \
      --group-name isolation-quarantine \
      --description "Isolation security group for quarantined instances" \
      --query 'GroupId' --output text)
  fi

  # Apply isolation security group (blocks all traffic)
  aws ec2 modify-instance-attribute \
    --instance-id $instance_id \
    --groups $ISOLATION_SG

  # Tag as quarantined
  aws ec2 create-tags \
    --resources $instance_id \
    --tags Key=SecurityStatus,Value=Quarantined Key=QuarantineReason,Value=Malware Key=QuarantineTime,Value=$(date -u +%Y-%m-%dT%H:%M:%SZ)
done

# 3. Create EBS snapshots for forensic analysis
for instance_id in $(aws guardduty get-findings --detector-id $DETECTOR_ID --finding-ids $FINDING_IDS --query 'Findings[*].Resource.InstanceDetails.InstanceId' --output text); do
  VOLUME_IDS=$(aws ec2 describe-instances \
    --instance-ids $instance_id \
    --query 'Reservations[*].Instances[*].BlockDeviceMappings[*].Ebs.VolumeId' \
    --output text)

  for volume_id in $VOLUME_IDS; do
    echo "Creating forensic snapshot of $volume_id"
    aws ec2 create-snapshot \
      --volume-id $volume_id \
      --description "Forensic snapshot - Malware incident $(date +%Y%m%d-%H%M%S)" \
      --tag-specifications "ResourceType=snapshot,Tags=[{Key=Purpose,Value=Forensics},{Key=IncidentDate,Value=$(date +%Y-%m-%d)}]"
  done
done

# 4. Notify security team and incident response
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:security-critical \
  --subject "P0: Malware Detection - Immediate Action Required" \
  --message "Malware detected on AWS resources. Infected instances have been isolated. Immediate investigation required. Finding IDs: $FINDING_IDS"

# 5. Document incident
cat > /tmp/incident-$(date +%Y%m%d-%H%M%S).md << EOF
# INCIDENT REPORT - MALWARE DETECTION

**Time:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Severity:** P0 - Critical
**Type:** Malware/Ransomware Detection
**Status:** Containment in progress

## Initial Detection
- GuardDuty Finding IDs: $FINDING_IDS
- Infected Resources: $(echo $instance_id)
- Detection Time: $(date)

## Immediate Actions Taken
- Instances isolated via security group
- Forensic snapshots created
- Security team notified
- Incident response initiated

## Next Steps
- Complete forensic analysis
- Determine attack vector
- Assess data impact
- Execute remediation plan
EOF
```

**Investigation (5-30 minutes):**
```bash
# Analyze GuardDuty finding details
aws guardduty get-findings \
  --detector-id $DETECTOR_ID \
  --finding-ids $FINDING_IDS \
  --query 'Findings[*].[Title,Description,Severity,Service.Action]' \
  --output table

# Check for lateral movement in CloudTrail
INSTANCE_ID="i-1234567890abcdef0"  # From GuardDuty finding
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=$INSTANCE_ID \
  --max-results 100 \
  --query 'Events[*].[EventTime,EventName,Username,SourceIPAddress]' \
  --output table

# Analyze network traffic for C2 communication
curl -X GET "https://${OPENSEARCH_ENDPOINT}/network-logs-*/_search" \
  -H 'Content-Type: application/json' \
  -d "{
    \"query\": {
      \"term\": {\"interface_id\": \"${INSTANCE_ID}\"}
    },
    \"size\": 100,
    \"sort\": [{\"@timestamp\": \"desc\"}]
  }" | jq '.hits.hits[] | {time: ._source."@timestamp", src: ._source.src_ip, dst: ._source.dst_ip, bytes: ._source.bytes}'

# Check for suspicious outbound connections
curl -X GET "https://${OPENSEARCH_ENDPOINT}/network-logs-*/_search" \
  -H 'Content-Type: application/json' \
  -d "{
    \"query\": {
      \"bool\": {
        \"must\": [
          {\"term\": {\"interface_id\": \"${INSTANCE_ID}\"}},
          {\"term\": {\"action\": \"ACCEPT\"}},
          {\"range\": {\"dst_port\": {\"gte\": 1024}}}
        ]
      }
    },
    \"size\": 50
  }"

# Review IAM activity from compromised instance
INSTANCE_ROLE=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].IamInstanceProfile.Arn' \
  --output text | cut -d'/' -f2)

aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=$INSTANCE_ROLE \
  --max-results 50 \
  --query 'Events[*].[EventTime,EventName,SourceIPAddress]'
```

**Containment and Remediation (30 minutes - 4 hours):**
```bash
# Revoke instance IAM credentials
aws ec2 disassociate-iam-instance-profile --association-id <association-id>

# Rotate any accessed secrets
aws secretsmanager rotate-secret --secret-id <secret-id>

# Terminate compromised instance (after forensics complete)
aws ec2 terminate-instances --instance-ids $INSTANCE_ID

# Launch clean replacement from known-good AMI
aws ec2 run-instances \
  --image-id ami-KNOWNGOOD \
  --instance-type t3.medium \
  --security-group-ids sg-PRODUCTION \
  --subnet-id subnet-PRODUCTION \
  --iam-instance-profile Name=SecureRole \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=Replacement-Clean},{Key=ReplacedInstance,Value='$INSTANCE_ID'}]'

# Update GuardDuty finding with remediation notes
aws guardduty update-findings-feedback \
  --detector-id $DETECTOR_ID \
  --finding-ids $FINDING_IDS \
  --feedback USEFUL \
  --comments "Instance isolated, forensics completed, instance terminated, clean replacement deployed"
```

#### P0: Data Exfiltration Detected

**Immediate Actions (0-10 minutes):**
```bash
# 1. Identify exfiltration event
curl -X GET "https://${OPENSEARCH_ENDPOINT}/network-logs-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "range": {"bytes": {"gte": 10737418240}}
    },
    "size": 10,
    "sort": [{"bytes": "desc"}, {"@timestamp": "desc"}]
  }' > /tmp/exfiltration-events.json

# Extract details
SOURCE_IP=$(jq -r '.hits.hits[0]._source.src_ip' /tmp/exfiltration-events.json)
DEST_IP=$(jq -r '.hits.hits[0]._source.dst_ip' /tmp/exfiltration-events.json)
BYTES=$(jq -r '.hits.hits[0]._source.bytes' /tmp/exfiltration-events.json)
INTERFACE_ID=$(jq -r '.hits.hits[0]._source.interface_id' /tmp/exfiltration-events.json)

echo "Potential exfiltration: $SOURCE_IP -> $DEST_IP ($BYTES bytes)"

# 2. Block external IP at network level
# Find associated instance
INSTANCE_ID=$(aws ec2 describe-network-interfaces \
  --network-interface-ids $INTERFACE_ID \
  --query 'NetworkInterfaces[0].Attachment.InstanceId' \
  --output text)

# Block destination IP via NACL or security group
VPC_ID=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].VpcId' \
  --output text)

# Add deny rule to NACL
aws ec2 create-network-acl-entry \
  --network-acl-id <nacl-id> \
  --rule-number 10 \
  --protocol -1 \
  --egress \
  --cidr-block ${DEST_IP}/32 \
  --rule-action deny

# 3. Isolate source instance
aws ec2 modify-instance-attribute \
  --instance-id $INSTANCE_ID \
  --groups sg-isolation-quarantine

# 4. Alert security team
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:security-critical \
  --subject "P0: Data Exfiltration Detected" \
  --message "Large data transfer detected: ${BYTES} bytes from ${SOURCE_IP} to ${DEST_IP}. Instance ${INSTANCE_ID} isolated."
```

**Investigation:**
```bash
# Determine what data was accessed
curl -X GET "https://${OPENSEARCH_ENDPOINT}/cloudtrail-events-*/_search" \
  -H 'Content-Type: application/json' \
  -d "{
    \"query\": {
      \"bool\": {
        \"must\": [
          {\"term\": {\"sourceIPAddress\": \"${SOURCE_IP}\"}},
          {\"terms\": {\"eventName.keyword\": [\"GetObject\", \"GetBucketLocation\", \"ListBucket\"]}}
        ]
      }
    },
    \"size\": 100
  }"

# Check IAM activity
curl -X GET "https://${OPENSEARCH_ENDPOINT}/cloudtrail-events-*/_search" \
  -H 'Content-Type: application/json' \
  -d "{
    \"query\": {
      \"match\": {\"resources.instanceId\": \"${INSTANCE_ID}\"}
    },
    \"size\": 50,
    \"sort\": [{\"@timestamp\": \"desc\"}]
  }"

# Forensic analysis of instance
aws ec2 create-snapshot \
  --volume-id $(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].BlockDeviceMappings[0].Ebs.VolumeId' --output text) \
  --description "Forensic snapshot - Data exfiltration incident"
```

#### P1: Brute Force Attack

**Response (0-15 minutes):**
```bash
# 1. Identify attack source
curl -X GET "https://${OPENSEARCH_ENDPOINT}/cloudtrail-events-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"term": {"errorCode.keyword": "UnauthorizedOperation"}},
          {"range": {"@timestamp": {"gte": "now-10m"}}}
        ]
      }
    },
    "aggs": {
      "attack_sources": {
        "terms": {"field": "sourceIPAddress.keyword", "size": 10}
      }
    }
  }' > /tmp/brute-force.json

# Extract attacker IPs
ATTACKER_IPS=$(jq -r '.aggregations.attack_sources.buckets[].key' /tmp/brute-force.json)

# 2. Block attacker IPs
for ip in $ATTACKER_IPS; do
  echo "Blocking IP: $ip"
  # Add to WAF IP set
  aws wafv2 update-ip-set \
    --name blocked-ips \
    --scope REGIONAL \
    --id <ip-set-id> \
    --addresses $(aws wafv2 get-ip-set --name blocked-ips --scope REGIONAL --id <ip-set-id> --query 'IPSet.Addresses' --output text) ${ip}/32

  # Add to NACL deny rule
  aws ec2 create-network-acl-entry \
    --network-acl-id <nacl-id> \
    --rule-number $((RANDOM % 32000 + 1)) \
    --protocol -1 \
    --ingress \
    --cidr-block ${ip}/32 \
    --rule-action deny
done

# 3. Force password reset for targeted accounts
TARGETED_USERS=$(jq -r '.hits.hits[]._source.userIdentity.principalId' /tmp/brute-force.json | sort -u)
for user in $TARGETED_USERS; do
  echo "Forcing password reset for: $user"
  aws iam update-login-profile \
    --user-name $user \
    --password-reset-required
done

# 4. Enable MFA requirement
aws iam put-user-policy \
  --user-name $user \
  --policy-name RequireMFA \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {"aws:MultiFactorAuthPresent": "false"}
      }
    }]
  }'
```

#### P1: Security Group Widely Opened (0.0.0.0/0)

**Response (0-30 minutes):**
```bash
# 1. Detect unauthorized security group changes
curl -X GET "https://${OPENSEARCH_ENDPOINT}/cloudtrail-events-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"terms": {"eventName.keyword": ["AuthorizeSecurityGroupIngress", "AuthorizeSecurityGroupEgress"]}},
          {"match": {"requestParameters.ipPermissions.items.ipRanges.items.cidrIp": "0.0.0.0/0"}}
        ]
      }
    },
    "size": 10,
    "sort": [{"@timestamp": "desc"}]
  }' > /tmp/sg-changes.json

# Extract details
SG_ID=$(jq -r '.hits.hits[0]._source.requestParameters.groupId' /tmp/sg-changes.json)
USER=$(jq -r '.hits.hits[0]._source.userIdentity.principalId' /tmp/sg-changes.json)
PORT=$(jq -r '.hits.hits[0]._source.requestParameters.ipPermissions.items[0].fromPort' /tmp/sg-changes.json)

# 2. IMMEDIATELY revoke the rule
aws ec2 revoke-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port $PORT \
  --cidr 0.0.0.0/0

# 3. Check if instances are exposed
EXPOSED_INSTANCES=$(aws ec2 describe-instances \
  --filters "Name=instance.group-id,Values=$SG_ID" \
  --query 'Reservations[*].Instances[*].InstanceId' \
  --output text)

echo "Exposed instances: $EXPOSED_INSTANCES"

# 4. Investigate who made the change and why
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=$SG_ID \
  --max-results 20

# 5. Notify and document
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:security-alerts \
  --subject "P1: Unauthorized Security Group Change" \
  --message "Security group $SG_ID was opened to 0.0.0.0/0 on port $PORT by $USER. Rule has been revoked. Investigate: $EXPOSED_INSTANCES"
```

### Post-Incident

**After Resolution:**
```bash
# 1. Document incident in detail
cat > incidents/incident-$(date +%Y%m%d-%H%M%S).md << 'EOF'
# Security Incident Report

**Incident ID:** INC-$(date +%Y%m%d-%H%M%S)
**Date:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Severity:** P0
**Type:** Malware Detection
**Status:** Resolved

## Timeline
- 10:15: GuardDuty alert triggered for EC2 malware
- 10:20: Incident confirmed, instance isolated
- 10:25: Forensic snapshots created
- 10:30: Security team assembled
- 11:00: Root cause identified (vulnerable application)
- 12:00: Instance terminated, clean replacement deployed
- 12:30: Verification complete, no data loss confirmed
- 13:00: Incident closed

## Root Cause
Unpatched web application with known RCE vulnerability exploited to deploy malware.

## Impact
- 1 EC2 instance compromised
- No data exfiltration detected
- 2-hour downtime for affected service
- No customer impact

## Action Items
- [x] Patch all instances with same vulnerability
- [x] Implement automated patching for critical CVEs
- [ ] Add vulnerability scanning to CI/CD pipeline
- [ ] Enhanced GuardDuty monitoring for exploitation indicators
- [ ] Security training for development team

## Lessons Learned
- Detection was fast (5 minutes)
- Isolation procedure worked well
- Need better vulnerability management process
- Forensic snapshot process should be automated

EOF

# 2. Update GuardDuty findings
aws guardduty update-findings-feedback \
  --detector-id $DETECTOR_ID \
  --finding-ids $FINDING_IDS \
  --feedback USEFUL \
  --comments "Incident resolved. Instance terminated. Clean deployment completed. No data loss."

# 3. Archive incident data
aws s3 cp incidents/incident-$(date +%Y%m%d)*.md \
  s3://security-incidents-archive/$(date +%Y)/$(date +%m)/

# 4. Generate post-incident report
cat > post-incident-report-$(date +%Y%m%d).md << 'EOF'
# Post-Incident Review

## What Went Well
- Fast detection (5 minutes from exploit to alert)
- Effective isolation procedure
- Clear communication during incident
- Forensic data successfully preserved

## What Could Be Improved
- Vulnerability patching was delayed
- No automated response for this threat type
- Incident runbook needs update
- Need better attack surface visibility

## Action Items
1. Implement automated patching (Owner: DevOps, Due: 2 weeks)
2. Update incident response playbooks (Owner: Security, Due: 1 week)
3. Deploy additional GuardDuty monitors (Owner: Security, Due: 3 days)
4. Conduct security training (Owner: Security, Due: 1 month)

EOF

# 5. Update metrics and KPIs
# Track MTTR (Mean Time To Resolve)
# Track MTTD (Mean Time To Detect)
# Update incident statistics
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: OpenSearch Cluster Status Red

**Symptoms:**
```bash
$ curl -X GET "https://${OPENSEARCH_ENDPOINT}/_cluster/health"
{"status":"red","number_of_nodes":3}
```

**Diagnosis:**
```bash
# Check which indices are red
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_cat/indices?v&health=red"

# Check shard allocation
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_cat/shards?v" | grep UNASSIGNED

# Check cluster allocation explanation
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_cluster/allocation/explain?pretty"

# Check node status
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_cat/nodes?v"
```

**Solution:**
```bash
# If disk space issue, delete old indices
curl -X DELETE "https://${OPENSEARCH_ENDPOINT}/old-index-name"

# If unassigned shards, force allocation
curl -X POST "https://${OPENSEARCH_ENDPOINT}/_cluster/reroute?retry_failed=true"

# If specific shard issue, manually allocate
curl -X POST "https://${OPENSEARCH_ENDPOINT}/_cluster/reroute" \
  -H 'Content-Type: application/json' \
  -d '{
    "commands": [{
      "allocate_replica": {
        "index": "guardduty-findings-2025.11.10",
        "shard": 0,
        "node": "node-1"
      }
    }]
  }'

# Last resort: recreate index from snapshot
curl -X DELETE "https://${OPENSEARCH_ENDPOINT}/problematic-index"
curl -X POST "https://${OPENSEARCH_ENDPOINT}/_snapshot/siem-snapshots/latest-snapshot/_restore" \
  -H 'Content-Type: application/json' \
  -d '{"indices": "problematic-index"}'
```

---

#### Issue: Log Ingestion Pipeline Stopped

**Symptoms:**
```bash
# No recent logs in OpenSearch
curl -X GET "https://${OPENSEARCH_ENDPOINT}/guardduty-findings-*/_search" \
  -d '{"query": {"range": {"@timestamp": {"gte": "now-10m"}}}}'
# Returns: "hits": {"total": {"value": 0}}
```

**Diagnosis:**
```bash
# Check Kinesis Firehose status
aws firehose describe-delivery-stream \
  --delivery-stream-name security-logs-stream \
  --query 'DeliveryStreamDescription.[DeliveryStreamStatus,Destinations[0].ExtendedS3DestinationDescription.ProcessingConfiguration]'

# Check Lambda function status
aws lambda get-function \
  --function-name siem-log-transformer \
  --query 'Configuration.[State,LastUpdateStatus,StateReason]'

# Check for Lambda errors
aws logs tail /aws/lambda/siem-log-transformer --since 1h --filter-pattern "ERROR"

# Check Firehose delivery errors
aws logs tail /aws/kinesisfirehose/security-logs-stream --since 1h

# Check source (CloudWatch Log Groups)
aws logs describe-log-streams \
  --log-group-name /aws/guardduty/findings \
  --order-by LastEventTime \
  --descending \
  --max-items 1 \
  --query 'logStreams[0].lastEventTimestamp'
```

**Solution:**
```bash
# If Lambda function failed, check and fix
aws lambda update-function-configuration \
  --function-name siem-log-transformer \
  --timeout 60 \
  --memory-size 512

# Restart Lambda by updating environment variable
aws lambda update-function-configuration \
  --function-name siem-log-transformer \
  --environment Variables={RESTART=$(date +%s)}

# If Firehose stopped, check IAM permissions
aws firehose describe-delivery-stream \
  --delivery-stream-name security-logs-stream \
  --query 'DeliveryStreamDescription.Destinations[0].ExtendedS3DestinationDescription.RoleARN'

# Test Firehose delivery manually
aws firehose put-record \
  --delivery-stream-name security-logs-stream \
  --record '{"Data":"dGVzdCBtZXNzYWdl"}'  # base64 encoded "test message"

# If CloudWatch subscription filter broken, recreate
aws logs put-subscription-filter \
  --log-group-name /aws/guardduty/findings \
  --filter-name guardduty-to-firehose \
  --filter-pattern "" \
  --destination-arn arn:aws:firehose:us-east-1:ACCOUNT_ID:deliverystream/security-logs-stream
```

---

#### Issue: High Lambda Transformation Errors

**Symptoms:**
```bash
# Many failed records in S3 backup bucket
aws s3 ls s3://siem-failed-records-bucket/ --recursive | wc -l
# Returns: 1500 (high number)
```

**Diagnosis:**
```bash
# Check Lambda error logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/siem-log-transformer \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --max-events 50

# Download and analyze failed records
aws s3 cp s3://siem-failed-records-bucket/ /tmp/failed-logs/ --recursive
head -100 /tmp/failed-logs/*.json

# Check Lambda metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=siem-log-transformer \
  --start-time $(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

**Solution:**
```bash
# Fix Lambda code if parsing error
# Download current Lambda code
aws lambda get-function --function-name siem-log-transformer \
  --query 'Code.Location' --output text | xargs wget -O lambda.zip

# Fix the code, then update
zip lambda-fixed.zip lambda_function.py
aws lambda update-function-code \
  --function-name siem-log-transformer \
  --zip-file fileb://lambda-fixed.zip

# Increase Lambda timeout/memory if needed
aws lambda update-function-configuration \
  --function-name siem-log-transformer \
  --timeout 120 \
  --memory-size 1024

# Reprocess failed records
for file in /tmp/failed-logs/*.json; do
  aws firehose put-record \
    --delivery-stream-name security-logs-stream \
    --record "Data=$(cat $file | base64)"
done
```

---

#### Issue: Dashboard Performance Degradation

**Symptoms:**
- OpenSearch Dashboards loading slowly (> 10 seconds)
- Queries timing out
- High CPU on OpenSearch nodes

**Diagnosis:**
```bash
# Check cluster performance
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_nodes/stats?pretty" | \
  jq '.nodes[] | {name: .name, cpu: .os.cpu.percent, memory: .jvm.mem.heap_used_percent}'

# Check slow queries
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_nodes/stats?pretty" | \
  jq '.nodes[].indices.search.query_time_in_millis'

# Check index size and shard count
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_cat/indices?v&s=docs.count:desc"

# Check running tasks
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_tasks?detailed=true&actions=*search*"
```

**Solution:**
```bash
# Force merge old indices to reduce segments
for index in $(curl -s -X GET "${OPENSEARCH_ENDPOINT}/_cat/indices" | awk '{print $3}' | grep "$(date -d '7 days ago' +%Y.%m.%d)"); do
  echo "Force merging $index"
  curl -X POST "https://${OPENSEARCH_ENDPOINT}/${index}/_forcemerge?max_num_segments=1"
done

# Clear cache
curl -X POST "https://${OPENSEARCH_ENDPOINT}/_cache/clear"

# Optimize queries by adding filters
# Instead of: match_all
# Use: range filter on @timestamp

# If cluster too small, scale up
aws opensearch update-domain-config \
  --domain-name security-siem \
  --cluster-config '{
    "InstanceType": "t3.medium.search",
    "InstanceCount": 3
  }'

# Add read replicas for frequently queried indices
curl -X PUT "https://${OPENSEARCH_ENDPOINT}/guardduty-findings-*/_settings" \
  -H 'Content-Type: application/json' \
  -d '{"index": {"number_of_replicas": 2}}'
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 1 hour (automated snapshots every hour)
- **RTO** (Recovery Time Objective): 4 hours (complete SIEM restoration)
- **Log Retention**: 90 days in hot storage, 1 year in S3 cold storage

### Backup Strategy

**Automated Snapshots:**
```bash
# OpenSearch automated snapshots are configured in Terraform
# Manual verification:
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_snapshot/siem-snapshots/_all?pretty"

# Check latest snapshot
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_snapshot/siem-snapshots/_current?pretty"

# Verify snapshot schedule
aws opensearch describe-domain --domain-name security-siem \
  --query 'DomainStatus.SnapshotOptions'
```

**Manual Backup:**
```bash
# Create on-demand snapshot
curl -X PUT "https://${OPENSEARCH_ENDPOINT}/_snapshot/siem-snapshots/manual-backup-$(date +%Y%m%d-%H%M%S)?wait_for_completion=false" \
  -H 'Content-Type: application/json' \
  -d '{
    "indices": "guardduty-findings-*,network-logs-*,cloudtrail-events-*,security-events-*",
    "ignore_unavailable": true,
    "include_global_state": false,
    "metadata": {
      "taken_by": "security-team",
      "taken_because": "pre-maintenance backup"
    }
  }'

# Export configurations
aws opensearch describe-domain --domain-name security-siem > /tmp/opensearch-config-backup.json
aws firehose describe-delivery-stream --delivery-stream-name security-logs-stream > /tmp/firehose-config-backup.json
aws lambda get-function --function-name siem-log-transformer > /tmp/lambda-config-backup.json

# Backup to S3
aws s3 cp /tmp/opensearch-config-backup.json s3://siem-config-backups/$(date +%Y/%m/%d)/
aws s3 cp /tmp/firehose-config-backup.json s3://siem-config-backups/$(date +%Y/%m/%d)/
aws s3 cp /tmp/lambda-config-backup.json s3://siem-config-backups/$(date +%Y/%m/%d)/
```

### Disaster Recovery Procedures

#### Complete SIEM Failure

**Recovery Steps (2-4 hours):**
```bash
# 1. Verify OpenSearch domain status
aws opensearch describe-domain --domain-name security-siem \
  --query 'DomainStatus.[DomainId,Processing,Deleted]'

# 2. If domain deleted or corrupted, restore from Terraform
cd terraform/
terraform plan -target=aws_opensearch_domain.security_siem
terraform apply -target=aws_opensearch_domain.security_siem

# 3. Wait for cluster to be available (20-30 minutes)
while true; do
  STATUS=$(aws opensearch describe-domain --domain-name security-siem --query 'DomainStatus.Processing' --output text)
  if [ "$STATUS" == "False" ]; then
    echo "Cluster is ready"
    break
  fi
  echo "Waiting for cluster... (status: $STATUS)"
  sleep 60
done

# 4. Restore from latest snapshot
LATEST_SNAPSHOT=$(curl -s -X GET "${OPENSEARCH_ENDPOINT}/_snapshot/siem-snapshots/_all" | \
  jq -r '.snapshots | sort_by(.start_time) | last | .snapshot')

curl -X POST "https://${OPENSEARCH_ENDPOINT}/_snapshot/siem-snapshots/${LATEST_SNAPSHOT}/_restore" \
  -H 'Content-Type: application/json' \
  -d '{
    "indices": "*",
    "ignore_unavailable": true,
    "include_global_state": false,
    "rename_pattern": "(.+)",
    "rename_replacement": "restored-$1"
  }'

# 5. Verify restoration
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_cat/indices?v"

# 6. Re-establish log ingestion
terraform apply -target=aws_kinesis_firehose_delivery_stream.security_logs
terraform apply -target=aws_lambda_function.log_transformer

# 7. Verify end-to-end flow
aws logs put-log-events \
  --log-group-name /aws/guardduty/findings \
  --log-stream-name test-stream \
  --log-events timestamp=$(date +%s)000,message='{"test":"recovery"}'

# Wait 5 minutes, then check OpenSearch
sleep 300
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_search?q=test:recovery"

# 8. Re-create dashboards and alerts
# Import saved dashboards from backup
curl -X POST "https://${OPENSEARCH_ENDPOINT}/.kibana/_bulk" \
  -H 'Content-Type: application/json' \
  --data-binary @dashboards-backup.ndjson
```

#### Data Loss (Index Corruption)

**Recovery Steps (30-60 minutes):**
```bash
# 1. Identify corrupted index
CORRUPTED_INDEX="guardduty-findings-2025.11.10"

# 2. Delete corrupted index
curl -X DELETE "https://${OPENSEARCH_ENDPOINT}/${CORRUPTED_INDEX}"

# 3. Restore from snapshot
curl -X POST "https://${OPENSEARCH_ENDPOINT}/_snapshot/siem-snapshots/latest/_restore" \
  -H 'Content-Type: application/json' \
  -d "{
    \"indices\": \"${CORRUPTED_INDEX}\",
    \"ignore_unavailable\": true
  }"

# 4. If no snapshot available, re-ingest from S3 archive
# CloudWatch Logs exports to S3 for long-term retention
aws s3 ls s3://cloudwatch-logs-archive/guardduty/2025/11/10/

# Download and re-ingest
aws s3 cp s3://cloudwatch-logs-archive/guardduty/2025/11/10/ /tmp/logs/ --recursive

for logfile in /tmp/logs/*.gz; do
  gunzip -c $logfile | while read line; do
    aws firehose put-record \
      --delivery-stream-name security-logs-stream \
      --record "Data=$(echo $line | base64)"
  done
done
```

---

## Maintenance Procedures

### Daily Tasks
```bash
# Run health checks
./scripts/siem-health-check.sh

# Check for critical alerts
curl -X GET "https://${OPENSEARCH_ENDPOINT}/guardduty-findings-*/_search" \
  -d '{"query": {"range": {"severity": {"gte": 8}}}}'

# Review SNS notifications
aws sns get-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:ACCOUNT_ID:security-alerts:subscription-id

# Check log ingestion lag
# Compare CloudWatch latest event vs OpenSearch latest document
CW_LATEST=$(aws logs describe-log-streams \
  --log-group-name /aws/guardduty/findings \
  --order-by LastEventTime \
  --descending \
  --max-items 1 \
  --query 'logStreams[0].lastEventTimestamp')

OS_LATEST=$(curl -s -X GET "${OPENSEARCH_ENDPOINT}/guardduty-findings-*/_search" \
  -d '{"size":1,"sort":[{"@timestamp":"desc"}]}' | \
  jq -r '.hits.hits[0]._source."@timestamp"' | date -f - +%s)

LAG=$((($CW_LATEST - $OS_LATEST*1000)/1000))
echo "Log ingestion lag: ${LAG} seconds"
if [ $LAG -gt 300 ]; then
  echo "WARNING: Lag exceeds 5 minutes!"
fi

# Monitor cluster health
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_cluster/health?pretty" | \
  jq '{status, active_shards_percent_as_number, number_of_pending_tasks}'
```

### Weekly Tasks
```bash
# Review alert effectiveness
# Check for noisy alerts (too many false positives)
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_plugins/_alerting/monitors/_search" \
  -d '{"size": 100}' | \
  jq '.hits.hits[] | {name: ._source.name, id: ._id}'

# Review GuardDuty findings trends
curl -X GET "https://${OPENSEARCH_ENDPOINT}/guardduty-findings-*/_search" \
  -d '{
    "size": 0,
    "query": {"range": {"@timestamp": {"gte": "now-7d"}}},
    "aggs": {
      "findings_by_day": {
        "date_histogram": {
          "field": "@timestamp",
          "interval": "day"
        },
        "aggs": {
          "severity": {
            "stats": {"field": "severity"}
          }
        }
      }
    }
  }'

# Check index sizes and plan for rotation
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_cat/indices?v&s=store.size:desc&h=index,store.size,docs.count"

# Optimize old indices
curl -X POST "https://${OPENSEARCH_ENDPOINT}/guardduty-findings-$(date -d '14 days ago' +%Y.%m.%d)/_forcemerge?max_num_segments=1"

# Test snapshot restore (disaster recovery drill)
LATEST_SNAPSHOT=$(curl -s -X GET "${OPENSEARCH_ENDPOINT}/_snapshot/siem-snapshots/_all" | \
  jq -r '.snapshots | sort_by(.start_time) | last | .snapshot')
echo "Latest snapshot: $LATEST_SNAPSHOT"

# Review Lambda performance
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=siem-log-transformer \
  --start-time $(date -d '7 days ago' -u +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Average,Maximum
```

### Monthly Tasks
```bash
# Full system audit
./scripts/siem-full-audit.sh

# Review and update alert rules
# Disable low-value alerts
# Add new threat detection rules based on latest threats

# Cost optimization
# Check CloudWatch Logs retention
aws logs describe-log-groups --query 'logGroups[*].[logGroupName,retentionInDays]'

# Check OpenSearch storage usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/ES \
  --metric-name FreeStorageSpace \
  --dimensions Name=DomainName,Value=security-siem,Name=ClientId,Value=ACCOUNT_ID \
  --start-time $(date -d '30 days ago' -u +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Average

# Delete indices older than retention period (90 days)
CUTOFF_DATE=$(date -d '90 days ago' +%Y.%m.%d)
curl -X GET "${OPENSEARCH_ENDPOINT}/_cat/indices?h=index" | \
  grep -E "[0-9]{4}\.[0-9]{2}\.[0-9]{2}" | \
  while read index; do
    INDEX_DATE=$(echo $index | grep -oE "[0-9]{4}\.[0-9]{2}\.[0-9]{2}")
    if [[ "$INDEX_DATE" < "$CUTOFF_DATE" ]]; then
      echo "Deleting index: $index (older than 90 days)"
      curl -X DELETE "${OPENSEARCH_ENDPOINT}/${index}"
    fi
  done

# Update threat intelligence
# GuardDuty automatically updates, but review findings categories
aws guardduty get-detector --detector-id $DETECTOR_ID

# Security patching review
aws lambda get-function --function-name siem-log-transformer \
  --query 'Configuration.Runtime'
# If runtime is deprecated, update to latest Python version

# Generate monthly report
./scripts/generate-monthly-security-report.sh > reports/security-report-$(date +%Y-%m).html
```

### Quarterly Tasks
```bash
# Major version upgrades
# Check for OpenSearch version updates
aws opensearch describe-domain --domain-name security-siem \
  --query 'DomainStatus.EngineVersion'

# Plan upgrade during maintenance window
aws opensearch upgrade-domain \
  --domain-name security-siem \
  --target-version OpenSearch_2.11

# Review access controls
# Audit Cognito user pool
aws cognito-idp list-users --user-pool-id <pool-id>

# Review IAM policies
aws iam get-policy-version \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/SIEMAccessPolicy \
  --version-id <version-id>

# Conduct security assessment
# Review GuardDuty coverage
aws guardduty get-detector --detector-id $DETECTOR_ID \
  --query 'DataSources'

# Test incident response procedures
# Simulate security incident and verify response
./scripts/simulate-security-incident.sh --type malware

# Update runbook
# Review and update this runbook based on learnings
git add RUNBOOK.md
git commit -m "Update runbook based on Q$(date +%q) review"
```

---

## Operational Best Practices

### Pre-Deployment Checklist
- [ ] OpenSearch cluster properly sized (t3.small minimum for prod)
- [ ] Multi-AZ deployment enabled
- [ ] Encryption at rest and in transit enabled
- [ ] Fine-grained access control configured
- [ ] Automated snapshots enabled (hourly)
- [ ] Log sources configured (GuardDuty, VPC Flow Logs, CloudTrail)
- [ ] Kinesis Firehose delivery stream tested
- [ ] Lambda transformation function tested with sample logs
- [ ] SNS topics configured for alerts
- [ ] OpenSearch Dashboards accessible via Cognito
- [ ] Alert rules created and tested
- [ ] CloudWatch alarms configured
- [ ] IAM roles and policies validated
- [ ] S3 bucket for failed records configured
- [ ] Log retention policies set (90 days)
- [ ] Cost alerts configured

### Security Monitoring Best Practices
- **Alert tuning**: Review and adjust weekly to reduce false positives
- **Threat hunting**: Conduct proactive searches daily for IOCs
- **Correlation**: Always correlate GuardDuty findings with CloudTrail and VPC Flow Logs
- **Baselines**: Establish normal behavior baselines for comparison
- **Documentation**: Document all security incidents thoroughly
- **Automation**: Automate response for common, low-risk incidents
- **Escalation**: Have clear escalation paths for P0/P1 incidents

### Performance Optimization
- **Index lifecycle**: Rotate indices daily, delete after 90 days
- **Force merge**: Merge old indices weekly to optimize storage
- **Query optimization**: Use time-based filters on all queries
- **Caching**: Enable query caching for frequently accessed data
- **Sharding**: Maintain 20-50GB per shard for optimal performance
- **Replicas**: Use 2 replicas minimum for production indices

---

## Quick Reference

### Most Common Operations
```bash
# Check SIEM health
curl -s https://${OPENSEARCH_ENDPOINT}/_cluster/health | jq '{status, nodes, shards}'

# View recent high-severity findings
curl -X GET "https://${OPENSEARCH_ENDPOINT}/guardduty-findings-*/_search" \
  -d '{"query": {"range": {"severity": {"gte": 7}}}, "size": 10, "sort": [{"@timestamp": "desc"}]}'

# Check log ingestion lag
aws cloudwatch get-metric-statistics \
  --namespace AWS/Firehose \
  --metric-name DeliveryToS3.DataFreshness \
  --dimensions Name=DeliveryStreamName,Value=security-logs-stream \
  --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average

# Search for specific IP
curl -X GET "https://${OPENSEARCH_ENDPOINT}/_search" \
  -d '{"query": {"multi_match": {"query": "192.0.2.1", "fields": ["src_ip", "dst_ip", "sourceIPAddress"]}}}'

# Create manual snapshot
curl -X PUT "https://${OPENSEARCH_ENDPOINT}/_snapshot/siem-snapshots/backup-$(date +%Y%m%d)"

# Delete old index
curl -X DELETE "https://${OPENSEARCH_ENDPOINT}/guardduty-findings-2024.01.01"
```

### Emergency Response
```bash
# P0: Malware detected - Isolate instance immediately
INSTANCE_ID="i-1234567890abcdef0"
aws ec2 modify-instance-attribute --instance-id $INSTANCE_ID --groups sg-isolation-quarantine
aws ec2 create-tags --resources $INSTANCE_ID --tags Key=SecurityStatus,Value=Quarantined

# P0: Data exfiltration - Block destination IP
DEST_IP="192.0.2.100"
aws ec2 create-network-acl-entry \
  --network-acl-id <nacl-id> \
  --rule-number 10 \
  --protocol -1 \
  --egress \
  --cidr-block ${DEST_IP}/32 \
  --rule-action deny

# P1: Brute force attack - Block attacker IP
ATTACKER_IP="198.51.100.50"
aws wafv2 update-ip-set \
  --name blocked-ips \
  --scope REGIONAL \
  --id <ip-set-id> \
  --addresses ${ATTACKER_IP}/32

# P1: Unauthorized SG change - Revoke rule
SG_ID="sg-1234567890abcdef0"
aws ec2 revoke-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0
```

### Important Links
- **OpenSearch Dashboards**: `https://${OPENSEARCH_ENDPOINT}/_dashboards`
- **GuardDuty Console**: https://console.aws.amazon.com/guardduty/
- **CloudWatch Logs**: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups
- **SNS Topics**: https://console.aws.amazon.com/sns/v3/home?region=us-east-1#/topics
- **Lambda Functions**: https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Blue Team / Security Engineering
- **Review Schedule:** Quarterly or after major security incidents
- **Related Docs**: [README.md](README.md), [DEPLOYMENT.md](DEPLOYMENT.md)
- **Feedback:** Create issue or submit PR with improvements
