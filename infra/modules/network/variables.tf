variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_cidr" {
  type = string
}

variable "public_subnets" {
  type = list(string)
}

variable "private_subnets" {
  type = list(string)
}

variable "data_subnets" {
  type = list(string)
}

variable "common_tags" {
  type = map(string)
  default = {}
}
