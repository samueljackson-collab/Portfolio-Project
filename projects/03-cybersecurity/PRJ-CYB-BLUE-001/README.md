# PRJ-CYB-BLUE-001: AWS SIEM Pipeline with OpenSearch

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../../DOCUMENTATION_INDEX.md).


**Status:** 🟢 **COMPLETE**
**Category:** Cybersecurity / Blue Team / Security Engineering
**Technologies:** AWS OpenSearch, Kinesis Firehose, Lambda, GuardDuty, VPC Flow Logs, CloudTrail, Python

---

## Overview

Production-ready Security Information and Event Management (SIEM) pipeline built on AWS, providing centralized log aggregation, real-time threat detection, and security monitoring across cloud infrastructure.

**Key Capabilities:**
- **Centralized Log Aggregation**: Ingest logs from GuardDuty, VPC Flow Logs, and CloudTrail
- **Real-time Processing**: Lambda-based log transformation and normalization
- **Threat Detection**: Pre-configured detection rules and alerts
- **Security Dashboards**: Visual security posture monitoring
- **Scalable Architecture**: Serverless ingestion with managed OpenSearch

This project demonstrates blue team defensive security capabilities, AWS security service integration, and Security Operations Center (SOC) automation.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          AWS Security Sources                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │  GuardDuty   │    │ VPC Flow     │    │  CloudTrail  │              │
│  │  Findings    │    │  Logs        │    │  Events      │              │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘              │
│         │                   │                    │                       │
│         │                   │                    │                       │
│         └───────────────────┴────────────────────┘                       │
│                             │                                            │
│                             ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │              CloudWatch Logs (Log Groups)                       │    │
│  │  - /aws/guardduty/findings                                      │    │
│  │  - /aws/vpc/flow-logs                                           │    │
│  │  - /aws/cloudtrail/events                                       │    │
│  └──────────────────────────┬──────────────────────────────────────┘    │
│                             │                                            │
│                             ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │         CloudWatch Subscription Filters                         │    │
│  └──────────────────────────┬──────────────────────────────────────┘    │
│                             │                                            │
└─────────────────────────────┼──────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Kinesis Data Firehose                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  - Buffer: 5 MB or 300 seconds                                    │  │
│  │  - Transformation: Lambda (log normalization)                     │  │
│  │  - S3 Backup: Failed records                                      │  │
│  └────────────────────────┬──────────────────────────────────────────┘  │
└───────────────────────────┼──────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│               Lambda Log Transformer                                     │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Python 3.11 Function:                                            │  │
│  │  - Parse and normalize log formats                                │  │
│  │  - Add common schema fields (@timestamp, severity, source)        │  │
│  │  - Enrich with metadata (account, region, environment)            │  │
│  │  - Error handling and logging                                     │  │
│  └────────────────────────┬──────────────────────────────────────────┘  │
└───────────────────────────┼──────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│               AWS OpenSearch Service                                     │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  3-Node Cluster (t3.small.search across 3 AZs)                   │  │
│  │  - Encryption at rest (KMS)                                       │  │
│  │  - Encryption in transit (TLS)                                    │  │
│  │  - Fine-grained access control (Cognito)                          │  │
│  │  - Automated snapshots (daily, 30-day retention)                  │  │
│  └────────────────────────┬──────────────────────────────────────────┘  │
│                           │                                              │
│  ┌────────────────────────┴──────────────────────────────────────────┐  │
│  │                Index Templates & Mappings                         │  │
│  │  - security-events-*  - guardduty-findings-*                      │  │
│  │  - network-logs-*     - cloudtrail-events-*                       │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                   OpenSearch Dashboards                           │  │
│  │  - Security Overview (findings by severity, timeline, geo map)    │  │
│  │  - GuardDuty Deep Dive (detailed threat analysis)                 │  │
│  │  - Network Activity (top talkers, protocol distribution)          │  │
│  │  - CloudTrail Audit (API calls, failed auth, root usage)          │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    Alert Rules (Monitors)                         │  │
│  │  - High-severity GuardDuty findings (severity ≥ 7)                │  │
│  │  - Failed login attempts (>5 in 10 minutes)                       │  │
│  │  - Root account API calls                                         │  │
│  │  - Security group changes (allow 0.0.0.0/0)                       │  │
│  │  - Data exfiltration (bytes > threshold)                          │  │
│  │  - GuardDuty/CloudTrail disabled                                  │  │
│  └───────────────────────┬───────────────────────────────────────────┘  │
└───────────────────────────┼──────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       SNS Notifications                                  │
│  - Email alerts for critical findings                                   │
│  - Slack/PagerDuty integration (optional)                               │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## What's Implemented

### ✅ OpenSearch Domain

Production-ready OpenSearch cluster with security hardening:

**Cluster Configuration:**
- 3-node cluster across 3 availability zones
- Instance type: t3.small.search (adjustable)
- EBS storage: 20 GB per node with encryption
- Version: OpenSearch 2.11 (latest)

**Security:**
- VPC deployment in private subnets
- Encryption at rest using AWS KMS
- Encryption in transit with TLS 1.2+
- Fine-grained access control with Amazon Cognito
- IAM-based access policies
- Security group restrictions

**Availability:**
- Multi-AZ deployment for high availability
- Automated daily snapshots
- 30-day snapshot retention
- Zone-aware replica allocation

