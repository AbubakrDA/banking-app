# Conversion Evidence — `AbubakrDA/banking-app`

## Step 0 Checks
```
1_PWD=D:\banking-app\banking-app
1_REMOTE=https://github.com/AbubakrDA/banking-app.git
2_BRANCH=main
3_HEAD=3948354 chore: fork ConversaIQ hardening branch into banking-ai-platform
4_BANKING_MD=True
5_STATUS: (clean)
```

## Phase A — Remove Support-Desk Product
- Removed `tickets`, `nlp`, `business_data`, `connectors`, `data_quality`, old support-desk tests, old frontend pages (`BusinessDataHubPage`, `ComplaintsTicketsPage`, `IntegrationsToolsPage`), and 28 old ConversaIQ `.md` reports.
- Added `backend/alembic/versions/015_drop_support_desk_tables.py`.
- Command: `python -m pytest tests/test_health.py tests/test_auth_security.py -v`
- Result: `10 passed in 0.72s`


## Phase B — Banking Domain
- Added `BankAccount`, `BankTransaction`, `BankTransfer`, `BankCard`, `RiskAlert`, `PolicyDocument`, `PolicyChunk` (`BigInteger` minor units).
- Added `backend/alembic/versions/016_banking_domain_tables.py` (`down_revision = '015_drop_support_desk_tables'`).
- Added `BankingAPI` protocol, `MockBankingAPI` (2 customers, 3 accounts, 2 cards, 10 transactions, 1 approved policy in dev/test only), and `BankingService` (ownership, staff reason + flagged audit, transfer validation, high-risk approval + `SELF_APPROVAL_FORBIDDEN`, card block/unblock, policy upload/review, allow/deny audit).
- Command: `python -m pytest tests/test_banking_domain.py -v`
- Result: `1 passed in 0.33s`

## Phase C — Banking API Routes (`/api/v1`), Surfaces, Idempotency & Integrations
- Added `/api/v1/accounts`, `/transactions`, `/transfers`, `/cards`, `/customers`, `/risk`, `/approvals`, `/policies`, `/audit`, `/admin`, `/integrations`.
- Added `require_surface("customer" | "staff" | "both")` on every banking route, `hr` and `marketing` department isolation, configurable `STAFF_IDLE_TIMEOUT_MINUTES` (default 10m), `Idempotency-Key` deduplication on transfers, `ENABLE_CROSS_BORDER_TRANSFERS` feature flag (default `False`), and `IntegrationProvider` registry (`MobileMoneyProvider`, `AgentNetworkProvider`, `StubProvider`, startup validation).
- Command: `python -m pytest tests/test_health.py tests/test_auth_security.py tests/test_banking_domain.py tests/test_banking_rbac_matrix.py -v`
- Result: `14 passed in 1.31s`

## Phase D — Bilingual AI Layer, Guardrails & Approved Policy RAG
- Added `language.py` (`ar` / `en` / `mixed` detector), `intent.py` (rule-based intents & entity extraction), `provider.py` (`LLMProvider` protocol + `StubLLMProvider` with zero vendor SDK/API keys), `retrieval.py` (approved-only `PolicyDocument` RAG + AR/EN safe abstention), and updated `prompt_guard.py` (AR/EN prompt injection, cross-customer refusal, account/national-ID output masking).
- Updated `BankingToolGateway`, `BankingAIAgent`, and `POST /api/v1/chat` so all AI tool calls route through `BankingService` with RBAC, ownership, and audit logging.
- Command: `python -m pytest tests/test_banking_ai.py -v`
- Result: `3 passed in 0.43s`

