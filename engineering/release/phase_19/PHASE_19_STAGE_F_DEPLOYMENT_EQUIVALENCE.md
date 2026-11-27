# Phase 19 — Stage F: Deployment Equivalence Report

## 1. Environment × Mode Verification Status

| Execution Environment | Deployment Mode | Application & Security Parity | Live Execution Status | Evidence / Blocker |
| :--- | :--- | :---: | :---: | :--- |
| **`WINDOWS_LOCAL`** | **`NATIVE`** | Identical FastAPI + `frontend/dist` + security headers | **`VERIFIED` (Live)** | `Deploy-Native.ps1`, `Test-NativeReliability.ps1` (startup, crash recovery, log rotation, shutdown) |
| **`WINDOWS_LOCAL`** | **`DOCKER`** | Identical app + `Dockerfile.prod` + `nginx.conf` | **`BLOCKED` (Static `PASS`)** | Docker Engine not installed on Windows host; `security_iac_audit.py` 6/6 passed |
| **`GITHUB_ACTIONS`** | **`DOCKER`** | Identical app + `.github/workflows/staging-deploy.yml` | **`BLOCKED` (Static `PASS`)** | Requires GitHub repository runner & OIDC AWS role |
| **`GITHUB_ACTIONS`** | **`AWS_MANAGED`** | Identical app + `buildspec.yml` + ECS/RDS Terraform | **`BLOCKED` (Static `PASS`)** | Requires GitHub runner & AWS staging authorization |
| **`AWS_CLOUDSHELL`** | **`AWS_MANAGED`** | Identical app + `docs/cloudshell_deployment.md` | **`BLOCKED` (Static `PASS`)** | Requires AWS CloudShell session & AWS account |

## 2. Cross-Mode Invariants Verified
- All modes enforce identical authentication, 4-tier RBAC, 5-layer `PromptGuard`, Pydantic v2 validation, Alembic migration chain (`001`–`011`), and `/api/v1/health` + `/healthz` smoke contracts.
- Only `WINDOWS_LOCAL + NATIVE` is claimed as live-verified; all Docker and AWS modes are honestly reported as static-verified / cloud-blocked.
