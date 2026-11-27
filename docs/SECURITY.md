# Security Posture & Verification Status

## Verification Matrix

| Control | Status | Notes |
|---|---|---|
| JWT validation (`alg`, `typ`, `iss`, `aud`, expiry) | `VERIFIED` | Tested in `backend/tests/test_auth_security.py` |
| Authenticated `/api/v1/tenants/current` from JWT + DB | `VERIFIED` | Tested in `backend/tests/test_tenant_and_route_audit.py` and `test_health.py` |
| Route surface & role declaration audit (`test_every_api_route_declares_surface_and_roles`) | `VERIFIED` | Tested in `backend/tests/test_tenant_and_route_audit.py`; inventory in `docs/conversion/route-audit.md` |
| Account ownership, `404` cross-customer isolation, `X-Override-Reason` audit | `VERIFIED` | Tested in `backend/tests/test_ownership.py` |
| Default-deny RBAC & surface isolation (`customer` / `staff` / `both`) | `VERIFIED` | Tested in `backend/tests/test_banking_rbac_matrix.py` |
| Department isolation (`hr` / `marketing` blocked from balances & transactions) | `VERIFIED` | Tested in `backend/tests/test_banking_rbac_matrix.py`, `test_requirements_coverage.py`, `test_banking_ai.py` |
| Pluggable `MFAProvider` hook on login & high-risk transfers | `VERIFIED` | Tested in `backend/tests/test_requirements_coverage.py` (`test_req_C6_mfa_hook_login_and_high_risk_actions`) |
| Tamper-evident SHA-256 audit hash chain & `/audit/verify` | `VERIFIED` | Tested in `backend/tests/test_banking_rbac_matrix.py` |
| Bilingual prompt-injection guard, PII masking, approved-only RAG | `VERIFIED` | Tested in `backend/tests/test_banking_ai.py` |
| Transfer `Idempotency-Key`, cross-border & S5 sanctions feature flags | `VERIFIED` | Tested in `backend/tests/test_banking_rbac_matrix.py` and `test_requirements_coverage.py` |
| In-memory frontend token store (no `localStorage`/`sessionStorage`) | `VERIFIED` | Implemented in `packages/shared/src/apiClient.ts` |
| Live PostgreSQL Row-Level Security (RLS) isolation as `app_user` | `UNVERIFIED` | Skipped in local run (`POSTGRES_TEST_URL=UNSET`; no `psql` or `docker` installed) |
| Keycloak RS256 JWKS validation | `UNVERIFIED` | Requires live Keycloak JWKS endpoint |
| ClamAV malware scanning in live deployment | `UNVERIFIED` | Disabled by default (`CLAMAV_ENABLED=False`); requires live `clamd` |
| Native mobile secure-enclave plugin binding | `NOT BUILT` | Web/Capacitor privacy shield & background lock implemented; native OS plugin requires mobile build |
