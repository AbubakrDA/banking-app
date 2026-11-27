# Architecture Decisions

1. **Cross-Customer Resources Return `404` Instead of `403`:**
   Returning `404 Not Found` when a customer requests another customer's account, transaction, or card prevents existence enumeration while still recording a `DENIED` audit log entry.
2. **Staff Access Reason (`X-Access-Reason` or `?reason=`):**
   All staff reads across customer accounts, transactions, transfers, cards, and customer search require a non-empty written reason, which is flagged (`staff_access: true`) in the immutable audit trail.
3. **Money Stored Strictly as Integer Minor Units:**
   All balances, transaction amounts, and transfer amounts use `BigInteger` / `int` minor units (e.g., cents/piastres) to eliminate floating-point rounding drift.
4. **Vendor-Agnostic `LLMProvider` + `StubLLMProvider`:**
   No LLM vendor SDK or API key is embedded. All model calls go through `LLMProvider`, defaulting to `StubLLMProvider`.
5. **Two Separate Frontend Apps (`apps/customer` & `apps/staff`):**
   Customer and staff surfaces are built as separate Vite applications. `apps/staff` never imports any component from `apps/customer`; shared types, API client, and translations live in `packages/shared`.
6. **Mobile Wrapper & Token Storage Choice:**
   `apps/customer` targets responsive web wrapped with Capacitor (`capacitor.config.ts` with `PrivacyScreen`). Access tokens stay in memory only (`packages/shared/src/apiClient.ts`), never written to disk (`localStorage`/`sessionStorage`); native deployments should bind to OS Keychain/Keystore via a Capacitor secure-storage plugin, and `visibilitychange` immediately locks the session and hides balances/transfers.

7. **Operations Research (OR) Module (`backend/app/services/optimisation/`):**
   Pluggable `OptimisationProvider` interface with a zero-dependency deterministic `RuleBasedAllocationBaseline` (integer minor units). Open items awaiting bank confirmation before any solver or domain rules are implemented:
   - *Open Item OR-1:* Branch/ATM/agent-network cash liquidity replenishment targets and SLAs.
   - *Open Item OR-2:* FX / treasury routing constraints (deferred until CBOS & sanctions decisions are finalized).
