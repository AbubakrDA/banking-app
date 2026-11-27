# Phase 20 — Stage F: Deployment Mode Consistency Report

## 1. Environment × Mode Verification Matrix

| Target Combination | Application & Security Parity | Verification Status | Notes |
| :--- | :--- | :---: | :--- |
| **`WINDOWS_LOCAL + NATIVE`** | FastAPI (Uvicorn) + `frontend/dist` (`serve_frontend.mjs`) | **`PASS`** | Verified live startup, healthchecks, security headers, 5 MB log rotation, crash recovery, shutdown, and all `test_multi_mode_deployment.py` tests (`104/104` suite pass). |
| **`WINDOWS_LOCAL + DOCKER`** | `Dockerfile.prod` + `nginx.conf` + `docker-compose.prod.yml` | **`BLOCKED`** | Docker Engine not installed on host; static IaC checks pass. |
| **`GITHUB_ACTIONS`** | `.github/workflows/staging-deploy.yml` | **`BLOCKED`** | Requires GitHub Actions runner & AWS OIDC role. |
| **`AWS_CLOUDSHELL + AWS_MANAGED`** | `buildspec.yml` + Terraform + `docs/cloudshell_deployment.md` | **`BLOCKED`** | Requires AWS CloudShell session & authorized AWS account. |
