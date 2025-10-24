# Sample values for the production environment. Provide real secrets via a private tfvars file or TF_VAR overrides before applying.
environment = "prod"
public_subnets = {
  az1 = {
    cidr  = "10.40.0.0/24"
    az    = "us-west-2a"
    order = "0"
  }
  az2 = {
    cidr  = "10.40.2.0/24"
    az    = "us-west-2b"
    order = "1"
  }
  az3 = {
    cidr  = "10.40.4.0/24"
    az    = "us-west-2c"
    order = "2"
  }
}
private_subnets = {
  az1 = {
    cidr = "10.40.1.0/24"
    az   = "us-west-2a"
  }
  az2 = {
    cidr = "10.40.3.0/24"
    az   = "us-west-2b"
  }
  az3 = {
    cidr = "10.40.5.0/24"
    az   = "us-west-2c"
  }
}
db_master_username = "portfolio_app"
db_master_password = "ChangeMe123!"
kms_key_id          = "arn:aws:kms:us-west-2:123456789012:key/example"
