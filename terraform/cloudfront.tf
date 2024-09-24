resource "aws_s3_bucket" "app_website_bucket" {
  bucket = "email-snap-app-website-bucket"
}

resource "aws_s3_bucket_ownership_controls" "public" {
  bucket = aws_s3_bucket.app_website_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_public_access_block" "public" {
  bucket = aws_s3_bucket.app_website_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_acl" "public" {
  depends_on = [
    aws_s3_bucket_ownership_controls.public,
    aws_s3_bucket_public_access_block.public,
  ]

  bucket = aws_s3_bucket.app_website_bucket.id
  acl    = "public-read"
}

resource "aws_s3_bucket_website_configuration" "configurations" {
  bucket = aws_s3_bucket.app_website_bucket.bucket

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }

}

locals {
  s3_origin_id = "appS3Origin"
}

resource "aws_cloudfront_origin_access_control" "s3_oac" {
  name                              = "app-s3-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
  description                       = "Origin Access Control for app-public-static-website-bucket"
}

resource "aws_acm_certificate" "cert" {
  domain_name       = var.web_app_domain
  validation_method = "DNS"

  subject_alternative_names = [var.web_app_domain_alternative]
}

resource "aws_cloudfront_distribution" "website_distribution" {

  origin {
    domain_name              = aws_s3_bucket.app_website_bucket.bucket_regional_domain_name
    origin_id                = local.s3_origin_id
    origin_access_control_id = aws_cloudfront_origin_access_control.s3_oac.id
  }

  enabled             = true
  default_root_object = "index.html"

  aliases = [var.web_app_domain]

  default_cache_behavior {
    target_origin_id = local.s3_origin_id

    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = ["GET", "HEAD", "OPTIONS"]
    cached_methods  = ["GET", "HEAD", "OPTIONS"]

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
  }

  viewer_certificate {
    cloudfront_default_certificate = false
    ssl_support_method             = "sni-only"
    acm_certificate_arn            = aws_acm_certificate.cert.arn
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}

data "aws_iam_policy_document" "allow_access_to_s3" {
  statement {
    sid = "AllowCloudFrontServicePrincipalRead"
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    actions = [
      "s3:GetObject",
    ]
    resources = [
      "${aws_s3_bucket.app_website_bucket.arn}/*",
    ]

    condition {
      test     = "StringLike"
      variable = "AWS:SourceArn"

      values = [
        aws_cloudfront_distribution.website_distribution.arn
      ]
    }
  }

}

resource "aws_s3_bucket_policy" "this" {
  bucket = aws_s3_bucket.app_website_bucket.id
  policy = data.aws_iam_policy_document.allow_access_to_s3.json
}