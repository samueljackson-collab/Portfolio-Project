output "vpc_id" {
  value       = aws_vpc.portfolio.id
  description = "ID of the portfolio VPC"
}

output "eks_cluster_name" {
  value       = aws_eks_cluster.portfolio.name
  description = "Name of the EKS cluster"
}

output "rds_endpoint" {
  value       = aws_rds_cluster.portfolio.endpoint
  description = "Writer endpoint for Aurora"
  sensitive   = true
}

output "evidence_bucket" {
  value       = aws_s3_bucket.evidence.bucket
  description = "S3 bucket storing portfolio evidence"
}
