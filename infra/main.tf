module "network" {
  source          = "./modules/network"
  project         = var.project
  environment     = var.environment
  vpc_cidr        = var.vpc_cidr
  public_subnets  = var.public_subnets
  private_subnets = var.private_subnets
  data_subnets    = var.data_subnets
}

module "compute" {
  source          = "./modules/compute"
  project         = var.project
  environment     = var.environment
  subnet_ids      = module.network.private_subnet_ids
  instance_type   = var.instance_type
  min_size        = var.min_size
  max_size        = var.max_size
  vpc_id          = module.network.vpc_id
  security_group_ids = [module.network.app_security_group_id]
}

module "storage" {
  source              = "./modules/storage"
  project             = var.project
  environment         = var.environment
  data_subnet_ids     = module.network.data_subnet_ids
  db_instance_class   = var.db_instance_class
  db_name             = var.db_name
  db_username         = var.db_username
  db_password         = var.db_password
  vpc_security_groups = [module.network.db_security_group_id]
}
