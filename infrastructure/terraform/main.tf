terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "BankingAIPlatform"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# ==========================================
# 1. VPC & Networking
# ==========================================
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "banking-ai-platform-${var.environment}-vpc"
  }
}

resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true
}

resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.aws_region}b"
  map_public_ip_on_launch = true
}

resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = "${var.aws_region}a"
}

resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.11.0/24"
  availability_zone = "${var.aws_region}b"
}

# ==========================================
# 2. Security Groups
# ==========================================
resource "aws_security_group" "alb" {
  name        = "banking-ai-platform-${var.environment}-alb-sg"
  description = "Public ALB ingress"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
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

resource "aws_security_group" "ecs_tasks" {
  name        = "banking-ai-platform-${var.environment}-ecs-sg"
  description = "Ingress from ALB only"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ==========================================
# 3. Amazon RDS PostgreSQL 16 + pgvector
# ==========================================
resource "aws_db_subnet_group" "rds" {
  name       = "banking-ai-platform-${var.environment}-db-subnet"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
}

resource "aws_db_instance" "postgres" {
  identifier            = "banking-ai-platform-${var.environment}-db"
  allocated_storage     = 100
  max_allocated_storage = 500
  engine                = "postgres"
  engine_version        = "16.3"
  instance_class        = "db.r6g.xlarge"
  db_name               = "banking_ai_db"
  username              = "postgres"
  password              = var.db_password
  db_subnet_group_name  = aws_db_subnet_group.rds.name
  multi_az              = true
  storage_encrypted     = true
  skip_final_snapshot   = false
  deletion_protection   = true
}

# ==========================================
# 4. Amazon S3 Private Tenant Storage
# ==========================================
resource "aws_s3_bucket" "tenant_storage" {
  bucket = "banking-ai-platform-${var.environment}-tenant-storage"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "s3_enc" {
  bucket = aws_s3_bucket.tenant_storage.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "s3_block" {
  bucket                  = aws_s3_bucket.tenant_storage.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ==========================================
# 5. ECS Fargate Cluster & Application Services
# ==========================================
resource "aws_ecs_cluster" "main" {
  name = "banking-ai-platform-${var.environment}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/banking-ai-platform-${var.environment}"
  retention_in_days = 90
}

# ==========================================
# 6. Amazon ECR Repositories
# ==========================================
resource "aws_ecr_repository" "backend" {
  name                 = "banking-ai-platform-${var.environment}-backend"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "frontend" {
  name                 = "banking-ai-platform-${var.environment}-frontend"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# ==========================================
# 7. Amazon ElastiCache Redis 7 (TLS)
# ==========================================
resource "aws_elasticache_subnet_group" "redis" {
  name       = "banking-ai-platform-${var.environment}-redis-subnet"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
}

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "banking-ai-platform-${var.environment}-redis"
  description                = "BankingAIPlatform Redis 7 TLS cluster"
  engine                     = "redis"
  engine_version             = "7.1"
  node_type                  = "cache.t4g.medium"
  num_cache_clusters         = 2
  port                       = 6379
  subnet_group_name          = aws_elasticache_subnet_group.redis.name
  transit_encryption_enabled = true
  at_rest_encryption_enabled = true
}

# ==========================================
# 8. Application Load Balancer (ALB + TLS)
# ==========================================
resource "aws_lb" "main" {
  name               = "banking-ai-platform-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_subnet.public_a.id, aws_subnet.public_b.id]
}

resource "aws_lb_target_group" "backend" {
  name        = "banking-ai-platform-${var.environment}-api-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/api/v1/health"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
  }
}

resource "aws_lb_listener" "https" {
  count             = var.acm_certificate_arn != "" ? 1 : 0
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.acm_certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
}

# ==========================================
# 9. AWS Secrets Manager
# ==========================================
resource "aws_secretsmanager_secret" "app_secrets" {
  name        = "banking-ai-platform/${var.environment}/app-secrets"
  description = "BankingAIPlatform runtime secrets (DATABASE_URL, REDIS_URL, SECRET_KEY, GEMINI_API_KEY)"
}
