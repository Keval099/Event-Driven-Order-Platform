variable "aws_region" {
  description = "AWS region for the project"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name used for AWS resource naming"
  type        = string
  default     = "EventDrivenOrderPlatform"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}