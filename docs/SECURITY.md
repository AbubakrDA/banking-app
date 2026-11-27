# Security Posture & Verification Status

## Verification Matrix

| Control | Status | Notes |
|---|---|---|
| JWT validation (`alg`, `typ`, `iss`, `aud`, expiry) | `VERIFIED` | Tested in `backend/tests/test_auth_security.py` |
| Default-deny RBAC & surface isolation (`customer` / `staff` / `both`) | `VERIFIED` | Tested in `backend/tests/test_banking_rbac_matrix.py` |
| Department isolation (`hr` / `marketing` blocked from balances & transactions) | `VERIFIED` | Tested in `backend/tests/test_banking_rbac_matrix.py` and `backend/tests/test_banking_ai.py` |
| Cross-customer `404` & maker-checker self-approval block | `VERIFIED` | Tested in `backend/tests/test_banking_domain.py` and `test_banking_rbac_matrix.py` |
| Tamper-evident SHA-256 audit hash chain & `/audit/verify` | `VERIFIED` | Tested in `backend/tests/test_banking_rbac_matrix.py` |
| Bilingual prompt-injection guard, PII masking, approved-only RAG | `VERIFIED` | Tested in `backend/tests/test_banking_ai.py` |
| Transfer `Idempotency-Key` & cross-border feature flag | `VERIFIED` | Tested in `backend/tests/test_banking_rbac_matrix.py` |
| In-memory frontend token store (no `localStorage`/`sessionStorage`) | `VERIFIED` | Implemented in `packages/shared/src/apiClient.ts` |
| Live PostgreSQL Row-Level Security (RLS) isolation | `UNVERIFIED` | Requires `POSTGRES_TEST_URL` pointing to Postgres 16; skipped in local SQLite runs |
| Keycloak RS256 JWKS validation | `UNVERIFIED` | Requires live Keycloak JWKS endpoint |
| ClamAV malware scanning in live deployment | `UNVERIFIED` | Disabled by default (`CLAMAV_ENABLED=False`); requires live `clamd` |
| Native mobile secure-enclave plugin binding | `NOT BUILT` | Web/Capacitor privacy shield & background lock implemented; native biometric plugin requires mobile build |
