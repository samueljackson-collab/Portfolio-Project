variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "data_subnet_ids" {
  type = list(string)
}

variable "db_instance_class" {
  type = string
}

variable "db_name" {
  type = string
}

variable "db_username" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "vpc_security_groups" {
  type = list(string)
}

variable "common_tags" {
  type    = map(string)
  default = {}
}
