# BankingAIPlatform — Production Deployment & Operations Guide

## 1. Production Architecture Overview
BankingAIPlatform is engineered as a secure, containerized, multi-tenant cloud platform deployed on AWS using **ECS Fargate**, **RDS PostgreSQL 16 (with pgvector)**, **ElastiCache Redis 7**, **S3 Encrypted Buckets**, **CloudFront CDN**, and an **Application Load Balancer (ALB)**.

```mermaid
flowchart TD
    Client["HTTPS Clients & Browsers"] --> CF["AWS CloudFront CDN"]
    CF --> S3Static["S3 Frontend Bucket (SPA Assets)"]
    CF --> ALB["AWS Application Load Balancer (TLS 1.3)"]
    
    subgraph VPC["AWS Production VPC (10.0.0.0/16)"]
        subgraph PublicSubnets["Public Subnets"]
            ALB
        end
        
        subgraph AppSubnets["Private App Subnets"]
            ECSWeb["ECS Fargate: Web API (FastAPI)"]
            ECSWorker["ECS Fargate: Celery Task Workers"]
        end
        
        subgraph DBSubnets["Isolated Database Subnets"]
            RDS["RDS PostgreSQL 16 + pgvector"]
            Redis["ElastiCache Redis 7 Cluster"]
        end
    end

    ECSWeb --> RDS
    ECSWeb --> Redis
    ECSWorker --> RDS
    ECSWorker --> Redis
    ECSWeb --> S3Docs["S3 Private Storage (SSE-KMS)"]
```

---

## 2. Infrastructure Deployment Sequence

### Step 1: Provision Infrastructure via Terraform
```bash
cd infrastructure/terraform

# Initialize Terraform providers
terraform init

# Plan production infrastructure
terraform plan -var="environment=production" -out=tfplan

# Apply configuration
terraform apply tfplan
```

### Step 2: Configure Environment Variables & Secrets
Secrets are securely fetched from **AWS Secrets Manager** at task startup:
```ini
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://banking_ai_admin:SECURE_PASSWORD@banking-ai-platform-prod-db.c123.us-east-1.rds.amazonaws.com:5432/banking-ai-platform
REDIS_URL=rediss://banking-ai-platform-prod-redis.c123.us-east-1.cache.amazonaws.com:6379/0
SECRET_KEY=SECURE_256_BIT_HEX_KEY
S3_BUCKET_NAME=banking-ai-platform-documents-production
BACKEND_CORS_ORIGINS=["https://app.banking-ai-platform.com","https://admin.banking-ai-platform.com"]
```

### Step 3: Database Migration Execution
Run database migrations within an ephemeral ECS Fargate task:
```bash
aws ecs run-task \
  --cluster banking-ai-platform-production-cluster \
  --task-definition banking-ai-platform-migration-task \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-abc123],securityGroups=[sg-def456],assignPublicIp=DISABLED}" \
  --overrides '{"containerOverrides": [{"name": "migrator", "command": ["alembic", "upgrade", "head"]}]}'
```

### Step 4: Deploy Container Services
Push hardened multi-stage Docker images to Amazon Elastic Container Registry (ECR):
```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Build and tag backend
docker build -t banking-ai-platform-backend:latest -f backend/Dockerfile.prod backend/
docker tag banking-ai-platform-backend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/banking-ai-platform-backend:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/banking-ai-platform-backend:latest

# Trigger zero-downtime rolling update
aws ecs update-service \
  --cluster banking-ai-platform-production-cluster \
  --service banking-ai-platform-web-service \
  --force-new-deployment
```

---

## 3. Operational Health & Telemetry Verification

### Health Check Verification
- API Health: `GET /api/v1/health` -> Returns `{"status": "healthy"}`.
- Live Infrastructure Dashboard: `GET /api/v1/infrastructure/dashboard` -> Returns status across all 6 core services and RPO/RTO metrics.
- Backup Status: `GET /api/v1/backup/status` -> Returns live backup compliance and GFS rotation state.

### Automated Rollback Criteria & Execution
An automated deployment rollback is triggered immediately if:
1. ALB target health checks fail for > 120 seconds.
2. Container error rate spikes above 1% over a 5-minute rolling window.
3. Database connection pool errors or timeouts are encountered.

To execute a manual rollback from `WINDOWS_LOCAL` PowerShell:
```powershell
.\scripts\deploy\Invoke-StagingVerification.ps1 `
  -StagingBaseUrl "https://staging.banking-ai-platform.com" `
  -RehearseRollback `
  -PreviousTaskDefinitionArn "arn:aws:ecs:us-east-1:123456789012:task-definition/banking-ai-platform-staging-web:PREV_REV"
```

---

## 4. Environment & Deployment Mode Selection
BankingAIPlatform separates **Execution Environment** (`WINDOWS_LOCAL`, `GITHUB_ACTIONS`, `AWS_CLOUDSHELL`) from **Deployment Mode** (`NATIVE`, `DOCKER`, `AWS_MANAGED`). Docker is **optional**.

### Deployment Modes
- **`NATIVE`** *(Default on `WINDOWS_LOCAL`)*: Docker-free local production execution via Uvicorn + static production SPA server (`scripts/deploy/serve_frontend.mjs`):
  ```powershell
  .\scripts\deploy\Deploy-Native.ps1
  .\scripts\deploy\Start-Native.ps1
  .\scripts\deploy\Test-Native.ps1
  .\scripts\deploy\Stop-Native.ps1
  ```
- **`DOCKER`**: Local multi-stage container build -> ECR push -> ECS Fargate deploy:
  ```powershell
  .\scripts\deploy\Deploy-Staging.ps1 -Environment WINDOWS_LOCAL -Mode DOCKER -ConfirmProvisioning
  ```
- **`AWS_MANAGED`**: Remote AWS CodeBuild (`buildspec.yml`) -> ECR -> ECS Fargate + S3/CloudFront (no local Docker required):
  ```powershell
  .\scripts\deploy\Deploy-Staging.ps1 -Environment WINDOWS_LOCAL -Mode AWS_MANAGED -ConfirmProvisioning
  ```

### Runner Environments
- `WINDOWS_LOCAL` *(Default)*: Primary local PowerShell workflow.
- `GITHUB_ACTIONS` *(Optional CI/CD)*: Trigger `.github/workflows/staging-deploy.yml` via `workflow_dispatch`.
- `AWS_CLOUDSHELL` *(Optional AWS Shell)*: Follow `docs/cloudshell_deployment.md`.