## Phase E — Two Frontend Apps (`apps/customer`, `apps/staff`) & `packages/shared`
- Created `packages/shared/` (`types.ts`, `apiClient.ts` with in-memory token store only & `Idempotency-Key`/`X-Access-Reason` headers, `translations.ts` with EN/AR + RTL direction).
- Created `apps/customer/` (login, biometric/PIN background lock + privacy shield, accounts/balances in minor units, transactions, idempotent transfers, card block/unblock, bilingual AI chat, Capacitor config).
- Created `apps/staff/` (separate login & build with zero imports from `apps/customer/`, 10-minute idle timeout, written-reason customer search, risk alerts, approvals, audit chain verify, HR/Marketing policy-only restricted view).
- Command: `npm.cmd run typecheck; npm.cmd test; npm.cmd run build`
- Result: `apps/customer`: `3 passed`, `tsc` & `vite build` passed; `apps/staff`: `3 passed`, `tsc` & `vite build` passed.

## Phase F — Documentation, Compliance, CI & Final Verification
- Added/updated `README.md`, `BANKING.md`, `docs/SECURITY.md`, `docs/decisions.md`, `docs/requirements.md`, `docs/integrations.md`, `docs/compliance/cbos.md`, and `.github/workflows/ci-security-and-tests.yml`.
- Historical (before `banking/update-2026-11-27`, not re-run): backend `31 passed, 1 skipped in 1.51s`. Superseded by the live verification run below.
- Frontend workspaces (`npm.cmd run typecheck; npm.cmd test; npm.cmd run build`): `@banking/customer-app`: `3 passed`; `@banking/staff-app`: `3 passed`; `tsc` & `vite build` passed for both apps.

## Baseline Note (`247b533`)
- Starting commit on `main`: `247b533` (empty commit message, author "Verdent Agent"), preserved without rewriting history.

## Live Verification Run (`banking/update-2026-11-27` at `2056401`, fresh clone `D:\banking-verify`)
- **Live PostgreSQL 16 RLS (`test_postgres_rls_cross_tenant_isolation`):** `UNVERIFIED` (SKIPPED).
  - PostgreSQL version / role: Not installed (`BLOCKED`). `winget install -e --id PostgreSQL.PostgreSQL.16` failed with: `Downloading https://get.enterprisedb.com/postgresql/postgresql-16.16-2-windows-x64.exe` -> `0x80190193 : Forbidden (403)`. No `psql` or `docker` is installed on the host, so `POSTGRES_TEST_URL` remained unset.
  - RLS skip output: `SKIPPED [1] tests\test_rls_postgres_integration.py:25: Live PostgreSQL 16 + non-superuser role unavailable (POSTGRES_TEST_URL unset)`
- **Backend Ruff & Pytest (`D:\banking-verify\backend` after `python -m pip install -r requirements.txt`):**
  - Command: `python -m ruff check app` -> `Found 1117 errors.` (`[*] 689 fixable with --fix (3 unsafe fixes available with --fix --unsafe-fixes)`).
  - Command: `python -m pytest -q -rs`
  ```
  ........................................s..                              [100%]
  =========================== short test summary info ===========================
  SKIPPED [1] tests\test_rls_postgres_integration.py:25: Live PostgreSQL 16 + non-superuser role unavailable (POSTGRES_TEST_URL unset)
  42 passed, 1 skipped in 2.11s
  ```
  - Failed tests: none (0 failed).
- **Frontend Workspaces (`D:\banking-verify`):**
  - `npm ci`: `added 188 packages, and audited 192 packages in 8s`
  - `npm run typecheck`: `@banking/customer-app` `tsc --noEmit` (exit 0); `@banking/staff-app` `tsc --noEmit` (exit 0).
  - `npm test`: `@banking/customer-app` `Test Files 1 passed (1), Tests 3 passed (3)`; `@banking/staff-app` `Test Files 1 passed (1), Tests 3 passed (3)`.
  - `npm run build`: `@banking/customer-app` `dist/assets/index-BfyPvx91.js 154.30 kB │ gzip: 50.17 kB (built in 1.03s)`; `@banking/staff-app` `dist/assets/index-CDptEYMp.js 153.50 kB │ gzip: 49.98 kB (built in 1.06s)`.
