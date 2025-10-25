variable "primary_region" { type = string }
variable "secondary_region" { type = string }
variable "primary_vpc_cidr" { type = string }
variable "secondary_vpc_cidr" { type = string }
variable "primary_azs" { type = list(string) }
variable "secondary_azs" { type = list(string) }
variable "primary_private_subnets" { type = list(string) }
variable "primary_public_subnets" { type = list(string) }
variable "secondary_private_subnets" { type = list(string) }
variable "secondary_public_subnets" { type = list(string) }
variable "db_username" { type = string sensitive = true }
variable "db_password" { type = string sensitive = true }
variable "replication_bucket_name" { type = string }
variable "replication_destination_bucket" { type = string }
variable "replication_role_arn" { type = string }
variable "health_check_fqdn" { type = string }
variable "hosted_zone_id" { type = string }
variable "application_domain" { type = string }
variable "primary_alb_dns" { type = string }
variable "primary_alb_zone_id" { type = string }
variable "secondary_alb_dns" { type = string }
variable "secondary_alb_zone_id" { type = string }
