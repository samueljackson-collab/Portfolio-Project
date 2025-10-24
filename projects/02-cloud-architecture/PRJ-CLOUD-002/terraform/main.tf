locals {
  common_tags = merge({
    Project     = var.project_name,
    Environment = var.environment,
    Owner       = var.owner
  }, var.extra_tags)
}

module "network" {
  source                   = "./modules/vpc"
  project_name             = var.project_name
  environment              = var.environment
  cidr_block               = var.cidr_block
  availability_zones       = var.availability_zones
  public_subnet_cidrs      = var.public_subnet_cidrs
  private_app_subnet_cidrs = var.private_app_subnet_cidrs
  database_subnet_cidrs    = var.database_subnet_cidrs
  tags                     = local.common_tags
}

module "security" {
  source            = "./modules/security-groups"
  vpc_id            = module.network.vpc_id
  alb_allowed_cidrs = var.alb_allowed_cidrs
  app_port          = var.app_port
  tags              = local.common_tags
}

module "alb" {
  source                     = "./modules/alb"
  name_prefix                = "${var.project_name}-${var.environment}"
  vpc_id                     = module.network.vpc_id
  security_group_id          = module.security.alb_security_group_id
  public_subnet_ids          = module.network.public_subnet_ids
  certificate_arn            = var.certificate_arn
  target_group_port          = var.app_port
  health_check_path          = var.app_health_check_path
  enable_deletion_protection = var.enable_deletion_protection
  tags                       = local.common_tags
}

module "compute" {
  source              = "./modules/autoscaling"
  project_name        = var.project_name
  environment         = var.environment
  subnet_ids          = module.network.private_app_subnet_ids
  security_group_id   = module.security.app_security_group_id
  instance_type       = var.instance_type
  key_name            = var.key_name
  target_group_arns   = [module.alb.target_group_arn]
  min_size            = var.asg_min_size
  desired_capacity    = var.asg_desired_capacity
  max_size            = var.asg_max_size
  app_port            = var.app_port
  tags                = local.common_tags
}

module "database" {
  source                       = "./modules/rds"
  project_name                 = var.project_name
  environment                  = var.environment
  subnet_ids                   = module.network.database_subnet_ids
  security_group_id            = module.security.database_security_group_id
  instance_class               = var.db_instance_class
  allocated_storage            = var.db_allocated_storage
  max_allocated_storage        = var.db_max_allocated_storage
  db_name                      = var.db_name
  db_username                  = var.db_username
  db_password                  = var.db_password
  multi_az                     = var.db_multi_az
  backup_retention_days        = var.db_backup_retention_days
  enable_performance_insights  = var.enable_performance_insights
  deletion_protection          = var.enable_deletion_protection
  tags                         = local.common_tags
}

module "monitoring" {
  source                    = "./modules/monitoring"
  project_name              = var.project_name
  environment               = var.environment
  alb_arn_suffix            = module.alb.alb_arn_suffix
  target_group_arn_suffix   = module.alb.target_group_arn_suffix
  autoscaling_group_name    = module.compute.autoscaling_group_name
  db_instance_id            = module.database.db_instance_id
  vpc_id                    = module.network.vpc_id
  alert_email               = var.alert_email
  log_retention_days        = var.log_retention_days
  tags                      = local.common_tags
}

module "backup" {
  source           = "./modules/backup"
  project_name     = var.project_name
  environment      = var.environment
  rds_instance_arn = module.database.db_instance_arn
  tags             = local.common_tags
}
