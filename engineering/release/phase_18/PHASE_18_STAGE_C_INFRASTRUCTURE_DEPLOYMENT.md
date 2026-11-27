# Phase 18 — Stage C: Terraform & AWS Staging Infrastructure Report

## 1. Infrastructure Inspection & Gap Remediation
Independent inspection of `infrastructure/terraform/main.tf` revealed that while VPC, Subnets, Security Groups, RDS PostgreSQL 16.3, S3 encryption, and ECS Cluster were defined, several resources required for end-to-end staging deployment were missing. During Phase 18 preparation, the Terraform stack was enhanced (without provisioning any live resources) to include:
- **Amazon ECR Repositories:** `aws_ecr_repository.backend` & `aws_ecr_repository.frontend` (`IMMUTABLE` tags, `scan_on_push = true`).
- **Amazon ElastiCache Redis 7 TLS:** `aws_elasticache_replication_group.redis` (`engine_version = "7.1"`, `transit_encryption_enabled = true`, `at_rest_encryption_enabled = true`).
- **Application Load Balancer (ALB):** `aws_lb.main`, `aws_lb_target_group.backend` (healthcheck `/api/v1/health`), and conditional HTTPS TLS 1.3 listener (`ELBSecurityPolicy-TLS13-1-2-2021-06`).
- **AWS Secrets Manager:** `aws_secretsmanager_secret.app_secrets` (`banking-ai-platform/${var.environment}/app-secrets`).

---

## 2. Complete Staging Resource Inventory (Planned)

| AWS Resource | Terraform Identifier | Security & Cost Notes |
| :--- | :--- | :--- |
| **VPC & 4 Subnets (2 AZs)** | `aws_vpc.main`, `public_{a,b}`, `private_{a,b}` | `10.0.0.0/16` multi-AZ topology |
| **Security Groups** | `aws_security_group.alb`, `ecs_tasks` | Port 443 public ALB -> Port 8000 ECS only |
| **RDS PostgreSQL 16.3** | `aws_db_instance.postgres` | `db.r6g.xlarge`, Multi-AZ, `storage_encrypted = true`, `deletion_protection = true` |
| **ElastiCache Redis 7** | `aws_elasticache_replication_group.redis` | `cache.t4g.medium` (2 nodes), TLS + at-rest encryption |
| **S3 Private Storage** | `aws_s3_bucket.tenant_storage` | `AES256` SSE + 4-flag public access block |
| **ECR Repositories** | `aws_ecr_repository.backend`, `frontend` | Immutable tags + scan-on-push |
| **ECS Fargate & CloudWatch** | `aws_ecs_cluster.main`, `aws_cloudwatch_log_group.ecs_logs` | Container Insights enabled, 90-day log retention |
| **ALB & Secrets Manager** | `aws_lb.main`, `aws_secretsmanager_secret.app_secrets` | TLS 1.3 policy; secret container only |

---

## 3. Terraform Execution & Deployment Boundary
- **`terraform init` / `terraform validate` / `terraform plan`:** **`BLOCKED`** on `WINDOWS_LOCAL` (`'terraform' is not recognized` on host PATH).
- **Remote State Note:** `main.tf` currently uses default local state; before team/CI staging deployment, configure an S3 backend + DynamoDB state lock table.
- **Deployment Safety Gate:** `scripts/deploy/Deploy-Staging.ps1` enforces `-ConfirmProvisioning` so `terraform apply` can never execute without explicit authorization.
