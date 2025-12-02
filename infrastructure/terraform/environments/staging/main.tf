locals {
  base_tags = merge(var.tags, {
    Project     = var.project_name
    Environment = var.environment
    Service     = "orchestration-api"
  })
}

module "network" {
  source               = "../../modules/vpc"
  project_name         = var.project_name
  environment          = var.environment
  vpc_cidr             = var.vpc_cidr
  az_count             = var.az_count
  enable_nat_gateway   = true
  single_nat_gateway   = false
  enable_flow_logs     = true
  flow_logs_retention_days = 14
  enable_s3_endpoint   = true
  tags                 = local.base_tags
}

module "database" {
  source                    = "../../modules/database"
  project_name              = var.project_name
  environment               = var.environment
  vpc_id                    = module.network.vpc_id
  subnet_ids                = module.network.database_subnet_ids
  db_username               = var.db_username
  db_password               = var.db_password
  instance_class            = "db.t3.small"
  allocated_storage         = 20
  max_allocated_storage     = 100
  multi_az                  = true
  backup_retention_period   = 7
  deletion_protection       = true
  apply_immediately         = false
  skip_final_snapshot       = false
  allowed_security_group_ids = []
  tags                      = local.base_tags
}

module "app" {
  source                       = "../../modules/ecs-application"
  project_name                 = var.project_name
  environment                  = var.environment
  vpc_id                       = module.network.vpc_id
  public_subnet_ids            = module.network.public_subnet_ids
  private_subnet_ids           = module.network.private_subnet_ids
  container_image              = var.container_image
  container_port               = 8000
  desired_count                = var.desired_count
  min_capacity                 = var.min_capacity
  max_capacity                 = var.max_capacity
  enable_execute_command       = true
  health_check_path            = "/health"
  health_check_matcher         = "200-399"
  environment_variables = [
    {
      name  = "DB_ENDPOINT"
      value = module.database.db_endpoint
    },
    {
      name  = "DB_USERNAME"
      value = var.db_username
    },
    {
      name  = "DB_NAME"
      value = "portfolio"
    }
  ]
  database_security_group_id = module.database.db_security_group_id
  enable_container_insights  = true
  enable_autoscaling         = true
  cpu_target_value           = 65
  memory_target_value        = 75
  tags                       = local.base_tags
}

resource "aws_security_group_rule" "db_from_app" {
  type                     = "ingress"
  description              = "Allow ECS tasks to talk to the database"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = module.database.db_security_group_id
  source_security_group_id = module.app.ecs_tasks_security_group_id
}
