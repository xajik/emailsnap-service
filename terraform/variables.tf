variable "aws_region" {
  description = "AWS region to deploy resources into"
  type        = string
  default     = "us-east-1"
}

variable "ssh_key_name" {
  description = "Name of the SSH key pair to use for EC2 instance"
  type        = string
  default     = "email_snap"
}

variable "ssh_key_path" {
  description = "Path to the SSH public key file"
  type        = string
  default     = "../ssh/email_snap.pub"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.small"
}

variable "domain" {
  description = "The domain to verify in SES (emailsnap.app)"
  type        = string
  default     = "emailsnap.app"
}

variable "s3_bucket_name" {
  description = "The S3 bucket to store received emails and attachments"
  type        = string
  default     = "emailsnap-app-emails" # Make sure the name is globally unique
}

variable "web_app_domain" {
  description = "Web App Work Domain"
  type        = string
  default     = "emailsnap.app"
}

variable "web_app_domain_alternative" {
  description = "Web App Work Domain"
  type        = string
  default     = "*.emailsnap.app"
}

variable "db_name" {
  description = "The name of the database to create"
  default     = "zDYOpfERcL"
}

variable "db_username" {
  description = "The database admin username"
  default     = "HwzMvgQOFX"
}

variable "db_password" {
  description = "The database admin password"
  default     = "fbZmbGsprt" # Replace with a AWS Secrets Manager
}