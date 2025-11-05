output "assets_bucket" {
  description = "S3 bucket used for app assets"
  value       = aws_s3_bucket.app_assets.bucket
}
