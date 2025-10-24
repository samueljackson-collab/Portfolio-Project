# Root Terraform configuration
# This orchestrates all modules

# Network Module
module "network" {
  source = "./modules/network"
  
  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
}

# Note: Additional modules (compute, storage, monitoring) would be added here
# For brevity, I'm showing the pattern with the network module
# The complete implementation would include all modules

# Example of how to reference module outputs:
# resource "aws_instance" "example" {
#   subnet_id              = module.network.private_subnet_ids[0]
#   vpc_security_group_ids = [module.network.app_security_group_id]
# }
