variable "cidr_block" {
  description = "CIDR block allocated to the network"
  type        = string
}

variable "name" {
  description = "Name of the network segment"
  type        = string
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
  default     = {}
}
