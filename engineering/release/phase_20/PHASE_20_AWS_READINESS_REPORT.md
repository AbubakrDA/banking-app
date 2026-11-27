# Phase 20 — Stage E: AWS Managed Deployment Readiness Report

## 1. Target Architecture (`CodeBuild → ECR → ECS Fargate`)
Validated statically without provisioning any paid AWS resources:
- **Remote Build (`buildspec.yml`):** Builds `backend/Dockerfile.prod` and `frontend/Dockerfile.prod` remotely in AWS CodeBuild and pushes immutable tags to Amazon ECR (`scan_on_push = true`). Zero local Docker required.
- **IAM Least-Privilege (`infrastructure/iam/ecs-least-privilege-policy.json`):** Created explicit IAM policy template scoped strictly to `banking-ai-platform/*` Secrets Manager secrets, `banking-ai-platform-*-tenant-storage` S3 buckets, and `/ecs/banking-ai-platform-*` CloudWatch Logs.
- **ECS Task Definitions:** `task-definition-web.json` & `worker.json` include `executionRoleArn`, `taskRoleArn`, ECR URIs, and AWS Secrets Manager `secrets` bindings.
- **Terraform Stack (`infrastructure/terraform/main.tf`):** Multi-AZ VPC, private DB/Redis subnets, RDS PostgreSQL 16.3 (`storage_encrypted = true`, `deletion_protection = true`), ElastiCache Redis 7.1 TLS, S3 SSE + public access block, ALB TLS 1.3 (`ELBSecurityPolicy-TLS13-1-2-2021-06`).

## 2. Estimated Monthly Cost Scenarios
- **Non-HA Staging Sizing (`db.t4g.medium` Single-AZ, `cache.t4g.small`, 1x Fargate Web + Worker):** ~$280–$350/month.
- **Production HA Sizing (`db.r6g.xlarge` Multi-AZ, `cache.t4g.medium` x2, Fargate auto-scaling 2–20):** ~$770–$885/month.

## 3. Readiness Status
- **Static IaC, IAM & CodeBuild Configuration:** **`PASS` (Static Only)**
- **Live AWS `terraform plan/apply` & Deployment:** **`BLOCKED`** (`aws` and `terraform` CLIs not installed locally; paid AWS provisioning not authorized).