**Monitoring:**
- CloudWatch metrics for cluster health
- Alarms for disk space, CPU, memory
- Index and search performance metrics

### ✅ Log Ingestion Pipeline

Serverless log processing with Kinesis and Lambda:

**Kinesis Firehose Stream:**
- Buffer size: 5 MB or 300 seconds
- Lambda transformation enabled
- S3 backup for failed records
- CloudWatch error logging
- Auto-scaling based on throughput

**Lambda Log Transformer:**
- Runtime: Python 3.11
- Memory: 512 MB
- Timeout: 60 seconds
- Concurrent executions: 10

**Transformation Logic:**
- **GuardDuty**: Parse findings, extract severity, threat type, affected resources
- **VPC Flow Logs**: Normalize fields (src/dst IP, ports, bytes, packets, action)
- **CloudTrail**: Extract API calls, user identity, source IP, error codes
- **Common Schema**: Add @timestamp, severity, source, account_id, region
- **Enrichment**: Add tags, environment labels, custom metadata

**Error Handling:**
- Malformed logs sent to S3 backup bucket
- Failed transformations logged to CloudWatch
- Dead letter queue for persistent failures
- Retry logic with exponential backoff

### ✅ Log Sources

Security data from AWS native services:

**1. AWS GuardDuty**
- Threat intelligence-based detection
- Anomaly detection for EC2, S3, IAM
- Malware detection, cryptocurrency mining
- Findings exported to CloudWatch Logs
- Severity scoring (0-10)

**2. VPC Flow Logs**
- All VPCs in the account
- Capture accepted and rejected traffic
- Source/destination IPs and ports
- Protocol, bytes, packets
- Flow direction (ingress/egress)

**3. AWS CloudTrail**
- All API activity across AWS services
- Management events (create/delete resources)
- Data events (S3 object access, Lambda invocations)
- User identity and source IP
- Error codes and response elements

### ✅ OpenSearch Dashboards

Pre-configured visualizations for security monitoring:

**Dashboard 1: Security Overview**
- Findings by severity (pie chart)
- Security events timeline (area chart)
- Top affected resources (table)
- Geographic map of source IPs
- KPIs: Total events, high-severity findings, blocked IPs

**Dashboard 2: GuardDuty Deep Dive**
- Threat types distribution
- Findings by resource type
- Severity trend over time
- Detailed findings table with drill-down
- Affected IAM principals

**Dashboard 3: Network Activity**
- Top talkers (source/destination IPs)
- Protocol distribution (TCP, UDP, ICMP)
- Rejected connections by port
- Bandwidth usage timeline
- Geographic visualization of traffic

**Dashboard 4: CloudTrail Audit**
- API call frequency (top 10 actions)
- Failed authentication attempts
- Root account activity
- IAM changes timeline
- Service usage heatmap

### ✅ Alert Rules (OpenSearch Monitors)

Automated threat detection and alerting:

| Alert Name | Condition | Severity | Action |
|------------|-----------|----------|--------|
| High-Severity GuardDuty | severity ≥ 7 | Critical | SNS + Email |
| Failed Logins | >5 in 10 min | High | SNS + Email |
| Root Account Usage | Any API call | Critical | SNS + Email |
| Security Group Open | 0.0.0.0/0 added | High | SNS + Email |
| Data Exfiltration | bytes > 10 GB | High | SNS + Email |
| GuardDuty Disabled | service stopped | Critical | SNS + Email |
| CloudTrail Disabled | logging stopped | Critical | SNS + Email |
| Unauthorized Access | access denied >10 | Medium | SNS |

**Alert Delivery:**
- SNS topic for email notifications
- JSON payload with event details
- Links to OpenSearch for investigation
- Configurable notification frequency

---

## Project Status

**🟢 IMPLEMENTATION COMPLETE**

All components have been implemented and tested:

- [x] **OpenSearch Terraform module** - Production-ready cluster with HA, encryption, monitoring
- [x] **Kinesis Firehose configuration** - Serverless ingestion with Lambda transformation
- [x] **Lambda transformer function** - Python 3.11 log normalization (GuardDuty, CloudTrail, VPC)
- [x] **Log source configurations** - GuardDuty, CloudTrail, VPC Flow Logs integration
- [x] **Dashboard templates** - Security overview, threat analysis, network monitoring
- [x] **Alert rule definitions** - Critical security event monitoring with SNS alerts
- [x] **Deployment documentation** - Complete deployment guide with troubleshooting

**Infrastructure Code:** 2,300+ lines of production-ready Terraform and Python
**Test Coverage:** Comprehensive pytest suite with 15+ test cases
**Documentation:** Architecture diagrams, deployment guide, cost estimates

Ready for deployment to dev/staging/prod environments. See [DEPLOYMENT.md](DEPLOYMENT.md) for setup instructions.

---

**Project Lead:** Sam Jackson
**Status:** 🟢 Complete
**Completed:** November 6, 2025
**Technologies:** AWS OpenSearch, Kinesis, Lambda, Python, Terraform

**GitHub:** [samueljackson-collab/Portfolio-Project](https://github.com/samueljackson-collab/Portfolio-Project)
**LinkedIn:** [sams-jackson](https://www.linkedin.com/in/sams-jackson)
