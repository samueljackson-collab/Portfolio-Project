output "bucket_name" {
  description = "State bucket name"
  value       = var.bucket_name
}

output "dynamodb_table_name" {
  description = "State lock table name"
  value       = var.dynamodb_table_name
}
