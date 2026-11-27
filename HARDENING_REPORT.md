# BankingAIPlatform Production-Readiness Hardening Report

**Branch:** `harden/production-readiness` (built on `origin/harden/production-readiness` at `47b3f3a`)  
**Date:** 2026-11-25  
**Protocol:** Harness Engineering (`READ → PLAN → IMPLEMENT → TEST → INSPECT → REPAIR → RETEST → REPORT`)

---

## 1. Summary of Changes by Priority

### P0 — Security
- **Item 1 (Tool approval gate, `81679c7` + Step 5 `c60007d`):** Enforced `owner`/`admin` role gate, `SELF_APPROVAL_FORBIDDEN` 403 rejection, `012_tool_requester_tracking.py`, and cross-tenant approval/rejection isolation test (`9 passed`).
- **Item 2 (PostgreSQL RLS, `0d0c9b3`):** Added `013_enable_postgresql_rls.py` (`app.tenant_id` forced RLS) and JWT-only `ContextVar` injection (`X-Tenant-ID` spoof test passed; live PG16 test **unverified** locally due to missing `psql`/`docker`).
- **Item 3 (Consistent RBAC, `0e0cd73` + `891a8a5`):** Unified `Depends(require_roles(...))` across endpoints with 129-case route matrix test (`129 passed`).
- **Item 4 (Malware scanning, `47b3f3a`):** `ClamAVScanner` (`INSTREAM`, fail-closed quarantine), full-file heuristic scan, and PDF active-object detection.
- **Item 5 (Secrets & JWT, `394bfc5`):** Enforced `alg == settings.ALGORITHM` (rejects `alg: none` & other algorithms), `typ == "JWT"`, non-empty signature, `exp`, `iss`, `aud`. Gated static HS256 secret behind `ALLOW_DEV_STATIC_JWT_SECRET` (fails startup in `staging`/`production` or if `KEYCLOAK_JWKS_URL` is missing). Verified 0 tracked `.env`/key files; `gitleaks` missing on host (`BLOCKED`).
- **Item 6 (Prompt-injection defenses, `b2bfe7d`):** Escaped closing envelope/system/instruction tags in `PromptGuard.sanitize_untrusted_envelope`, added `build_role_separated_messages`, added `backend/tests/fixtures/injections.json`, and verified Pydantic `ToolExecuteRequest` validation (`11 passed`).

### P1 — Correctness & Tests
- **Item 7 (KPI test & `tb.txt`, `9a7d0ec`):** Verified `test_kpi_dashboard_aggregation` passes (`1 passed in 0.49s`), archived historical traceback, and removed stale `backend/tb.txt`.
- **Item 8 (Coverage gate, `c420b9c` + `0d54d22`):** Measured baseline `74%`, set `fail_under = 74` in `backend/pyproject.toml`, and fixed `StaticPool` + `session` asyncio loop scope for `uv run pytest`.
- **Item 9 (Audit log hash chain, `2723401`):** Added `prev_hash` and `hash_timestamp` (`014_audit_log_hash_chain.py`), chained SHA-256 hashing ordered by `hash_timestamp`, `GET /api/v1/enterprise/audit-logs/verify`, and tamper-detection test (`7 passed`).
- **Item 10 (Error envelopes, `bf0ce4e`):** Mapped `ValueError` to specific 4xx codes (`404 NOT_FOUND`, `403 FORBIDDEN`, `409 CONFLICT`, `400 BAD_REQUEST`), safe `422` validation serialization, and sanitized `500 INTERNAL_SERVER_ERROR` (`5 passed`).

