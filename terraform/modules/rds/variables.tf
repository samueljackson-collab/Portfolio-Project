variable "name" { type = string }
variable "subnet_ids" { type = list(string) }
variable "security_group_ids" { type = list(string) }
variable "allocated_storage" { type = number, default = 20 }
variable "engine" { type = string, default = "postgres" }
variable "engine_version" { type = string, default = "15.3" }
variable "instance_class" { type = string, default = "db.t3.micro" }
variable "db_name" { type = string, default = "appdb" }
variable "username" { type = string, default = "appuser" }
variable "password" { type = string, default = "" }
variable "tags" { type = map(string), default = {} }
