# Item 11 Plan & Evidence — CI/CD Pipeline

## Plan
- Add `.github/workflows/ci-security-and-tests.yml` with:
  - Backend: `ruff check app`, `mypy app/services/`, `pytest --cov=app --cov-fail-under=74`, PostgreSQL 16 service (`POSTGRES_TEST_URL` for live RLS).
  - Frontend: `npm ci`, `npm run lint`, `npx tsc --noEmit`, `npm test`, `npm run build`, `npm audit --omit=dev --audit-level=high`.
  - Security: `gitleaks`, `bandit`, `semgrep`, `pip-audit`, `trivy`.
- Validate YAML syntax and check `actionlint`.

## Evidence
- `python -c "import yaml; yaml.safe_load(...)"` -> `YAML_OK`
- `where.exe actionlint` -> `actionlint_not_installed` (`BLOCKED` locally; `gitleaks`, `bandit`, `semgrep`, `trivy`, `pip-audit` also absent on host and configured for GitHub Actions).
- **Status:** `PARTIALLY VERIFIED` (YAML validated; GitHub Actions runner pending).
