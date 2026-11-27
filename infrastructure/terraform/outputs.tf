output "vpc_id" {
  value       = aws_vpc.main.id
  description = "ID of the main VPC"
}

output "rds_endpoint" {
  value       = aws_db_instance.postgres.endpoint
  description = "Connection endpoint for PostgreSQL database"
}

output "s3_bucket_name" {
  value       = aws_s3_bucket.tenant_storage.id
  description = "Private S3 bucket name for tenant files"
}

output "ecs_cluster_name" {
  value       = aws_ecs_cluster.main.name
  description = "Name of the ECS Fargate cluster"
}

output "ecr_backend_url" {
  value       = aws_ecr_repository.backend.repository_url
  description = "ECR repository URL for backend image"
}

output "ecr_frontend_url" {
  value       = aws_ecr_repository.frontend.repository_url
  description = "ECR repository URL for frontend image"
}

output "alb_dns_name" {
  value       = aws_lb.main.dns_name
  description = "Public DNS name of the Application Load Balancer"
}

output "redis_endpoint" {
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
  description = "Primary TLS endpoint for ElastiCache Redis 7"
}

output "secrets_manager_arn" {
  value       = aws_secretsmanager_secret.app_secrets.arn
  description = "ARN of the AWS Secrets Manager container secret"
}
