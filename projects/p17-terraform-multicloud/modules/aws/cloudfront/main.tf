locals {
  tags = merge(var.tags, { Project = var.project_name, Environment = var.environment })
}

resource "aws_cloudfront_distribution" "this" {
  enabled             = var.enabled
  comment             = "${var.project_name}-cdn"
  default_root_object = var.default_root_object
  price_class         = var.price_class
  aliases             = var.aliases
  web_acl_id          = var.web_acl_id

  origin {
    domain_name = var.origin_domain_name
    origin_id   = var.origin_id

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = var.origin_protocol_policy
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = var.origin_id
    viewer_protocol_policy = var.viewer_protocol_policy
    compress               = var.compress

    forwarded_values {
      query_string = var.forward_query_string
      headers      = var.forward_headers

      cookies {
        forward = var.forward_cookies
      }
    }

    min_ttl     = var.min_ttl
    default_ttl = var.default_ttl
    max_ttl     = var.max_ttl
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = var.viewer_certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = var.minimum_protocol_version
  }

  logging_config {
    bucket = var.logging_bucket
    prefix = var.logging_prefix
    include_cookies = false
  }

  tags = local.tags
}
