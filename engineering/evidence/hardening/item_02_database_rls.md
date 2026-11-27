# Item 2 Plan — Database-Level Tenant Isolation (PostgreSQL RLS)

## Plan
- **Change:** Add Alembic migration `013_enable_postgresql_rls.py` enabling & forcing RLS on all 33 `tenant_id` tables keyed on `current_setting('app.tenant_id', true)`. Wire `tenant_context_var` + `set_config('app.tenant_id', :tenant, true)` in `app/core/database.py`, set `tenant_context_var` exclusively from verified JWT in `auth.py`, and remove untrusted `X-Tenant-ID` header resolution from `middleware.py`. Document non-superuser DB role in `docs/postgresql_setup.md` and add `tests/test_rls_postgres_integration.py`.
- **Files:** `backend/alembic/versions/013_enable_postgresql_rls.py`, `backend/app/core/database.py`, `backend/app/core/middleware.py`, `backend/app/core/auth.py`, `docs/postgresql_setup.md`, `backend/tests/test_rls_postgres_integration.py`.
- **Tests:** JWT vs `X-Tenant-ID` header isolation test + real PostgreSQL RLS integration test (requires `POSTGRES_TEST_URL`).
- **Risk:** Medium if app DB role is superuser or table owner (bypasses RLS unless `FORCE ROW LEVEL SECURITY` + non-superuser role is used); mitigated by `FORCE ROW LEVEL SECURITY` and role setup docs.

## Execution & Evidence
- Audited all 34 SQLAlchemy tables: 30 strict `tenant_id` NOT NULL tables (including `sync_history`, `ticket_notes`, `messages`), 3 nullable `tenant_id` backup tables (`backup_records`, `backup_retention_policies`, `restore_drills`), and 1 root `tenants` table.
- Created migration `013_enable_postgresql_rls.py` enabling and forcing RLS on all 33 tenant tables.
- Implemented `tenant_context_var` + `apply_rls_tenant_context` (`set_config('app.tenant_id', :tenant, true)`) in `database.py`, populated strictly from verified JWT in `auth.py`.
- **Blocker:** Live PostgreSQL container execution (`test_postgres_rls_cross_tenant_isolation`) is `BLOCKED` on this host because `docker` and `psql` are not installed.

```
tests/test_rls_postgres_integration.py::test_x_tenant_id_header_cannot_spoof_jwt_tenant_context PASSED [ 20%]
tests/test_rls_postgres_integration.py::test_postgres_rls_cross_tenant_isolation SKIPPED [ 40%]
tests/test_health.py::test_health_check_endpoint PASSED                  [ 60%]
tests/test_health.py::test_tenant_context_endpoint PASSED                [ 80%]
tests/test_health.py::test_404_error_envelope PASSED                     [100%]
======================== 4 passed, 1 skipped in 0.54s =========================
```
