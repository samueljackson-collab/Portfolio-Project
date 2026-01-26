###############################################################################
# Storage Module - Outputs
###############################################################################

#------------------------------------------------------------------------------
# S3 Bucket Outputs
#------------------------------------------------------------------------------

output "bucket_id" {
  description = "The name of the S3 bucket."
  value       = aws_s3_bucket.static.id
}

output "bucket_arn" {
  description = "The ARN of the S3 bucket."
  value       = aws_s3_bucket.static.arn
}

output "bucket_domain_name" {
  description = "The bucket domain name."
  value       = aws_s3_bucket.static.bucket_domain_name
}

output "bucket_regional_domain_name" {
  description = "The bucket regional domain name."
  value       = aws_s3_bucket.static.bucket_regional_domain_name
}

output "bucket_website_endpoint" {
  description = "The website endpoint of the bucket (if configured)."
  value       = try(aws_s3_bucket.static.website_endpoint, null)
}

#------------------------------------------------------------------------------
# CloudFront Distribution Outputs
#------------------------------------------------------------------------------

output "cloudfront_distribution_id" {
  description = "The ID of the CloudFront distribution."
  value       = var.create_cloudfront_distribution ? aws_cloudfront_distribution.static[0].id : null
}

output "cloudfront_distribution_arn" {
  description = "The ARN of the CloudFront distribution."
  value       = var.create_cloudfront_distribution ? aws_cloudfront_distribution.static[0].arn : null
}

output "cloudfront_domain_name" {
  description = "The domain name of the CloudFront distribution."
  value       = var.create_cloudfront_distribution ? aws_cloudfront_distribution.static[0].domain_name : null
}

output "cloudfront_hosted_zone_id" {
  description = "The hosted zone ID of the CloudFront distribution."
  value       = var.create_cloudfront_distribution ? aws_cloudfront_distribution.static[0].hosted_zone_id : null
}

output "cloudfront_status" {
  description = "The status of the CloudFront distribution."
  value       = var.create_cloudfront_distribution ? aws_cloudfront_distribution.static[0].status : null
}

output "cloudfront_etag" {
  description = "The ETag of the CloudFront distribution."
  value       = var.create_cloudfront_distribution ? aws_cloudfront_distribution.static[0].etag : null
}

#------------------------------------------------------------------------------
# Origin Access Identity Outputs
#------------------------------------------------------------------------------

output "oai_id" {
  description = "The ID of the CloudFront Origin Access Identity."
  value       = var.create_cloudfront_distribution ? aws_cloudfront_origin_access_identity.static[0].id : null
}

output "oai_iam_arn" {
  description = "The IAM ARN of the CloudFront Origin Access Identity."
  value       = var.create_cloudfront_distribution ? aws_cloudfront_origin_access_identity.static[0].iam_arn : null
}

output "oai_cloudfront_access_identity_path" {
  description = "The CloudFront access identity path."
  value       = var.create_cloudfront_distribution ? aws_cloudfront_origin_access_identity.static[0].cloudfront_access_identity_path : null
}

#------------------------------------------------------------------------------
# Logs Bucket Outputs
#------------------------------------------------------------------------------

output "logs_bucket_id" {
  description = "The name of the logs S3 bucket."
  value       = var.create_logs_bucket ? aws_s3_bucket.logs[0].id : null
}

output "logs_bucket_arn" {
  description = "The ARN of the logs S3 bucket."
  value       = var.create_logs_bucket ? aws_s3_bucket.logs[0].arn : null
}

#------------------------------------------------------------------------------
# URL Outputs
#------------------------------------------------------------------------------

output "static_website_url" {
  description = "The URL to access static content (CloudFront HTTPS URL or S3 bucket reference when CloudFront is disabled)."
  value       = var.create_cloudfront_distribution ? "https://${aws_cloudfront_distribution.static[0].domain_name}" : "https://${aws_s3_bucket.static.bucket_regional_domain_name}"
}
