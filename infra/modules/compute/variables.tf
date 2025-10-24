variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "instance_type" {
  type = string
}

variable "min_size" {
  type = number
}

variable "max_size" {
  type = number
}

variable "vpc_id" {
  type = string
}

variable "security_group_ids" {
  type = list(string)
}

variable "common_tags" {
  type    = map(string)
  default = {}
}
