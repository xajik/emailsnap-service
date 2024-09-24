output "ec2_ssh_command" {
  description = "Command to SSH into the EC2 instance"
  value       = "ssh -i ../ssh/id_rsa ec2-user@${aws_instance.fastapi_instance.public_ip}"
}

output "ec2_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.fastapi_instance.public_ip
}

output "ec2_instance_id" {
  description = "Instance ID of the EC2 instance"
  value       = aws_instance.fastapi_instance.id
}

output "ec2_public_dns" {
  description = "Public DNS of the EC2 instance"
  value       = aws_instance.fastapi_instance.public_dns
}

output "security_group_id" {
  description = "Security Group ID for the EC2 instance"
  value       = aws_security_group.fastapi_sg.id
}

output "ssh_access_command" {
  description = "Command to SSH into the EC2 instance"
  value       = "ssh -i ../ssh/email_snap ec2-user@${aws_instance.fastapi_instance.public_ip}"
}

output "ami_used" {
  description = "The AMI used for the EC2 instance"
  value       = data.aws_ami.amazon-linux-2.id
}

output "instance_type" {
  description = "The EC2 instance type used"
  value       = var.instance_type
}

output "s3_bucket_name" {
  description = "S3 bucket name for email storage"
  value       = aws_s3_bucket.email_bucket.bucket
}

output "sns_topic_arn" {
  description = "SNS topic ARN for email notifications"
  value       = aws_sns_topic.email_notifications.arn
}

output "ses_domain_identity_arn" {
  description = "SES domain identity ARN"
  value       = aws_ses_domain_identity.ses_domain.arn
}

output "sqs_queue_url" {
  description = "The URL of the SQS queue for email processing"
  value       = aws_sqs_queue.email_queue.id
}

output "sqs_queue_arn" {
  description = "The ARN of the SQS queue for email processing"
  value       = aws_sqs_queue.email_queue.arn
}

output "website_bucket_name" {
  value = aws_s3_bucket.app_website_bucket.bucket
}

output "website_bucket_regional_domain_name" {
  value = aws_s3_bucket.app_website_bucket.bucket_regional_domain_name
}

output "website_distribution" {
  value = aws_cloudfront_distribution.website_distribution.domain_name
}

output "db_endpoint" {
  description = "The endpoint of the Aurora DB cluster"
  value       = aws_db_instance.mysql_instance.endpoint
}