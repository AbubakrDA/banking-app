# BankingAIPlatform — Production Operational Runbook

## 1. Incident Response Procedure
- **Severity Classification:**
  - `SEV-1`: Full service outage, data breach, or cross-tenant isolation anomaly -> Page On-Call SRE & Security Officer immediately; target ack < 15m.
  - `SEV-2`: Degraded AI/RAG latency (> 3s), background worker queue backlog, or failed scheduled backup -> Ack < 30m.
  - `SEV-3`: Single-tenant connector sync error or non-blocking UI bug -> Next business day triage.
- **Immediate Triage Commands:**
  - `NATIVE`: Check `.run\backend.err.log`, `.run\frontend.err.log`, `.run\supervisor.log`, and `.\scripts\deploy\Test-Native.ps1`.
  - `AWS_MANAGED / DOCKER`: Check CloudWatch `/ecs/banking-ai-platform-production`, `/api/v1/health`, `/api/v1/infrastructure/dashboard`.

## 2. Monitoring & Alerting Plan
- **Health Probes:** `/api/v1/health` (Backend FastAPI), `/healthz` (Frontend Nginx / `serve_frontend.mjs`).
- **CloudWatch Alarms (AWS):**
  - ALB `HTTPCode_Target_5XX_Count > 5` over 2 minutes.
  - ECS Service CPU > 85% or Memory > 85% sustained for 5 minutes.
  - RDS `FreeStorageSpace < 20 GB` or `DatabaseConnections > 80%`.

## 3. Security Maintenance & Dependency Update Procedure
- **Weekly:** Run `npm audit --omit=dev` and `python scripts/generate_sbom.py`.
- **Monthly:** Review `audit_logs` export (`/api/v1/enterprise/audit-logs/export`), rotate IAM/API keys, and run `scripts/security_iac_audit.py`.
- **Dependency Updates:** Update pinned versions in `backend/requirements.txt` and `frontend/package.json`, run full 103-test backend + 8-test frontend + build gates prior to tagging release.

## 4. Database Migration Runbook
1. Trigger manual pre-migration snapshot (`POST /api/v1/backup/trigger` or `aws rds create-db-snapshot`).
2. Inspect pending migrations: `alembic current && alembic history`.
3. Execute migration: `alembic upgrade head`.
4. Verify native RLS policies on PostgreSQL 16: `psql -f scripts/deploy/verify_rls_postgres.sql`.
5. Rollback if needed: `alembic downgrade -1` or restore pre-migration snapshot.

## 5. Environment Configuration & Release Rollback
- **Required Production Env Vars:** `ENVIRONMENT=production`, `SECRET_KEY` (32+ chars, enforced by `Settings.validate_production_secrets`), `DATABASE_URL`, `REDIS_URL`, `S3_BUCKET_NAME`, `GEMINI_API_KEY`.
- **Rollback:**
  - `NATIVE`: `.\scripts\deploy\Stop-Native.ps1`, checkout previous release tag, `.\scripts\deploy\Deploy-Native.ps1`, `.\scripts\deploy\Start-Native.ps1`.
  - `AWS_MANAGED / DOCKER`: `.\scripts\deploy\Invoke-StagingVerification.ps1 -StagingBaseUrl <URL> -RehearseRollback -PreviousTaskDefinitionArn <ARN>`.
