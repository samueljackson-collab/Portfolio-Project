module "network" {
  source = "../../modules/vpc"

  name       = var.name
  cidr_block = "10.20.0.0/16"
  public_subnets = {
    a = {
      cidr = "10.20.1.0/24"
      az   = "${var.aws_region}a"
    }
    b = {
      cidr = "10.20.2.0/24"
      az   = "${var.aws_region}b"
    }
  }
  private_subnets = {
    a = {
      cidr = "10.20.101.0/24"
      az   = "${var.aws_region}a"
    }
    b = {
      cidr = "10.20.102.0/24"
      az   = "${var.aws_region}b"
    }
  }
  tags = {
    Environment = "prod"
    Application = "portfolio"
  }
}
