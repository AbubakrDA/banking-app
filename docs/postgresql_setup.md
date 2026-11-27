# BankingAIPlatform — PostgreSQL 16 & pgvector Setup Guide (Windows & Staging)

## 1. Overview
BankingAIPlatform requires **PostgreSQL 16** with the **`pgvector`** extension for vector embeddings (`001_initial_multi_tenant_baseline.py`, `004_knowledge_base_rag.py`) and native **Row-Level Security (RLS)** (`scripts/deploy/verify_rls_postgres.sql`).

> [!IMPORTANT]
> SQLite (`sqlite+aiosqlite`) is used strictly for isolated in-memory unit tests and **never** substitutes for native PostgreSQL 16 RLS or `pgvector` verification.

---

## 2. Option A: Native Windows PostgreSQL 16 Installation (Docker-Free)
1. Download the official **PostgreSQL 16 Windows x86-64 installer** from EDB (`https://www.enterprisedb.com/downloads/postgres-postgresql-downloads`).
2. Add `C:\Program Files\PostgreSQL\16\bin` to System `PATH` and verify:
   ```powershell
   psql --version
   ```
3. Install **`pgvector`** for Windows PostgreSQL 16 (build from source with Visual Studio Build Tools or install prebuilt `vector.dll` / `vector.control` into `share\extension` and `lib`).
4. Create database, enable `pgvector`, and create a **non-superuser, non-table-owner** application role (required so PostgreSQL RLS policies are enforced even without relying solely on `FORCE ROW LEVEL SECURITY`):
   ```sql
   CREATE DATABASE banking_ai_db;
   \c banking_ai_db
   CREATE EXTENSION IF NOT EXISTS vector;

   -- Migration owner role (runs alembic upgrade head)
   CREATE ROLE banking_ai_migrator WITH LOGIN PASSWORD '<MIGRATOR_PASSWORD>';
   GRANT ALL PRIVILEGES ON DATABASE banking_ai_db TO banking_ai_migrator;

   -- Runtime application role (non-superuser, non-owner, no BYPASSRLS)
   CREATE ROLE banking_ai_app WITH LOGIN PASSWORD '<APP_PASSWORD>' NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
   GRANT CONNECT ON DATABASE banking_ai_db TO banking_ai_app;
   GRANT USAGE ON SCHEMA public TO banking_ai_app;
   GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO banking_ai_app;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO banking_ai_app;
   ```

---

## 3. Option B: Authorized Remote PostgreSQL 16 / Amazon RDS
1. Provision or connect to an authorized PostgreSQL 16 + `pgvector` instance.
2. Export `DATABASE_URL` (never commit credentials):
   ```powershell
   $env:DATABASE_URL = "postgresql+asyncpg://<USER>:<PASSWORD>@<HOST>:5432/banking_ai_db"
   ```

---

## 4. Repeatable Verification Execution
Run the automated Stage B PostgreSQL integration script:
```powershell
.\scripts\deploy\Test-PostgresIntegration.ps1 -DatabaseUrl $env:DATABASE_URL
```
This script executes:
1. `alembic upgrade head` (validates all 11 migrations).
2. `psql -f scripts/deploy/verify_rls_postgres.sql` (validates `pgvector`, enables native RLS, and tests cross-tenant isolation).
3. Non-destructive `pg_dump` backup & isolated temporary database restore test.

