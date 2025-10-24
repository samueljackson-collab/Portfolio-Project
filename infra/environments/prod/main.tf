module "portfolio" {
  source = "../../"

  environment     = "prod"
  region          = "us-east-1"
  vpc_cidr        = "10.3.0.0/16"
  public_subnets  = ["10.3.1.0/24", "10.3.2.0/24"]
  private_subnets = ["10.3.11.0/24", "10.3.12.0/24"]
  data_subnets    = ["10.3.21.0/24", "10.3.22.0/24"]
  instance_type   = "t3.medium"
  min_size        = 2
  max_size        = 3
  db_instance_class = "db.t3.medium"
  db_password     = "change-me"
}
