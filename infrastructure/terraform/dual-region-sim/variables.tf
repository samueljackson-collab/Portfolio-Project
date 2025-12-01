variable "project_name" {
  description = "Project name used for tagging"
  type        = string
  default     = "roaming-sim"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "simulation"
}

variable "primary_region" {
  description = "Primary AWS region"
  type        = string
  default     = "us-east-1"
}

variable "secondary_region" {
  description = "Secondary AWS region"
  type        = string
  default     = "us-west-2"
}

variable "container_image" {
  description = "Container image for the FastAPI roaming service"
  type        = string
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
  default     = {}
}
