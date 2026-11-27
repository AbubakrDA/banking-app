# Phase 20 — Execution Plan

## 1. Mission & Authorization Scope
**Project:** BankingAIPlatform (`D:\BANKING_AI_PLATFORM`)  
**Default Environment:** `WINDOWS_LOCAL` + `NATIVE` (Docker optional)  
**Workflow:** `READ → PLAN → IMPLEMENT → TEST → INSPECT → REPAIR → RETEST → REPORT`

### Authorization Boundaries
- **Authorized:** Non-destructive engineering, test execution, security verification, PostgreSQL integration tooling, Windows reboot verification scripting, IAM least-privilege templates, and release documentation.
- **Prohibited Without Separate Explicit Authorization:** Paid AWS resource provisioning, production cutover, destructive database operations, or elevated system modifications/host reboots.

## 2. Stage Roadmap
- **Stage A:** Phase 19 baseline inspection and independent test reproduction.
- **Stage B:** PostgreSQL 16, `pgvector`, and native RLS setup documentation & repeatable test script (`docs/postgresql_setup.md`, `scripts/deploy/Test-PostgresIntegration.ps1`).
- **Stage C:** Windows Native finalization & reboot verification tooling (`scripts/deploy/Verify-RebootRecovery.ps1`).
- **Stage D:** Staging vs production security verification (`SECRET_KEY` guard, production OpenAPI disabling, security headers).
- **Stage E:** AWS Managed (`CodeBuild -> ECR -> ECS Fargate`) static readiness, IAM least-privilege policy (`infrastructure/iam/ecs-least-privilege-policy.json`), and cost estimation.
- **Stage F:** Deployment mode consistency matrix (`NATIVE`, `DOCKER`, `AWS_MANAGED`).
- **Stage G:** Final acceptance reporting with strict `PASS` / `FAIL` / `BLOCKED` / `NOT TESTED` classification.

