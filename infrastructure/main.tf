terraform {
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

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "mlops-monitoring"
}

variable "business_hours_start" {
  description = "Business hours start (24h format)"
  type        = number
  default     = 6
}

variable "business_hours_end" {
  description = "Business hours end (24h format)"
  type        = number
  default     = 18
}

# S3 Bucket for ML artifacts
resource "aws_s3_bucket" "ml_artifacts" {
  bucket = "${var.project_name}-artifacts-${random_string.suffix.result}"
}

resource "aws_s3_bucket_versioning" "ml_artifacts_versioning" {
  bucket = aws_s3_bucket.ml_artifacts.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "ml_artifacts_encryption" {
  bucket = aws_s3_bucket.ml_artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# IAM Role for SageMaker
resource "aws_iam_role" "sagemaker_role" {
  name = "${var.project_name}-sagemaker-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = ["sagemaker.amazonaws.com", "lambda.amazonaws.com"]
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "sagemaker_execution_role" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

resource "aws_iam_role_policy_attachment" "s3_full_access" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "cloudwatch_full_access" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchFullAccess"
}

# SNS Topic for alerts
resource "aws_sns_topic" "mlops_alerts" {
  name = "${var.project_name}-alerts"
}

# EventBridge rule for business hours monitoring
resource "aws_cloudwatch_event_rule" "business_hours_monitoring" {
  name                = "${var.project_name}-business-hours"
  description         = "Trigger monitoring during business hours only"
  schedule_expression = "cron(0 ${var.business_hours_start}-${var.business_hours_end-1} ? * MON-FRI *)"
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "mlops_dashboard" {
  dashboard_name = "${var.project_name}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/SageMaker", "Invocations", "EndpointName", "fraud-detection-endpoint"],
            [".", "ModelLatency", ".", "."]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "MLOps Monitoring - Business Hours Only"
        }
      }
    ]
  })
}

resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

output "s3_bucket_name" {
  value = aws_s3_bucket.ml_artifacts.bucket
}

output "sagemaker_role_arn" {
  value = aws_iam_role.sagemaker_role.arn
}

output "sns_topic_arn" {
  value = aws_sns_topic.mlops_alerts.arn
}

output "business_hours_schedule" {
  value = "${var.business_hours_start}:00 - ${var.business_hours_end}:00 (Mon-Fri)"
}