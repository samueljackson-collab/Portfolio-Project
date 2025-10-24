output "db_endpoint" {
  value = aws_db_instance.this.endpoint
}

output "frontend_bucket" {
  value = aws_s3_bucket.frontend.bucket
}
