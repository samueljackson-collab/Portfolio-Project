variable "project_name" { type = string  default = "portfolio" }
variable "environment"  { type = string  default = "dev" }
variable "vpc_cidr"     { type = string  default = "10.10.0.0/16" }
variable "availability_zones" { type = list(string) default = ["us-west-2a","us-west-2b"] }
variable "enable_nat_gateway" { type = bool default = true }
variable "enable_vpn_gateway" { type = bool default = false }
