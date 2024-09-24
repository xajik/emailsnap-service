resource "aws_s3_bucket" "email_bucket" {
  bucket = var.s3_bucket_name
}

resource "aws_s3_bucket_policy" "email_bucket_policy" {
  bucket = aws_s3_bucket.email_bucket.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ses.amazonaws.com"
        },
        Action   = "s3:PutObject",
        Resource = "${aws_s3_bucket.email_bucket.arn}/*",
      }
    ]
  })
}

resource "aws_ses_domain_identity" "ses_domain" {
  domain = var.domain
}

resource "aws_sns_topic" "email_notifications" {
  name = "email-notifications"
}

# SES receipt rule set
resource "aws_ses_receipt_rule_set" "main" {
  rule_set_name = "default-rule-set"
}

resource "aws_ses_receipt_rule" "email_receipt_rule" {
  rule_set_name = aws_ses_receipt_rule_set.main.rule_set_name
  name          = "store_emails_to_s3_and_notify"

  recipients = ["review@${var.domain}"]

  enabled      = true
  scan_enabled = true


  s3_action {
    bucket_name       = aws_s3_bucket.email_bucket.bucket
    position          = 1
    object_key_prefix = "emails/"
  }

  sns_action {
    topic_arn = aws_sns_topic.email_notifications.arn
    position  = 2
  }
}

resource "aws_security_group" "fastapi_sg" {
  name_prefix = "fastapi-sg"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8088
    to_port     = 8088
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

resource "aws_key_pair" "key_pair" {
  key_name   = var.ssh_key_name
  public_key = file(var.ssh_key_path)
}

data "aws_ami" "amazon-linux-2" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm*"]
  }
}

resource "aws_instance" "fastapi_instance" {
  ami                         = "ami-06f555bf2f102b63c" # ami = data.aws_ami.amazon-linux-2.id
  instance_type               = var.instance_type
  iam_instance_profile        = aws_iam_instance_profile.ec2_instance_profile.name
  key_name                    = aws_key_pair.key_pair.key_name
  subnet_id                   = module.vpc.public_subnets[0]
  vpc_security_group_ids      = [aws_security_group.fastapi_sg.id]
  associate_public_ip_address = true

  user_data = <<-EOF
            #!/bin/bash
            sudo yum update -y || exit 1
            sudo yum install -y git docker fuse || exit 1
            sudo service docker start || exit 1
            sudo usermod -a -G docker ec2-user || exit 1
            curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose || exit 1
            sudo chmod +x /usr/local/bin/docker-compose || exit 1
            sudo -u ec2-user ssh-keygen -t rsa -b 4096 -f /home/ec2-user/.ssh/id_rsa -N "" || exit 1
            curl -LO https://github.com/neovim/neovim/releases/download/v0.5.0/nvim.appimage || exit 1
            mv nvim.appimage /usr/local/bin/nvim || exit 1
            sudo chmod +x /usr/local/bin/nvim || exit 1
            sudo yum clean all || exit 1
            EOF

  tags = {
    Name = "FastAPIInstance"
  }
}

resource "aws_iam_role" "ec2_role" {
  name = "FastAPI-EC2-Role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Principal = {
          Service = "ec2.amazonaws.com"
        },
        Effect = "Allow",
        Sid    = ""
      }
    ]
  })
}

resource "aws_iam_role_policy" "s3_access_policy" {
  name = "FastAPI-S3-Policy"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject"
        ],
        Resource = [
          "arn:aws:s3:::${var.s3_bucket_name}",
          "arn:aws:s3:::${var.s3_bucket_name}/*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ],
        Resource = aws_sqs_queue.email_queue.arn
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "FastAPI-Instance-Profile"
  role = aws_iam_role.ec2_role.name
}

resource "aws_sqs_queue" "email_queue" {
  name                       = "email-processing-queue"
  visibility_timeout_seconds = 30
  message_retention_seconds  = 86400
}

resource "aws_sqs_queue_policy" "email_queue_policy" {
  queue_url = aws_sqs_queue.email_queue.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = "*",
        Action    = "SQS:SendMessage",
        Resource  = aws_sqs_queue.email_queue.arn,
        Condition = {
          ArnEquals = {
            "aws:SourceArn" : aws_sns_topic.email_notifications.arn
          }
        }
      }
    ]
  })
}

resource "aws_sns_topic_subscription" "email_sqs_subscription" {
  topic_arn = aws_sns_topic.email_notifications.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.email_queue.arn
}