# AWS CloudFront Module

Creates a CloudFront distribution with origin configuration, TLS settings, cache behaviors, WAF integration, and access logging.

## Usage

```hcl
module "cdn" {
  source = "../modules/aws/cloudfront"

  project_name          = "portfolio"
  environment           = "prod"
  origin_domain_name    = module.alb.dns_name
  origin_id             = "alb-origin"
  viewer_certificate_arn = aws_acm_certificate.cdn.arn
  logging_bucket        = "portfolio-logs.s3.amazonaws.com"
  aliases               = ["cdn.example.com"]
}
```

## Outputs
- `distribution_id`
- `distribution_arn`
- `domain_name`
