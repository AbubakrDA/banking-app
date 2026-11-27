# Verification Protocol

BankingAIPlatform requires layered automated verification for all code changes.

## Verification Tiers

1. **Static Analysis & Type Checking:**
   - Backend: `mypy --strict`, `ruff check`
   - Frontend: `tsc --noEmit`, `eslint`

2. **Unit Testing:**
   - Backend: `pytest tests/unit/`
   - Frontend: `npm test` (Vitest)

3. **Integration & API Testing:**
   - Endpoint status, response envelopes, pagination, error schemas: `pytest tests/integration/`
   - Tenant isolation verification: verifying that Tenant A cannot query Tenant B's data under any condition.

4. **Security Testing:**
   - Secrets scanning: `gitleaks detect --source . -v`
   - Python security linter: `bandit -r backend/`
   - AST security scanning: `semgrep --config auto`

5. **End-to-End & Browser Testing:**
   - Playwright test suites executing customer and agent workflows: `npx playwright test`
