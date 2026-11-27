# Phase 19 — Stage E: AWS Readiness Report

## 1. Static AWS Architecture Validation (Zero Paid Provisioning)

| AWS Component | File / Manifest | Static Status | Key Configuration Verified |
| :--- | :--- | :---: | :--- |
| **Terraform Stack** | `infrastructure/terraform/main.tf`, `variables.tf`, `outputs.tf` | **`PASS` (Static)** | Multi-AZ VPC, private DB/Redis subnets, ALB TLS 1.3, ECS Cluster, CloudWatch 90-day logs |
| **AWS CodeBuild** | `buildspec.yml` | **`PASS` (Static)** | Remote ECR login, builds `backend/Dockerfile.prod` & `frontend/Dockerfile.prod` without local Docker |
| **ECS Task Definitions** | `infrastructure/ecs/task-definition-web.json`, `worker.json` | **`PASS` (Static)** | `executionRoleArn`, `taskRoleArn`, ECR image URIs, Secrets Manager `secrets` bindings |
| **ECR Repositories** | `infrastructure/terraform/main.tf` | **`PASS` (Static)** | `IMMUTABLE` tags, `scan_on_push = true` |
| **RDS & ElastiCache** | `infrastructure/terraform/main.tf` | **`PASS` (Static)** | RDS PG 16.3 Multi-AZ `storage_encrypted = true` + `deletion_protection = true`; Redis 7.1 TLS + at-rest enc |
| **S3 Storage** | `infrastructure/terraform/main.tf` | **`PASS` (Static)** | `AES256` SSE + 4-flag public access block (`security_iac_audit.py`: 6/6 passed) |
| **Live AWS `terraform plan/apply`** | AWS Account | **`BLOCKED`** | `aws` and `terraform` CLIs not installed locally; paid AWS provisioning not authorized |

## 2. Estimated Monthly AWS Staging Cost (Reference Estimate)
- **RDS PostgreSQL 16 (`db.r6g.xlarge`, Multi-AZ, 100GB gp3):** ~$500–$560/mo (can downsize to `db.t4g.medium` Single-AZ ~$60/mo for non-HA staging)
- **ElastiCache Redis 7 (`cache.t4g.medium` x2):** ~$95/mo
- **ECS Fargate (Web 2 vCPU/4GB + Worker 1 vCPU/2GB):** ~$90–$120/mo
- **ALB, NAT Gateways, S3, CloudWatch:** ~$85–$110/mo
- **Total Reference Staging Estimate:** ~$770–$885/mo (or ~$330/mo with `t4g.medium` staging sizing).
