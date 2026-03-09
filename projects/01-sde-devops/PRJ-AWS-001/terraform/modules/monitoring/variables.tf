variable "project_name" { type = string }
variable "environment" { type = string }
variable "common_tags" { type = map(string) default = {} }
variable "asg_name" { type = string }
variable "alb_metric_name" { type = string }
variable "aws_region" { type = string }
variable "alarm_sns_topic_arn" { type = string default = null }
variable "enable_dashboard" { type = bool default = true }
