/**
 * Data sources hydrate contextual information used for validations and outputs.
 */
data "aws_vpc" "selected" {
  id = var.vpc_id
}

data "aws_subnet" "selected" {
  for_each = toset(var.subnet_ids)
  id       = each.value
}

locals {
  availability_zones = tolist(distinct([for s in data.aws_subnet.selected : s.availability_zone]))
}
