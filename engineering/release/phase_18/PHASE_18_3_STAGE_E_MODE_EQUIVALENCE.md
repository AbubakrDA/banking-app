# Phase 18.3 — Stage E: Deployment Mode Equivalence Report

## 1. Cross-Mode Parity Verification Matrix

| Dimension | `NATIVE` (Windows Local) | `DOCKER` (Local/CI Containers) | `AWS_MANAGED` (CodeBuild + ECS/S3) | Equivalence Status |
| :--- | :--- | :--- | :--- | :---: |
| **Backend Application** | `backend/app/main.py` via Uvicorn ASGI | `backend/app/main.py` via `backend/Dockerfile.prod` | `backend/app/main.py` built via `buildspec.yml` | **`PASS`** |
| **Frontend Application** | `frontend/dist/` via `serve_frontend.mjs` | `frontend/dist/` via `nginx:1.27-alpine` (`Dockerfile.prod`) | `frontend/dist/` via ECS/S3+CloudFront | **`PASS`** |
| **Security Headers** | CSP, `X-Frame-Options`, `X-Content-Type-Options` | Identical headers in `frontend/nginx.conf` | Identical headers in `nginx.conf` / CloudFront | **`PASS`** |
| **Health & Smoke Endpoints** | `/api/v1/health`, `/healthz` (`Test-Native.ps1`) | `/api/v1/health`, `/healthz` (`HEALTHCHECK`) | `/api/v1/health`, `/healthz` (`Invoke-StagingVerification.ps1`) | **`PASS`** |
| **Database & Migrations** | Alembic `001`–`011` (`Deploy-Native.ps1`) | Alembic `001`–`011` + `verify_rls_postgres.sql` | Alembic `001`–`011` + `verify_rls_postgres.sql` | **`PASS`** |
| **Rollback Procedure** | `Stop-Native.ps1` + git checkout previous tag + restart | Revert Docker image tag + `docker compose up -d` | `Invoke-StagingVerification.ps1 -RehearseRollback` (ECS prev task def) | **`PASS`** |
