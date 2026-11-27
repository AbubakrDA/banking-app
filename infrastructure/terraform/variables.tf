variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "Target AWS Region"
}

variable "environment" {
  type        = string
  default     = "production"
  description = "Deployment environment"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
  description = "VPC CIDR block"
}

variable "db_password" {
  type        = string
  sensitive   = true
  description = "Amazon RDS PostgreSQL master password"
}

variable "domain_name" {
  type        = string
  default     = "banking-ai-platform.com"
  description = "Apex domain name for CloudFront and ALB Route 53 records"
}

variable "staging_subdomain" {
  type        = string
  default     = "staging.banking-ai-platform.com"
  description = "Staging subdomain for ALB and Route 53"
}

variable "acm_certificate_arn" {
  type        = string
  default     = ""
  description = "ACM TLS 1.3 Certificate ARN for HTTPS listener"
}
