# Monitoring Module

## Overview

This module creates comprehensive monitoring resources including CloudWatch dashboards, alarms, SNS topics for notifications, and log groups with retention policies.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Monitoring Stack                                    │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    CloudWatch Dashboard                               │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     │  │
│  │  │ ALB Metrics │ │ EC2 Metrics │ │ RDS Metrics │ │ NAT Metrics │     │  │
│  │  │ • Requests  │ │ • CPU       │ │ • CPU       │ │ • Bytes     │     │  │
│  │  │ • Latency   │ │ • Network   │ │ • Storage   │ │ • Packets   │     │  │
│  │  │ • Errors    │ │ • Count     │ │ • Conns     │ │ • Active    │     │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘     │  │
│  │  ┌─────────────────────────────────────────────────────────────┐     │  │
│  │  │                   CloudFront Metrics                        │     │  │
│  │  │  • Requests  • Cache Hit Rate  • Error Rates                │     │  │
│  │  └─────────────────────────────────────────────────────────────┘     │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      CloudWatch Alarms                                │  │
│  │                                                                       │  │
│  │  ┌────────────────────────────────────────────────────────────┐      │  │
│  │  │ ALB: 5xx Errors, Response Time, Unhealthy Hosts           │      │  │
│  │  ├────────────────────────────────────────────────────────────┤      │  │
│  │  │ EC2: High CPU Utilization                                  │      │  │
│  │  ├────────────────────────────────────────────────────────────┤      │  │
│  │  │ RDS: CPU, Storage, Connections                             │      │  │
│  │  ├────────────────────────────────────────────────────────────┤      │  │
│  │  │ Application: Error Count from Logs                         │      │  │
│  │  └────────────────────────────────────────────────────────────┘      │  │
│  │                             │                                         │  │
│  │                             ▼                                         │  │
│  │                    ┌────────────────┐                                │  │
│  │                    │   SNS Topic    │                                │  │
│  │                    │   (Alerts)     │                                │  │
│  │                    └───────┬────────┘                                │  │
│  │                            │                                         │  │
│  │           ┌────────────────┼────────────────┐                        │  │
│  │           ▼                ▼                ▼                        │  │
│  │      ┌─────────┐     ┌─────────┐     ┌─────────┐                    │  │
│  │      │  Email  │     │  Slack  │     │ PagerDuty│                    │  │
│  │      │ Notify  │     │ Webhook │     │  Alert  │                    │  │
│  │      └─────────┘     └─────────┘     └─────────┘                    │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    CloudWatch Log Groups                              │  │
│  │                                                                       │  │
│  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐            │  │
│  │  │ /application   │ │ /access        │ │ /error         │            │  │
│  │  │ (30 days)      │ │ (30 days)      │ │ (30 days)      │            │  │
│  │  └────────────────┘ └────────────────┘ └────────────────┘            │  │
│  │                                                                       │  │
│  │  ┌────────────────────────────────────────────────────────┐          │  │
│  │  │ Metric Filter: ERROR pattern → ErrorCount metric       │          │  │
│  │  └────────────────────────────────────────────────────────┘          │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Features

- **CloudWatch Dashboards**: Comprehensive infrastructure visualization
- **CloudWatch Alarms**: Pre-configured alarms for critical metrics
- **SNS Topics**: Alert notifications via email, Slack, or PagerDuty
- **Log Groups**: Centralized logging with retention policies
- **Metric Filters**: Extract metrics from log data
- **KMS Encryption**: Encrypted SNS topics and log groups

## Input Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| `name_prefix` | Prefix for resource names | `string` | - | Yes |
| `alert_email_addresses` | Email addresses for alerts | `list(string)` | `[]` | No |
| `kms_key_id` | KMS key for encryption | `string` | `null` | No |
| `log_retention_days` | Log retention period | `number` | `30` | No |
| `alb_arn_suffix` | ALB ARN suffix for metrics | `string` | `""` | No |
| `target_group_arn_suffix` | Target group ARN suffix | `string` | `""` | No |
| `asg_name` | ASG name for metrics | `string` | `""` | No |
| `rds_identifier` | RDS identifier for metrics | `string` | `""` | No |
| `nat_gateway_id` | NAT Gateway ID for metrics | `string` | `""` | No |
| `cloudfront_distribution_id` | CloudFront ID for metrics | `string` | `""` | No |
| `create_alarms` | Create CloudWatch alarms | `bool` | `true` | No |
| `alb_5xx_threshold` | ALB 5xx error threshold | `number` | `10` | No |
| `alb_response_time_threshold` | Response time threshold (sec) | `number` | `2` | No |
| `ec2_cpu_threshold` | EC2 CPU threshold (%) | `number` | `80` | No |
| `rds_cpu_threshold` | RDS CPU threshold (%) | `number` | `80` | No |
| `rds_storage_threshold` | RDS storage threshold (bytes) | `number` | `5368709120` | No |
| `tags` | Tags to apply to resources | `map(string)` | `{}` | No |

## Outputs

| Name | Description |
|------|-------------|
| `sns_topic_arn` | The ARN of the SNS alerts topic |
| `sns_topic_name` | The name of the SNS alerts topic |
| `application_log_group_name` | Application log group name |
| `application_log_group_arn` | Application log group ARN |
| `access_log_group_name` | Access log group name |
| `error_log_group_name` | Error log group name |
| `dashboard_name` | CloudWatch dashboard name |
| `dashboard_arn` | CloudWatch dashboard ARN |
| `alarm_arns` | Map of alarm names to ARNs |

