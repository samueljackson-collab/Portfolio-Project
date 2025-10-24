output "db_endpoint" {
  value = aws_db_instance.this.address
}

output "static_bucket" {
  value = aws_s3_bucket.static.bucket
}

output "cloudfront_domain" {
  value = aws_cloudfront_distribution.static.domain_name
}
