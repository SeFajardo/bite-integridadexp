variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "db_password" {
  description = "PostgreSQL password for the cloud_integrity_db user"
  type        = string
  sensitive   = true
  default     = "BitePass2025"
}

variable "key_name" {
  description = "Name of the EC2 key pair to attach to the instances"
  type        = string
  default     = "vockey"
}

variable "repo_url" {
  description = "Public Git URL of the cloud-integrity-lab repository"
  type        = string
  default     = "https://github.com/SeFajardo/bite-integridadexp.git"
}
