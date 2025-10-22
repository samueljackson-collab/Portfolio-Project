environment = "dev"
public_subnets = {
  az1 = {
    cidr  = "10.20.0.0/24"
    az    = "us-west-2a"
    order = "0"
  }
}
private_subnets = {
  az1 = {
    cidr = "10.20.1.0/24"
    az   = "us-west-2a"
  }
}
db_master_username = "portfolio_app"
db_master_password = "ChangeMe123!"
kms_key_id          = "arn:aws:kms:us-west-2:123456789012:key/example"
