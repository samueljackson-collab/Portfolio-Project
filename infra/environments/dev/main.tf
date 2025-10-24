module "portfolio" {
  source = "../../"

  environment     = "dev"
  region          = "us-east-1"
  vpc_cidr        = "10.1.0.0/16"
  public_subnets  = ["10.1.1.0/24", "10.1.2.0/24"]
  private_subnets = ["10.1.11.0/24", "10.1.12.0/24"]
  data_subnets    = ["10.1.21.0/24", "10.1.22.0/24"]
  instance_type   = "t3.small"
  min_size        = 1
  max_size        = 2
  db_password     = "change-me"
}
