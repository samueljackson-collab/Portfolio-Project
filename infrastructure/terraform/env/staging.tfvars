environment = "staging"
public_subnets = {
  az1 = {
    cidr  = "10.30.0.0/24"
    az    = "us-west-2a"
    order = "0"
  }
  az2 = {
    cidr  = "10.30.2.0/24"
    az    = "us-west-2b"
    order = "1"
  }
}
private_subnets = {
  az1 = {
    cidr = "10.30.1.0/24"
    az   = "us-west-2a"
  }
  az2 = {
    cidr = "10.30.3.0/24"
    az   = "us-west-2b"
  }
}
db_master_username = "portfolio_app"
db_master_password = "ChangeMe123!"
kms_key_id          = "arn:aws:kms:us-west-2:123456789012:key/example"
