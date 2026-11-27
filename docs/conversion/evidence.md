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
