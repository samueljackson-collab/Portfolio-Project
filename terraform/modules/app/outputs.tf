output "assets_bucket_name" {
  description = "Name of the S3 bucket for application assets"
  value       = aws_s3_bucket.assets.bucket
}

output "assets_bucket_arn" {
  description = "ARN of the S3 bucket for application assets"
  value       = aws_s3_bucket.assets.arn
}

output "rds_endpoint" {
  description = "Endpoint of the RDS instance"
  value       = try(aws_db_instance.postgres[0].address, "")
}

output "rds_identifier" {
  description = "Identifier of the RDS instance"
  value       = try(aws_db_instance.postgres[0].id, "")
}

output "eks_cluster_name" {
  description = "Name of the EKS cluster when created"
  value       = try(aws_eks_cluster.this[0].name, "")
}
