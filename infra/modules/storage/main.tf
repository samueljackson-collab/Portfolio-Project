resource "aws_db_subnet_group" "this" {
  name       = "${var.project}-${var.environment}-db"
  subnet_ids = var.data_subnet_ids

  tags = merge(var.common_tags, {
    Name = "${var.project}-${var.environment}-db-subnet"
  })
}

resource "aws_db_instance" "this" {
  identifier              = "${var.project}-${var.environment}-db"
  engine                  = "postgres"
  engine_version          = "14"
  instance_class          = var.db_instance_class
  allocated_storage       = 20
  db_name                 = var.db_name
  username                = var.db_username
  password                = var.db_password
  db_subnet_group_name    = aws_db_subnet_group.this.name
  vpc_security_group_ids  = var.vpc_security_groups
  skip_final_snapshot     = true
  publicly_accessible     = false
  deletion_protection     = false

  tags = merge(var.common_tags, {
    Name = "${var.project}-${var.environment}-db"
  })
}

resource "aws_s3_bucket" "static" {
  bucket = "${var.project}-${var.environment}-static-${random_string.suffix.id}"

  tags = merge(var.common_tags, {
    Name = "${var.project}-${var.environment}-static"
  })
}

resource "aws_s3_bucket_public_access_block" "static" {
  bucket = aws_s3_bucket.static.id

  block_public_acls   = false
  block_public_policy = false
  ignore_public_acls  = false
  restrict_public_buckets = false
}

resource "aws_cloudfront_distribution" "static" {
  enabled             = true
  default_root_object = "index.html"

  origin {
    domain_name = aws_s3_bucket.static.bucket_regional_domain_name
    origin_id   = "s3-static"
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "s3-static"

    viewer_protocol_policy = "redirect-to-https"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = merge(var.common_tags, {
    Name = "${var.project}-${var.environment}-cdn"
  })
}

resource "random_string" "suffix" {
  length  = 6
  special = false
}
