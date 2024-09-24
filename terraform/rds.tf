resource "aws_security_group" "rds_sg" {
  name        = "rds-public-sg"
  description = "Security group for public RDS instance"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "RDSPublicSG"
  }
}

resource "aws_db_subnet_group" "public" {
  name       = "public-subnet-group"
  subnet_ids = module.vpc.public_subnets

  tags = {
    Name = "PublicDBSubnetGroup"
  }
}

resource "aws_db_instance" "mysql_instance" {
  allocated_storage      = 20
  instance_class         = "db.t3.small"
  engine                 = "mysql"
  engine_version         = "8.0.39"
  username               = var.db_username
  password               = var.db_password
  db_name                = var.db_name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.public.name

  publicly_accessible     = true
  multi_az                = false
  storage_type            = "gp2"
  backup_retention_period = 7

  tags = {
    Name = "MySQLRDSInstance"
  }
}