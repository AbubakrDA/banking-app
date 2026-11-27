# Phase 17 — Stage F & Stage G: Operational Verification & Final Release Acceptance

## 1. Stage F — Staging & Operational Verification Status

### 1.1 Host Environment Verification
Direct inspection on the local host (`D:\BANKING_AI_PLATFORM`) confirmed the following infrastructure constraints:
- **Docker CLI:** `BLOCKED` (`'docker' is not recognized`) — Not installed on host.
- **AWS CLI:** `BLOCKED` (`'aws' is not recognized`) — Not installed on host.
- **Terraform CLI:** `BLOCKED` (`'terraform' is not recognized`) — Not installed on host.
- **Staging Secrets (`DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `S3_BUCKET_NAME`, `GEMINI_API_KEY`):** `BLOCKED` — Unset in local environment; managed in AWS Secrets Manager for staging/production.

### 1.2 Stage F Verification Matrix

| Verification Activity | Scope | Status | Evidence / Blocker Explanation |
| :--- | :--- | :---: | :--- |
| **End-to-End Application Suite** | All 16 phases, RBAC, multi-tenancy, AI chat, RAG, tickets, backup APIs | **`VERIFIED`** | `pytest tests/ -W default`: **98 / 98 passed** (4.55s, 0 warnings) |
| **Frontend Build & Lint Gate** | Vitest, TypeScript strict check, ESLint, Vite production bundle | **`VERIFIED`** | **8 / 8 Vitest passed**, **0 TS errors**, **0 ESLint warnings/errors**, clean `dist/` |
| **IaC & Container Security Audit** | Non-root user, healthchecks, Nginx CSP/HSTS, S3 KMS, RDS encryption | **`VERIFIED`** | `scripts/security_iac_audit.py`: **6 / 6 checks passed** |
| **Staging Artifact Pre-Flight** | Dockerfiles, Compose, Terraform, ECS task defs, SBOM, Runbooks | **`VERIFIED`** | `scripts/staging_readiness_check.py`: **12 / 12 artifacts `[PASS]`** |
| **Supply Chain & CVE Audit** | CycloneDX v1.5 SBOM & production npm audit | **`VERIFIED`** | `sbom.json` (23 components), `npm audit --omit=dev`: **0 vulnerabilities** |
| **Terraform Cloud Provisioning** | `terraform apply` for AWS VPC, ECS Fargate, RDS pgvector, S3 | **`BLOCKED`** | Requires CI/CD runner or authorized host with Terraform CLI + AWS credentials |
| **Container Image Build & ECR Push**| Build `Dockerfile.prod` and push to Amazon ECR | **`BLOCKED`** | Requires Docker Engine + AWS ECR authentication |
| **Live RDS Migration & Snapshot Drill**| `alembic upgrade head` & `aws rds restore-db-instance-from-db-snapshot` | **`BLOCKED`** | Requires live AWS RDS instance in staging VPC |
| **Distributed Cloud Load Test** | Sustained 500+ VU load test against live AWS ALB | **`BLOCKED`** | Requires live staging ALB endpoint |

---

## 2. Stage G — Final Release Acceptance Decision

### Final Decision: **`CONDITIONAL GO`**

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║                      STAGE G DECISION: CONDITIONAL GO                     ║
║                                                                           ║
║  All software engineering, security, architecture, and local verification ║
║  gates are 100% VERIFIED with zero errors and zero warnings. Live cloud   ║
║  provisioning, RDS migration, and physical snapshot restoration are       ║
║  BLOCKED on this host due to unavailable Docker/AWS/Terraform CLIs and    ║
║  cloud credentials, and must execute on an authorized CI/CD staging       ║
║  runner prior to public production DNS cutover.                           ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### Mandatory Pre-Cutover Conditions (To Be Executed on CI/CD & AWS Staging Runner)
1. **Provision Staging VPC & Services:** Execute `terraform apply` from `infrastructure/terraform/` in an authorized AWS staging account.
2. **Build & Push Hardened Images:** Build `backend/Dockerfile.prod` and `frontend/Dockerfile.prod` and push to Amazon ECR.
3. **Run Live Database Migrations:** Execute `alembic upgrade head` against staging RDS PostgreSQL 16 + `pgvector` and verify native PostgreSQL RLS.
4. **Execute Live RDS Snapshot Restore Drill:** Validate physical RDS snapshot restoration to an ephemeral instance and confirm RTO < 4 hours.
5. **Bind Production Secrets & TLS:** Populate AWS Secrets Manager (`DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `GEMINI_API_KEY`, OAuth/WhatsApp tokens) and attach ACM TLS 1.3 certificates to the ALB.
