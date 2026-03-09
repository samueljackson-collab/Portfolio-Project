terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  tags = merge({
    Project     = var.project_name,
    Environment = var.environment,
    ManagedBy   = "Terraform"
  }, var.extra_tags)

  simulators = {
    red_team   = { image = lookup(var.container_images, "red_team", "public.ecr.aws/docker/library/python:3.11"), port = 8000 }
    ransomware = { image = lookup(var.container_images, "ransomware", "public.ecr.aws/docker/library/python:3.11"), port = 8000 }
    soc        = { image = lookup(var.container_images, "soc", "public.ecr.aws/docker/library/node:20"), port = 8000 }
    hunting    = { image = lookup(var.container_images, "hunting", "public.ecr.aws/docker/library/python:3.11"), port = 8000 }
    malware    = { image = lookup(var.container_images, "malware", "public.ecr.aws/docker/library/python:3.11"), port = 8000 }
    edr        = { image = lookup(var.container_images, "edr", "public.ecr.aws/docker/library/python:3.11"), port = 8000 }
  }
}

# Networking shared across all simulators
module "network" {
  source       = "../terraform/modules/vpc"
  project_name = var.project_name
  environment  = var.environment

  vpc_cidr           = var.vpc_cidr
  az_count           = 2
  enable_nat_gateway = true
  single_nat_gateway = true
  enable_flow_logs   = true
  tags               = local.tags
}

# Broad ingress SG for simulation traffic within the VPC
resource "aws_security_group" "simulator_ingress" {
  name        = "${var.project_name}-${var.environment}-simulator"
  description = "Allow simulator services to reach shared data planes"
  vpc_id      = module.network.vpc_id

  ingress {
    description = "Allow Postgres within VPC"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}

# Shared database backing the simulators
module "shared_database" {
  source       = "../terraform/modules/database"
  project_name = "${var.project_name}-shared"
  environment  = var.environment
  vpc_id       = module.network.vpc_id
  subnet_ids   = module.network.database_subnet_ids

  db_username = var.db_username
  db_password = var.db_password

  allowed_security_group_ids = [aws_security_group.simulator_ingress.id]

  instance_class          = var.db_instance_class
  allocated_storage       = var.db_allocated_storage
  max_allocated_storage   = var.db_max_allocated_storage
  backup_retention_period = 7
  tags                    = local.tags
}

# ECS services for each simulator
module "simulator_apps" {
  source  = "../terraform/modules/ecs-application"
  for_each = local.simulators

  project_name = "${var.project_name}-${each.key}"
  environment  = var.environment

  vpc_id             = module.network.vpc_id
  public_subnet_ids  = module.network.public_subnet_ids
  private_subnet_ids = module.network.private_subnet_ids

  container_image       = each.value.image
  container_port        = each.value.port
  enable_autoscaling    = true
  enable_execute_command = true

  environment_variables = [
    { name = "DATABASE_HOST", value = module.shared_database.db_endpoint },
    { name = "ENVIRONMENT", value = var.environment }
  ]

  tags = local.tags
}

# Observability: optional CloudWatch alarm for red-team detections
resource "aws_cloudwatch_metric_alarm" "red_team_detection" {
  count               = var.enable_red_team_alarm ? 1 : 0
  alarm_name          = "${var.project_name}-${var.environment}-red-team-detections"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "RedTeamDetections"
  namespace           = "SecuritySimulators"
  period              = 300
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "Alert when red team detections are reported"
}

# Backup vault for ransomware drills
resource "aws_backup_vault" "ransomware" {
  count = var.enable_backup_vault ? 1 : 0
  name  = "${var.project_name}-${var.environment}-backup"
  tags  = local.tags
}

# Storage for SOC frontends and malware sample evidence
resource "aws_s3_bucket" "soc_frontend" {
  bucket = "${var.project_name}-${var.environment}-soc-ui"
  tags   = local.tags
}

resource "aws_s3_bucket" "malware_samples" {
  bucket = "${var.project_name}-${var.environment}-malware-samples"
  tags   = local.tags
}

# Optional analytics hooks for threat hunting
resource "aws_athena_workgroup" "hunts" {
  count = var.enable_hunting_athena ? 1 : 0
  name  = "${var.project_name}-${var.environment}-hunts"
}

resource "aws_opensearch_domain" "soc" {
  count          = var.enable_opensearch ? 1 : 0
  domain_name    = "${var.project_name}-${var.environment}-soc"
  engine_version = "OpenSearch_2.11"
  cluster_config {
    instance_type  = "t3.small.search"
    instance_count = 1
  }
  ebs_options {
    ebs_enabled = true
    volume_size = 10
  }
  tags = local.tags
}

resource "aws_sns_topic" "hunt_notifications" {
  count = var.enable_hunt_notifications ? 1 : 0
  name  = "${var.project_name}-${var.environment}-hunt-notify"
  tags  = local.tags
}

output "application_urls" {
  description = "ALB URLs for each simulator"
  value       = { for k, mod in module.simulator_apps : k => mod.application_url }
}

output "database_endpoint" {
  value       = module.shared_database.db_endpoint
  description = "Shared Postgres endpoint for the simulators"
}

output "storage" {
  value = {
    soc_frontend_bucket    = aws_s3_bucket.soc_frontend.bucket
    malware_samples_bucket = aws_s3_bucket.malware_samples.bucket
  }
}
