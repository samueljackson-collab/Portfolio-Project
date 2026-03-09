terraform {
  required_version = ">= 1.0"
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

module "portfolio" {
  source = "../.."

  project_tag          = "twisted-monk"
  environment          = "demo"
  aws_region           = var.aws_region
  vpc_cidr             = "10.1.0.0/16"
  public_subnet_cidrs  = ["10.1.1.0/24", "10.1.2.0/24"]
  private_subnet_cidrs = ["10.1.101.0/24", "10.1.102.0/24"]

  create_rds           = true
  db_name              = "demo_app"
  db_username          = "demo_admin"
  db_password          = "super-secret-password"
  db_instance_class    = "db.t3.micro"
  db_allocated_storage = 20

  enable_rds_alarms        = true
  alarm_email              = "alerts@example.com"
  enable_nat_gateway       = true
  enable_flow_logs         = true
  vpc_flow_log_traffic_type = "ALL"
}

variable "aws_region" {
  description = "Region for the example deployment"
  type        = string
  default     = "us-east-1"
}