## Example Usage

### Basic Monitoring

```hcl
module "monitoring" {
  source = "./modules/monitoring"

  name_prefix = "myapp-dev"

  alert_email_addresses = ["ops@example.com"]
  log_retention_days    = 14

  tags = {
    Environment = "dev"
    Project     = "myapp"
  }
}
```

### Full Infrastructure Monitoring

```hcl
module "monitoring" {
  source = "./modules/monitoring"

  name_prefix = "myapp-prod"

  # Alert recipients
  alert_email_addresses = [
    "ops@example.com",
    "oncall@example.com"
  ]

  # Encryption
  kms_key_id = module.security.kms_key_id

  # Log retention
  log_retention_days = 90

  # Resource identifiers for dashboard
  alb_arn_suffix             = module.compute.alb_arn_suffix
  target_group_arn_suffix    = module.compute.target_group_arn_suffix
  asg_name                   = module.compute.asg_name
  rds_identifier             = module.database.db_instance_identifier
  nat_gateway_id             = module.networking.nat_gateway_ids[0]
  cloudfront_distribution_id = module.storage.cloudfront_distribution_id

  # Alarm thresholds
  create_alarms               = true
  alb_5xx_threshold           = 5
  alb_response_time_threshold = 1
  ec2_cpu_threshold           = 70
  rds_cpu_threshold           = 70
  rds_storage_threshold       = 10737418240  # 10 GB

  tags = {
    Environment = "production"
  }
}
```

### Integration with Slack

```hcl
module "monitoring" {
  source = "./modules/monitoring"

  name_prefix = "myapp-prod"

  tags = {
    Environment = "production"
  }
}

# Slack integration via AWS Chatbot
resource "aws_chatbot_slack_channel_configuration" "alerts" {
  configuration_name = "${var.name_prefix}-alerts"
  slack_channel_id   = "C1234567890"
  slack_team_id      = "T1234567890"
  iam_role_arn       = aws_iam_role.chatbot.arn

  sns_topic_arns = [module.monitoring.sns_topic_arn]

  guardrail_policy_arns = [
    "arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess"
  ]
}
```

### Custom Alarms

```hcl
module "monitoring" {
  source = "./modules/monitoring"

  name_prefix   = "myapp-prod"
  create_alarms = true

  # Stricter thresholds for production
  alb_5xx_threshold           = 1
  alb_response_time_threshold = 0.5
  ec2_cpu_threshold           = 60
  rds_cpu_threshold           = 60
  rds_connections_threshold   = 50
  application_error_threshold = 5

  tags = {
    Environment = "production"
  }
}
```

## CloudWatch Dashboard Widgets

The dashboard includes these widgets (when resource IDs are provided):

### ALB Metrics
- Request Count (per minute)
- Target Response Time (avg, p95, p99)
- HTTP Errors (4xx, 5xx)

### EC2/ASG Metrics
- Instance Count (desired, in-service, total)
- CPU Utilization (average, maximum)
- Network I/O (in/out)

### RDS Metrics
- CPU Utilization
- Database Connections
- Free Storage Space
- Read/Write IOPS

### NAT Gateway Metrics
- Bytes In/Out
- Packets In/Out
- Active Connections

### CloudFront Metrics
- Request Count
- Cache Hit Rate
- Error Rates (4xx, 5xx)

## CloudWatch Alarms

Pre-configured alarms (when `create_alarms = true`):

| Alarm | Metric | Condition | Default Threshold |
|-------|--------|-----------|-------------------|
| ALB 5xx Errors | HTTPCode_ELB_5XX_Count | > threshold | 10 |
| ALB Response Time | TargetResponseTime | > threshold | 2 seconds |
| ALB Unhealthy Hosts | UnHealthyHostCount | > 0 | 0 |
| EC2 CPU High | CPUUtilization | > threshold | 80% |
| RDS CPU High | CPUUtilization | > threshold | 80% |
| RDS Storage Low | FreeStorageSpace | < threshold | 5 GB |
| RDS Connections High | DatabaseConnections | > threshold | 80 |
| Application Errors | ErrorCount (custom) | > threshold | 10 |

## Log Group Configuration

| Log Group | Purpose | Default Retention |
|-----------|---------|-------------------|
| `/aws/{prefix}/application` | Application logs | 30 days |
| `/aws/{prefix}/access` | Access logs | 30 days |
| `/aws/{prefix}/error` | Error logs | 30 days |

## Important Notes

1. **Email Confirmation**: SNS email subscriptions require confirmation before receiving alerts.

2. **CloudFront Metrics**: CloudFront metrics are always in `us-east-1` region.

3. **Alarm Actions**: All alarms trigger the SNS topic. Configure additional integrations as needed.

4. **Log Encryption**: Use `kms_key_id` for encrypted log groups in production.

5. **Metric Filters**: The error count filter looks for `ERROR` pattern in logs.

## Best Practices

- Set appropriate alarm thresholds based on baseline metrics
- Use different notification channels for different severity levels
- Enable detailed monitoring for EC2 instances
- Configure log insights queries for troubleshooting
- Set up composite alarms for complex conditions

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.4 |
| aws | ~> 5.0 |
