# Monitoring Module

Creates monitoring primitives for the portfolio stack: SNS alerting topic with optional email subscribers, a CloudWatch dashboard, and RDS alarms when a database is provisioned.

## Inputs
- `project_tag` (string): Project tag prefix.
- `log_group_names` (list(string)): Log groups to apply retention to.
- `rds_identifier` (string, optional): RDS instance identifier to monitor.
- `alarm_emails` (list(string)): Email endpoints to subscribe to the SNS topic.
- `enable_rds_alarm` (bool): Whether to create CPU and storage alarms for RDS.
- `log_retention` (number): Retention for created log groups.
- `tags` (map(string)): Tags applied to all resources.

## Outputs
- `alert_topic_arn`: SNS topic for alerts.
- `dashboard_name`: CloudWatch dashboard name.
