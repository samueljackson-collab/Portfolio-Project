# OpenSearch Module Outputs

output "domain_id" {
  description = "ID of the OpenSearch domain"
  value       = aws_opensearch_domain.main.domain_id
}

output "domain_name" {
  description = "Name of the OpenSearch domain"
  value       = aws_opensearch_domain.main.domain_name
}

output "domain_arn" {
  description = "ARN of the OpenSearch domain"
  value       = aws_opensearch_domain.main.arn
}

output "domain_endpoint" {
  description = "Domain-specific endpoint for OpenSearch"
  value       = aws_opensearch_domain.main.endpoint
}

output "kibana_endpoint" {
  description = "Domain-specific endpoint for Kibana/OpenSearch Dashboards"
  value       = aws_opensearch_domain.main.dashboard_endpoint
}

output "security_group_id" {
  description = "Security group ID for OpenSearch domain"
  value       = aws_security_group.opensearch.id
}

output "log_group_names" {
  description = "CloudWatch log group names for OpenSearch logs"
  value = {
    application = aws_cloudwatch_log_group.opensearch_application.name
    index_slow  = aws_cloudwatch_log_group.opensearch_index_slow.name
    search_slow = aws_cloudwatch_log_group.opensearch_search_slow.name
    audit       = aws_cloudwatch_log_group.opensearch_audit.name
  }
}

output "alarm_names" {
  description = "CloudWatch alarm names for monitoring"
  value = {
    cluster_red     = aws_cloudwatch_metric_alarm.cluster_status_red.alarm_name
    cluster_yellow  = aws_cloudwatch_metric_alarm.cluster_status_yellow.alarm_name
    low_storage     = aws_cloudwatch_metric_alarm.free_storage_space.alarm_name
    high_cpu        = aws_cloudwatch_metric_alarm.cpu_utilization.alarm_name
    jvm_pressure    = aws_cloudwatch_metric_alarm.jvm_memory_pressure.alarm_name
  }
}

output "dashboard_url" {
  description = "URL to access OpenSearch Dashboards"
  value       = "https://${aws_opensearch_domain.main.dashboard_endpoint}/_dashboards"
}

output "access_url" {
  description = "URL to access OpenSearch API"
  value       = "https://${aws_opensearch_domain.main.endpoint}"
}
