terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  base_tags = merge(
    var.tags,
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  )
}

resource "aws_security_group" "instance" {
  name        = "${local.name_prefix}-ec2-sg"
  description = "Security group for application instances"
  vpc_id      = var.vpc_id

  ingress {
    description = "Allow inbound application traffic"
    from_port   = var.instance_port
    to_port     = var.instance_port
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.base_tags, { Name = "${local.name_prefix}-ec2-sg" })
}

resource "aws_instance" "app" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [aws_security_group.instance.id]
  key_name               = var.key_name
  user_data              = var.user_data

  tags = merge(local.base_tags, { Name = "${local.name_prefix}-ec2" })
}

output "instance_id" {
  description = "ID of the deployed EC2 instance"
  value       = aws_instance.app.id
}

output "public_ip" {
  description = "Public IP address of the instance when available"
  value       = aws_instance.app.public_ip
}

variable "project_name" {
  description = "Name of the project owning the instance"
  type        = string
}

variable "environment" {
  description = "Deployment environment label"
  type        = string
}

variable "vpc_id" {
  description = "VPC where the instance and security group will live"
  type        = string
}

variable "subnet_id" {
  description = "Target subnet for the EC2 instance"
  type        = string
}

variable "ami_id" {
  description = "AMI ID to launch"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance size"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "SSH key pair name for access"
  type        = string
  default     = null
}

variable "user_data" {
  description = "Optional user data script to bootstrap the instance"
  type        = string
  default     = null
}

variable "instance_port" {
  description = "Port the instance should allow from clients"
  type        = number
  default     = 80
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to reach the instance"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}
