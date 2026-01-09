# Storage Module

## Overview

This module creates S3 buckets for static content hosting with CloudFront distribution for global content delivery, Origin Access Identity for secure S3 access, encryption at rest, versioning, and lifecycle policies.

## Architecture

```
                                Users
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │      CloudFront         │
                    │      Distribution       │
                    │  ┌───────────────────┐  │
                    │  │ Edge Locations    │  │
                    │  │ (Global Cache)    │  │
                    │  └───────────────────┘  │
                    └─────────────┬───────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
     ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
     │ /static/*      │  │ /api/*         │  │ Default (/)    │
     │ (S3 Origin)    │  │ (ALB Origin)   │  │ (S3 Origin)    │
     └────────┬───────┘  └────────┬───────┘  └────────────────┘
              │                   │
              ▼                   ▼
     ┌────────────────┐  ┌────────────────┐
     │ S3 Bucket      │  │ Application    │
     │ (Private)      │  │ Load Balancer  │
     │ ┌────────────┐ │  └────────────────┘
     │ │ OAI Access │ │
     │ └────────────┘ │
     │ ┌────────────┐ │
     │ │ Versioning │ │
     │ └────────────┘ │
     │ ┌────────────┐ │
     │ │ Encryption │ │
     │ └────────────┘ │
     └────────────────┘
```

## Features

- **CloudFront CDN**: Global content delivery with edge caching
- **Origin Access Identity**: Secure S3 access without public bucket
- **Versioning**: Object version history for rollback
- **Server-Side Encryption**: AES-256 or KMS encryption
- **Lifecycle Policies**: Automatic transition to IA and Glacier
- **CORS Support**: Cross-origin resource sharing configuration
- **Custom Error Pages**: SPA-friendly error responses
- **Multi-Origin**: Route API traffic through ALB origin

## Input Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| `name_prefix` | Prefix for resource names | `string` | - | Yes |
| `bucket_name` | Custom bucket name (auto-generated if empty) | `string` | `""` | No |
| `force_destroy` | Allow bucket deletion with objects | `bool` | `false` | No |
| `enable_versioning` | Enable S3 versioning | `bool` | `true` | No |
| `kms_key_arn` | KMS key for encryption | `string` | `""` | No |
| `cors_allowed_origins` | CORS allowed origins | `list(string)` | `[]` | No |
| `enable_lifecycle_rules` | Enable lifecycle rules | `bool` | `true` | No |
| `create_cloudfront_distribution` | Create CloudFront | `bool` | `true` | No |
| `cloudfront_price_class` | CloudFront price class | `string` | `"PriceClass_100"` | No |
| `cloudfront_aliases` | Domain aliases | `list(string)` | `[]` | No |
| `acm_certificate_arn` | ACM certificate ARN | `string` | `""` | No |
| `cache_default_ttl` | Default cache TTL | `number` | `86400` | No |
| `alb_domain_name` | ALB domain for API origin | `string` | `""` | No |
| `tags` | Tags to apply to resources | `map(string)` | `{}` | No |

## Outputs

| Name | Description |
|------|-------------|
| `bucket_id` | The name of the S3 bucket |
| `bucket_arn` | The ARN of the S3 bucket |
| `bucket_domain_name` | The bucket domain name |
| `bucket_regional_domain_name` | The bucket regional domain name |
| `cloudfront_distribution_id` | The CloudFront distribution ID |
| `cloudfront_distribution_arn` | The CloudFront distribution ARN |
| `cloudfront_domain_name` | The CloudFront domain name |
| `cloudfront_hosted_zone_id` | The CloudFront hosted zone ID |
| `oai_id` | The Origin Access Identity ID |
| `static_website_url` | The URL to access static content |

## Example Usage

### Basic Static Site

```hcl
module "storage" {
  source = "./modules/storage"

  name_prefix = "myapp-dev"

  tags = {
    Environment = "dev"
    Project     = "myapp"
  }
}

# Upload files
resource "aws_s3_object" "index" {
  bucket       = module.storage.bucket_id
  key          = "index.html"
  source       = "dist/index.html"
  content_type = "text/html"
}
```

### Production with Custom Domain

```hcl
module "storage" {
  source = "./modules/storage"

  name_prefix            = "myapp-prod"
  cloudfront_aliases     = ["static.example.com"]
  acm_certificate_arn    = "arn:aws:acm:us-east-1:123456789012:certificate/abc123"
  cloudfront_price_class = "PriceClass_200"

  cache_default_ttl = 604800  # 7 days

  enable_versioning     = true
  enable_lifecycle_rules = true

  tags = {
    Environment = "production"
  }
}

# Route53 Alias Record
resource "aws_route53_record" "static" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "static.example.com"
  type    = "A"

  alias {
    name                   = module.storage.cloudfront_domain_name
    zone_id                = module.storage.cloudfront_hosted_zone_id
    evaluate_target_health = false
  }
}
```

### SPA with API Routing

```hcl
module "storage" {
  source = "./modules/storage"

  name_prefix     = "myapp-prod"
  alb_domain_name = module.compute.alb_dns_name

  custom_error_responses = [
    {
      error_code            = 404
      response_code         = 200
      response_page_path    = "/index.html"
      error_caching_min_ttl = 0
    },
    {
      error_code            = 403
      response_code         = 200
      response_page_path    = "/index.html"
      error_caching_min_ttl = 0
    }
  ]

  tags = {
    Environment = "production"
  }
}
```

### With CORS for API Access

```hcl
module "storage" {
  source = "./modules/storage"

  name_prefix = "myapp-assets"

  cors_allowed_origins = ["https://example.com", "https://www.example.com"]
  cors_allowed_methods = ["GET", "HEAD"]
  cors_allowed_headers = ["*"]
  cors_max_age_seconds = 3600

  tags = {
    Environment = "production"
  }
}
```

## Lifecycle Rules

Default lifecycle configuration (when `enable_lifecycle_rules = true`):

| Transition | Days | Storage Class |
|------------|------|---------------|
| Current objects | 90 | STANDARD_IA |
| Non-current versions | 30 | STANDARD_IA |
| Non-current expiration | 90 | Deleted |
| Incomplete uploads | 7 | Aborted |

## CloudFront Price Classes

| Price Class | Regions Included |
|-------------|------------------|
| `PriceClass_100` | US, Canada, Europe |
| `PriceClass_200` | + Asia, Middle East, Africa |
| `PriceClass_All` | All edge locations |

## Important Notes

1. **ACM Certificates**: Must be in `us-east-1` region for CloudFront.

2. **Bucket Names**: S3 bucket names are globally unique. Use `bucket_name` to specify custom name or let module auto-generate.

3. **OAI Security**: S3 bucket is private. CloudFront uses Origin Access Identity for access.

4. **Cache Invalidation**: After deploying new content, create CloudFront invalidation:
   ```bash
   aws cloudfront create-invalidation --distribution-id <ID> --paths "/*"
   ```

5. **Versioning**: Enable for production to prevent accidental data loss.

## Security Considerations

- Block all public access to S3 bucket
- Use HTTPS-only viewer protocol policy
- Enable access logging for audit trails
- Consider WAF integration for DDoS protection

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.4 |
| aws | ~> 5.0 |
