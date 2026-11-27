# Phase 17 — Stage E: Staging Readiness & Verification Checklist

## 1. Executive Summary
All approved Stage D remediations have been implemented and verified with **0 errors and 0 warnings** across both backend and frontend test suites. This document defines the **Stage E Staging Readiness Procedures** and verification checklist required prior to executing Stage F (Staging Deployment & Operational Verification).

**Safety Constraint:** No cloud resources have been provisioned and no paid services have been triggered. Stage F deployment requires explicit authorization and AWS staging credentials.

---

## 2. Stage D Remediation Verification Summary

| Fix ID | Remediation Implemented | Result |
| :---: | :--- | :--- |
| **Fix 1** | Extracted React router hooks into `frontend/src/router/hooks.ts` | `VERIFIED` — ESLint reports **0 errors, 0 warnings** |
| **Fix 2** | Wrapped file reads in `test_cloud_infrastructure.py` in `with open(...)` | `VERIFIED` — Pytest runs with **0 ResourceWarnings** |
| **Fix 3** | Updated SQLAlchemy boolean filters to `.is_(True)` in `memory.py` & `nlp.py` | `VERIFIED` — **98 / 98** backend tests pass in 4.55s |
| **Fix 4** | Created `scripts/staging_readiness_check.py` diagnostic pre-flight script | `VERIFIED` — All 12 production artifacts `[PASS]` |

---

## 3. Staging Pre-Flight Checklist (Stage E → Stage F)

### 3.1 Infrastructure & Secrets Prerequisites
- [ ] Authorize target AWS Staging Account and IAM deployment role.
- [ ] Run `python scripts/staging_readiness_check.py` in target CI/CD runner.
- [ ] Populate AWS Secrets Manager entries for `banking-ai-platform/staging`:
  - `DATABASE_URL` (PostgreSQL 16 + `pgvector`)
  - `REDIS_URL` (ElastiCache Redis 7 TLS)
  - `SECRET_KEY` (256-bit cryptographic signing key)
  - `S3_BUCKET_NAME` (`banking-ai-platform-documents-staging`)
  - `GEMINI_API_KEY` (LLM API key)
- [ ] Configure ACM TLS certificate ARN and staging subdomain (`staging.banking-ai-platform.com`).

### 3.2 Staging Deployment Sequence (To Execute in Stage F Upon Approval)
1. **Provision Infrastructure:**
   ```bash
   cd infrastructure/terraform
   terraform workspace select staging || terraform workspace new staging
   terraform plan -var="environment=staging" -out=staging.tfplan
   terraform apply staging.tfplan
   ```
2. **Build & Push Container Images to ECR:**
   - Build `backend/Dockerfile.prod` and `frontend/Dockerfile.prod` via CI/CD runner.
   - Push tagged `:staging` images to Amazon ECR.
3. **Execute Database Migrations & Verify Native RLS:**
   ```bash
   alembic upgrade head
   ```
4. **Execute Staging Operational Verification (Stage F):**
   - Smoke test `/api/v1/health` and `/api/v1/infrastructure/dashboard`.
   - Run live non-destructive RDS snapshot restore drill (`aws rds restore-db-instance-from-db-snapshot`).
   - Execute distributed load test (`k6` / `Locust`) against staging ALB.
   - Verify CloudWatch logs and rollback rehearsal (`aws ecs update-service --force-new-deployment` to previous task revision).