### P2 — Engineering Quality
- **Item 11 (CI/CD, `a410ef6`):** Added `.github/workflows/ci-security-and-tests.yml` covering `ruff`, `mypy app/services/`, `pytest --cov-fail-under=74` with PG16 service, frontend checks + `npm audit --omit=dev --audit-level=high`, `gitleaks`, `bandit`, `semgrep`, `pip-audit`, and `trivy` (`YAML_OK`; `actionlint` not installed locally).
- **Item 12 (Dependencies, `5583244`):** Added `pydantic[email]` and `sqlalchemy[asyncio]` extras to `backend/pyproject.toml`, regenerated `backend/uv.lock`, verified `npm audit --omit=dev --audit-level=high` (`0 vulnerabilities`).
- **Item 13 (Docker, `5915045`):** Hardened `docker-compose.yml` and `docker-compose.prod.yml` (non-root `10001:10001`, `read_only: true`, `no-new-privileges:true`, resource limits, healthchecks, no host port exposure for `postgres`/`redis`/`minio` in prod). YAML validated; `docker` CLI missing on host (`BLOCKED`).
- **Item 14 (Repo hygiene, `1574c38`):** Untracked 88 synthetic test PDFs from `backend/app/storage_data/` while keeping `backend/app/storage_data/` ignored in `.gitignore`.
- **Item 15 (Docs, `ffe1bb5`):** Updated `README.md` (Python `>=3.12`, Node `>=20`, `uv` commands, verification boundaries) and `PHASE_ROADMAP.md` (`Done` / `Partial` / `Not started`).

### P3 — Frontend
- **Item 16 (Wiring & Demo labeling, `8986105`):** Added `frontend/src/services/apiClient.ts` (in-memory token storage) and wired `AppShell.tsx` to probe `/api/v1/health` and display a `Demo Data` banner across all 9 demo module views.
- **Item 17 (Token storage & headers, `45483a1`):** Confirmed 0 `localStorage`/`sessionStorage`/`dangerouslySetInnerHTML`/`eval(` usages; added CSP + referrer meta tags to `frontend/index.html` and security/CSP headers to `TenantAndLoggingMiddleware` (`9 passed` in `test_production_hardening_security.py`).
- **Item 18 (Accessibility, `4e3a887`):** Added `role="dialog"`, `aria-modal`, `aria-labelledby`, and `Escape` dismissal to `Modal.tsx` + `aria-label` to `Sidebar.tsx` + `Modal.test.tsx` (`9 passed`). `axe` browser audit `BLOCKED` (not installed).

---

## 2. Blocked / Not Done Items

- **Live PostgreSQL 16 RLS Verification:** `BLOCKED` locally (`psql` and `docker` unavailable on Windows host; `test_rls_isolates_rows_on_real_postgres` skipped). Item 2 remains **unverified** against real Postgres until CI or PG16 runs.
- **Keycloak OIDC JWKS:** `NOT VERIFIED` (production startup guard rejects static secret, but live RS256 JWKS fetching and frontend PKCE login are not yet connected).
- **Security & A11y CLIs on Host:** `gitleaks`, `bandit`, `semgrep`, `trivy`, `pip-audit`, `actionlint`, `docker`, and `axe` are not installed on this Windows host (`BLOCKED` locally; security scanners configured in CI).

---

## 3. Ranked Remaining Risks

1. **Critical (`GAP-H01`):** Live PostgreSQL 16 RLS not yet executed against real Postgres.
2. **Critical (`GAP-H02`):** Live Keycloak OIDC JWKS validation and UI login flow not yet connected.
3. **High (`GAP-H03`):** All 9 frontend module pages still render static demo data.
4. **High (`GAP-H04`):** `gitleaks`, `bandit`, `semgrep`, `pip-audit`, and `trivy` have not yet executed in GitHub Actions.
5. **Medium (`GAP-H05`, `GAP-H06`):** Live `clamd` sidecar, Windows reboot test, and AWS staging/production cutover pending.

---

## 4. Exact Verified Command Outputs

- **Backend (`cd backend && uv run pytest -q --cov=app --cov-fail-under=74`):**
  ```
  TOTAL                                        3726    305    92%
  Required test coverage of 74% reached. Total coverage: 91.81%
  244 passed, 1 skipped in 12.60s
  ```
- **Frontend (`cd frontend && npm run lint && npx tsc --noEmit && npm test && npm run build`):**
  ```
  eslint src --ext .ts,.tsx -> exit 0
  npx tsc --noEmit -> exit 0
  vitest run -> Test Files 2 passed (2), Tests 9 passed (9) in 4.80s
  tsc && vite build -> 1602 modules transformed, built in 3.53s
  ```
- **Frontend Production Audit (`cd frontend && npm audit --omit=dev --audit-level=high`):**
  ```
  found 0 vulnerabilities
  ```
