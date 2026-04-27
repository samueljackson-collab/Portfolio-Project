terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Database module placeholder: define RDS subnet groups, parameter groups, instances,
# and read replicas. Wire Secrets Manager integration for credentials when implementing.
