# Step 0 Baseline — `origin/harden/production-readiness` (`47b3f3a`)

## Dependency Setup
- `cd backend && uv sync --extra dev`: `uv sync` alone uninstalled dev dependencies (`pytest`, `aiosqlite`, `mypy`, `ruff`); `uv sync --extra dev` installed them, and `uv run pytest` revealed `greenlet` is missing from `backend/pyproject.toml` (`sqlalchemy[asyncio]` requires `greenlet`). Recorded for Item 12 / `pyproject.toml`.
- `cd frontend && npm ci`: installed 368 packages in 16s (reports 6 dev-dependency vulnerabilities; production audit checked separately).

## Baseline Backend (`python -m pytest -q --cov=app --cov-report=term-missing`)
- Result: `1 failed, 237 passed, 1 skipped in 19.57s`
- Coverage: `TOTAL 4008 statements, 1044 missed, 74%`
- Failure: `tests/test_auth_security.py::test_rbac_admin_vs_agent_permissions` (line 95 expected old ad-hoc error string `"Only organization admins or owners can create staff users"` instead of unified `require_roles` message `"lacks required permissions"` from Item 3).
- Skipped: `tests/test_rls_postgres_integration.py::test_rls_isolates_rows_on_real_postgres` (`POSTGRES_TEST_URL` / live PostgreSQL 16 unavailable on host).

## Baseline Frontend (`npm run lint && npx tsc --noEmit && npm test && npm run build`)
- `npm run lint`: exited 0
- `npx tsc --noEmit`: exited 0
- `npm test`: `Test Files 1 passed (1)`, `Tests 8 passed (8)` in `2.89s`
- `npm run build`: `1601 modules transformed`, built in `3.34s`
