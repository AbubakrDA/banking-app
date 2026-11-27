# Item 5 Plan — Secrets & JWT Validation

## Plan
- **Config (`backend/app/core/config.py`):** Add `JWT_ISSUER`, `JWT_AUDIENCE`, `KEYCLOAK_JWKS_URL`, and `ALLOW_DEV_STATIC_JWT_SECRET`. Fail startup in `production`/`staging` if `ALLOW_DEV_STATIC_JWT_SECRET` is enabled or `KEYCLOAK_JWKS_URL` is missing.
- **Security (`backend/app/core/security.py`):** Enforce `header["alg"] == settings.ALGORITHM` (rejecting `alg: none` and other algorithms), `header["typ"] == "JWT"`, non-empty signature, `exp`, `iss`, and `aud`. Reject static-secret validation when `ALLOW_DEV_STATIC_JWT_SECRET` is `False` or `ENVIRONMENT in ("production", "staging")`.
- **Gitleaks:** Check `git ls-files *.env .env* *.pem *.key` and attempt `gitleaks detect` (mark `BLOCKED` if `gitleaks` is absent on host).
- **Tests (`backend/tests/test_auth_security.py`):** Valid token, expired, wrong issuer, wrong audience, `alg: none`, wrong algorithm, unsigned token, and production static-secret startup rejection.

## Evidence
- `git ls-files *.env .env* *.pem *.key` returned empty.
- `where.exe gitleaks`: `gitleaks_not_installed` (`BLOCKED` on host; configured in CI in Item 11).
- `verify_access_token` enforces `alg == settings.ALGORITHM` (rejecting `alg: none` and `HS512`/`RS256`), `typ == "JWT"`, non-empty signature, `exp`, `iss`, and `aud`.
- `Settings.validate_production_secrets` fails startup in `staging`/`production` when `ALLOW_DEV_STATIC_JWT_SECRET=True` or `KEYCLOAK_JWKS_URL` is unset. Live Keycloak JWKS RS256 fetching is not yet wired (`NOT VERIFIED` / documented in `GAPS_AND_RISKS.md`).
- Test output:
```
$ python -m pytest tests/test_auth_security.py tests/test_production_hardening_security.py -v
16 passed in 0.89s
```
- **Status:** `VERIFIED` (HS256/iss/aud/alg/unsigned/startup-guard tests), `BLOCKED` (`gitleaks` on host), `NOT VERIFIED` (live Keycloak JWKS).
