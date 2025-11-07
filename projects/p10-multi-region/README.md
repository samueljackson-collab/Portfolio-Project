# P10 — Multi-Region Architecture

## Overview
Active-passive multi-region AWS architecture with Route 53 DNS failover, cross-region RDS read replicas, and automated disaster recovery. Demonstrates global infrastructure design, high availability, and business continuity planning.

## Key Outcomes
- [x] Active-passive multi-region deployment (us-east-1, us-west-2)
- [x] Route 53 health checks and failover policies
- [x] Cross-region RDS read replicas with promotion capability
- [x] S3 cross-region replication for static assets
- [x] CloudFormation stack sets for multi-region deployment
- [x] Automated failover testing scripts

## Architecture

```mermaid
flowchart TB
    Users[Global Users]
    R53[Route 53<br/>Health Check + Failover]

    subgraph Primary[Primary Region - us-east-1]
        ALB1[Application Load Balancer]
        EC21[EC2 Auto Scaling]
        RDS1[(RDS Primary)]
        S31[S3 Bucket]
    end

    subgraph Secondary[Secondary Region - us-west-2]
        ALB2[Application Load Balancer]
        EC22[EC2 Auto Scaling<br/>Standby]
        RDS2[(RDS Read Replica)]
        S32[S3 Bucket<br/>Replica]
    end

    Users --> R53
    R53 -->|Primary| ALB1
    R53 -.->|Failover| ALB2
    ALB1 --> EC21 --> RDS1
    ALB2 --> EC22 --> RDS2
    S31 -.->|CRR| S32
    RDS1 -.->|Async Replication| RDS2
```

## Quickstart

```bash
make setup
make deploy-primary
make deploy-secondary
make test-failover
```

## Configuration

| Env Var | Purpose | Example | Required |
|---------|---------|---------|----------|
| `PRIMARY_REGION` | Primary AWS region | `us-east-1` | Yes |
| `SECONDARY_REGION` | Secondary AWS region | `us-west-2` | Yes |
| `DOMAIN_NAME` | Route 53 domain | `example.com` | Yes |
| `RTO_MINUTES` | Recovery Time Objective | `15` | No |
| `RPO_MINUTES` | Recovery Point Objective | `5` | No |

## Testing

```bash
# Deploy to both regions
make deploy-all

# Test failover mechanism
make test-failover

# Validate Route 53 health checks
make check-health

# Simulate primary region failure
make simulate-outage
```

## Operations

### Logs, Metrics, Traces
- **CloudWatch Logs**: Centralized logging from both regions
- **Route 53 Health Checks**: Monitor endpoint availability
- **RDS Metrics**: Replication lag, IOPS, connections
- **Cross-Region Metrics**: Data transfer, sync status

### Common Issues & Fixes

**Issue**: High replication lag between regions
**Fix**: Increase RDS instance size, check network connectivity, reduce write load.

**Issue**: Route 53 failover not triggering
**Fix**: Verify health check configuration, ensure endpoints return correct HTTP status codes.

## Security

- Encrypted data in transit (TLS 1.2+)
- Encrypted data at rest (KMS with separate keys per region)
- IAM roles with least privilege
- VPC peering for cross-region communication

## Roadmap

- [ ] Add active-active configuration with DynamoDB Global Tables
- [ ] Implement automated failback procedures
- [ ] Add cross-region Lambda@Edge for edge caching
- [ ] Integrate AWS Backup for centralized backup management

## References

- [AWS Multi-Region Architecture](https://docs.aws.amazon.com/whitepapers/latest/real-time-communication-on-aws/multi-region-deployment.html)
- [Route 53 Health Checks](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-failover.html)
- [RDS Read Replicas](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html)
