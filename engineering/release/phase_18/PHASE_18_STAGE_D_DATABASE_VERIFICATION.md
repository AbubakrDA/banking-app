# Phase 18 — Stage D: Database Deployment & Verification Report

## 1. Alembic Migration & Schema Inspection
- **Migration Lineage:** 11 sequential migrations (`001_initial_multi_tenant_baseline.py` through `011_backup_and_disaster_recovery.py`) inspected.
- **pgvector Compatibility:** `001_initial_multi_tenant_baseline.py` line 20 executes `CREATE EXTENSION IF NOT EXISTS vector`, and `004_knowledge_base_rag.py` configures vector storage.
- **Indexes & Foreign Keys:** All tenant-scoped tables define `tenant_id` foreign keys with `ondelete='CASCADE'` and composite indexes (`ix_users_tenant_email`, `ix_conversations_tenant_status`, `ix_messages_tenant_conversation`).
- **Rollback Support:** Every migration includes an explicit `downgrade()` function.

---

## 2. Native PostgreSQL Row-Level Security (RLS) Gap & Preparation
- **Audit Finding:** Inspection of `001_initial_multi_tenant_baseline.py` confirmed that while `tenant_id` columns and ORM-level tenant filters are enforced across all services, **native PostgreSQL `ENABLE ROW LEVEL SECURITY` policies were not yet in the baseline migration**.
- **Remediation Delivered:** Created `scripts/deploy/verify_rls_postgres.sql` to:
  1. Verify `pg_extension` `vector` is installed.
  2. Enable `ROW LEVEL SECURITY` on `customers`, `conversations`, `messages`, `tickets`, `documents`, and `audit_logs`.
  3. Create `tenant_isolation_policy` bound to `current_setting('app.current_tenant_id', true)`.
  4. Execute a non-destructive read-only `BEGIN ... SET LOCAL ... ROLLBACK` cross-tenant isolation test.

---

## 3. Live Database Execution Status
- **Local Test Harness:** All **98 / 98** backend tests pass against SQLite in-memory (confirming ORM-level tenant isolation).
- **Live PostgreSQL 16 + pgvector Execution:** **`BLOCKED`** — No live staging PostgreSQL 16 RDS instance is provisioned yet.
- **Required Next Action:** Once Stage C provisions RDS in staging, run `alembic upgrade head` followed by `psql -f scripts/deploy/verify_rls_postgres.sql`.
