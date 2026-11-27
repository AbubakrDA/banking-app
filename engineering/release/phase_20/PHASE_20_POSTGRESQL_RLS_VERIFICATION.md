# Phase 20 — Stage B: PostgreSQL 16, pgvector & Native RLS Verification

## 1. PostgreSQL 16 Tooling Delivered
- **Setup Guide:** `docs/postgresql_setup.md` (covers native Windows PostgreSQL 16 + `pgvector` installation without Docker, and authorized remote RDS connection).
- **Repeatable Integration Script:** `scripts/deploy/Test-PostgresIntegration.ps1`:
  - Rejects `sqlite*` URLs (enforces genuine PostgreSQL 16).
  - Executes `alembic upgrade head` & `alembic current`.
  - Executes `scripts/deploy/verify_rls_postgres.sql` (`vector` extension check, `ENABLE ROW LEVEL SECURITY` on `customers`, `conversations`, `messages`, `tickets`, `documents`, `audit_logs`, and read-only cross-tenant isolation transaction).
  - Executes non-destructive `pg_dump --schema-only` backup verification.

## 2. Live Execution Result (`scripts/deploy/Test-PostgresIntegration.ps1`)
```
=== BankingAIPlatform PostgreSQL 16 + pgvector + RLS Integration Test ===
WARNING: [BLOCKED] 'psql' CLI is not installed on this host. Install PostgreSQL 16 (see docs/postgresql_setup.md).
```

| Criterion | Status | Evidence / Explanation |
| :--- | :---: | :--- |
| **PostgreSQL Setup Documentation** | **`PASS`** | `docs/postgresql_setup.md` created |
| **Repeatable Integration & RLS Script** | **`PASS`** | `scripts/deploy/Test-PostgresIntegration.ps1` & `verify_rls_postgres.sql` created |
| **PostgreSQL 16 + `pgvector` Connectivity** | **`BLOCKED`** | `psql` / PostgreSQL 16 not installed on Windows host |
| **Live `alembic upgrade head` on PG 16** | **`BLOCKED`** | Requires live PostgreSQL 16 instance |
| **Native PostgreSQL RLS Verification** | **`BLOCKED`** | Requires live PostgreSQL 16 instance (SQLite not substituted) |
| **Live `pg_dump` / Restore Verification** | **`BLOCKED`** | Requires live PostgreSQL 16 instance |
