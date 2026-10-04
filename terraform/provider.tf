terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 6.66.0"
    }

    awscc = {
      source  = "hashicorp/awscc"
      version = "~> 1.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = "ecr-lab"
}

provider "awscc" {
  region  = var.aws_region
  profile = "ecr-lab"
}