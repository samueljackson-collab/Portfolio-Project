/**
 * Main orchestration file that wires environment variables into the reusable database module.
 */
module "database" {
  source = "../../modules/database"

  project_name  = var.project_name
  environment   = var.environment
  vpc_id        = var.vpc_id
  subnet_ids    = var.subnet_ids
  db_username   = var.db_username
  db_password   = var.db_password

  allowed_security_group_ids = var.allowed_security_group_ids
  instance_class             = var.instance_class
  allocated_storage          = var.allocated_storage
  max_allocated_storage      = var.max_allocated_storage
  engine_version             = var.engine_version
  multi_az                   = var.multi_az
  backup_retention_period    = var.backup_retention_period
  deletion_protection        = var.deletion_protection
  skip_final_snapshot        = var.skip_final_snapshot
  apply_immediately          = var.apply_immediately
  performance_insights_enabled          = var.performance_insights_enabled
  performance_insights_retention_period = var.performance_insights_retention_period
  tags = var.tags
}
