terraform {
  required_version = ">= 1.3.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ----------------------------------------------------------------------------
# Networking - default VPC
# ----------------------------------------------------------------------------
data "aws_vpc" "default" {
  default = true
}

# ----------------------------------------------------------------------------
# AMI - Ubuntu 24.04
# ----------------------------------------------------------------------------
data "aws_ami" "ubuntu_2404" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ----------------------------------------------------------------------------
# Security Groups
# ----------------------------------------------------------------------------
resource "aws_security_group" "sg_app" {
  name        = "sg-app"
  description = "Cloud Integrity Lab - app instance"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Django"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "sg_db" {
  name        = "sg-db"
  description = "Cloud Integrity Lab - PostgreSQL"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description     = "PostgreSQL from app"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.sg_app.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ----------------------------------------------------------------------------
# DB Instance
# ----------------------------------------------------------------------------
resource "aws_instance" "cloud_integrity_db" {
  ami                    = data.aws_ami.ubuntu_2404.id
  instance_type          = "t2.micro"
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.sg_db.id]

  user_data = <<-EOF
    #!/bin/bash
    set -e
    apt-get update -y
    apt-get install -y postgresql postgresql-contrib

    PG_VER=$(ls /etc/postgresql/ | head -n1)
    PG_HBA="/etc/postgresql/$PG_VER/main/pg_hba.conf"
    PG_CONF="/etc/postgresql/$PG_VER/main/postgresql.conf"

    sed -i "s/^#listen_addresses.*/listen_addresses = '*'/" "$PG_CONF"
    echo "host all all 0.0.0.0/0 md5" >> "$PG_HBA"

    systemctl restart postgresql

    sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '${var.db_password}';"
    sudo -u postgres psql -c "CREATE DATABASE cloud_integrity_db;"
  EOF

  tags = {
    Name = "cloud-integrity-db"
  }
}

# ----------------------------------------------------------------------------
# App Instance
# ----------------------------------------------------------------------------
resource "aws_instance" "cloud_integrity_app" {
  ami                    = data.aws_ami.ubuntu_2404.id
  instance_type          = "t2.micro"
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.sg_app.id]

  user_data = templatefile("${path.module}/user_data_app.sh", {
    db_host     = aws_instance.cloud_integrity_db.private_ip
    db_password = var.db_password
    repo_url    = var.repo_url
  })

  depends_on = [aws_instance.cloud_integrity_db]

  tags = {
    Name = "cloud-integrity-app"
  }
}
