resource "random_password" "rds" {  
  length  = 16  
  special = true  
}

resource "aws_db_subnet_group" "this" {  
  name       = "${var.name}-subnet-group"  
  subnet_ids = var.subnet_ids  
  tags       = var.tags  
}

resource "aws_db_instance" "this" {  
  identifier              = "${var.name}-${terraform.workspace}"  
  allocated_storage       = var.allocated_storage  
  engine                  = var.engine  
  engine_version          = var.engine_version  
  instance_class          = var.instance_class  
  name                    = var.db_name  
  username                = var.username  
  password                = var.password != "" ? var.password : random_password.rds.result  
  db_subnet_group_name    = aws_db_subnet_group.this.name  
  vpc_security_group_ids  = var.security_group_ids  
  skip_final_snapshot     = true  
  tags                    = merge(var.tags, { "CreatedBy" = "infra/modules/rds" })  
}
