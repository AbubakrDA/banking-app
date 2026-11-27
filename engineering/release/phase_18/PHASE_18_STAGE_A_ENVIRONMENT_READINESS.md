# Phase 18 — Stage A: Environment Readiness Report

## 1. Execution Context & Environment Selection
- **Primary Target Environment:** `WINDOWS_LOCAL` (Default, verified via `scripts/deploy/Select-Environment.ps1`)
- **Alternative Supported Runners:** `GITHUB_ACTIONS` (`.github/workflows/staging-deploy.yml`), `AWS_CLOUDSHELL` (`docs/cloudshell_deployment.md`)
- **Project Location:** `D:\BANKING_AI_PLATFORM`
- **Host Operating System:** Windows 11 Enterprise (`win32`)

---

## 2. Automated Pre-Flight Detection (`scripts/deploy/Invoke-StagingPreflight.ps1`)

### 2.1 Tooling & Runtime Detection
| Tool | Status | Observed Version / State | Required Action |
| :--- | :---: | :--- | :--- |
| **Git** | `PASS` | `git version 2.56.0.windows.4` | Ready |
| **Python** | `PASS` | `Python 3.12.8` | Ready |
| **Node.js** | `PASS` | `v24.22.1` | Ready |
| **npm** | `PASS` | `11.19.1` | Ready |
| **Docker Desktop / Engine** | `MISSING` | Not found on PATH | Install Docker Desktop for Windows (26+) |
| **AWS CLI v2** | `MISSING` | Not found on PATH | Install AWS CLI v2 MSI for Windows |
| **Terraform CLI** | `MISSING` | Not found on PATH | Install Terraform (>= 1.5.0) and add to PATH |

### 2.2 AWS Identity & Permissions Check
- **`aws sts get-caller-identity`:** `BLOCKED` — AWS CLI is not installed and no IAM credentials are configured in the local environment.

### 2.3 Required Staging Environment Variables & Secrets (Values Redacted)
All 8 required runtime variables are currently `[UNSET]` in the local Windows session and must be populated in **AWS Secrets Manager** (`banking-ai-platform/staging/app-secrets`) or staging `.env` prior to deployment:
- `ENVIRONMENT` (`UNSET`)
- `DATABASE_URL` (`UNSET`)
- `REDIS_URL` (`UNSET`)
- `SECRET_KEY` (`UNSET`)
- `S3_BUCKET_NAME` (`UNSET`)
- `GEMINI_API_KEY` (`UNSET`)
- `ACM_CERTIFICATE_ARN` (`UNSET`)
- `STAGING_DOMAIN` (`UNSET`)

---

## 3. Windows Installation Instructions for Missing Tools
To execute staging provisioning directly from `WINDOWS_LOCAL` PowerShell:
1. **Docker Desktop for Windows:** Download from `https://www.docker.com/products/docker-desktop/` (enable WSL 2 backend). Verify with `docker --version`.
2. **AWS CLI v2 (64-bit Windows MSI):** Download and run `https://awscli.amazonaws.com/AWSCLIV2.msi`. Configure credentials via `aws configure` or `aws sso login`. Verify with `aws sts get-caller-identity`.
3. **Terraform (>= 1.5.0):** Download Windows AMD64 binary from `https://developer.hashicorp.com/terraform/install`, extract `terraform.exe` to `C:\Tools\Terraform\`, and append to User/System `PATH`. Verify with `terraform --version`.
