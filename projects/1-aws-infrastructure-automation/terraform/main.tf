terraform {
  required_version = ">= 1.4"

  backend "s3" {}

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "portfolio-vpc-${var.environment}"
  cidr = var.vpc_cidr

  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs

  enable_nat_gateway   = true
  single_nat_gateway   = var.environment == "production" ? false : true
  enable_dns_hostnames = true
  enable_dns_support   = true

  create_database_subnet_group = true
  database_subnets             = var.database_subnet_cidrs

  tags = {
    Environment = var.environment
    Project     = "portfolio"
    ManagedBy   = "terraform"
    AutoRecover = "true"
  }
}

module "eks" {
  source = "terraform-aws-modules/eks/aws"

  cluster_name    = "portfolio-${var.environment}"
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    primary = {
      min_size     = 2
      max_size     = 10
      desired_size = 3

      instance_types = ["t3.medium"]
      capacity_type  = "SPOT"

      health_check_type = "ELB"
      enable_monitoring = true

      mixed_instances_policy = {
        instances_distribution = {
          on_demand_base_capacity                  = 1
          on_demand_percentage_above_base_capacity = 50
          spot_allocation_strategy                 = "capacity-optimized"
        }
        override = [
          {
            instance_type = "t3.medium"
          },
          {
            instance_type = "t3.large"
          },
          {
            instance_type = "t2.medium"
          }
        ]
      }

      tags = {
        "k8s.io/cluster-autoscaler/enabled" = "true"
        "k8s.io/cluster-autoscaler/portfolio" = "owned"
      }
    }
  }

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
  }
}

module "rds" {
  source = "terraform-aws-modules/rds/aws"

  identifier = "portfolio-${var.environment}"

  engine               = "postgres"
  engine_version       = "15.4"
  family               = "postgres15"
  major_engine_version = "15"
  instance_class       = "db.t3.medium"

  allocated_storage     = 20
  max_allocated_storage = 100

  db_name  = "portfolio"
  username = var.db_username
  password = var.db_password
  port     = 5432

  db_subnet_group_name   = module.vpc.database_subnet_group_name
  vpc_security_group_ids = [module.vpc.default_security_group_id]

  backup_window      = "03:00-04:00"
  maintenance_window = "Mon:04:00-Mon:05:00"

  backup_retention_period = 7
  skip_final_snapshot     = var.environment != "production"
  deletion_protection     = var.environment == "production"

  performance_insights_enabled = true

  tags = {
    Environment = var.environment
    Project     = "portfolio"
    ManagedBy   = "terraform"
  }
}
