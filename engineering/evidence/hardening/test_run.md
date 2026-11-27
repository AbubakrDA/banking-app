# Item 8 Evidence — Measured Coverage Gate (`fail_under = 74`)

## Plan
- Measured baseline coverage on `origin/harden/production-readiness`: `74%` (`4008` statements, `1044` missed).
- Configure `[tool.coverage.report] fail_under = 74` in `backend/pyproject.toml`.
- Verify `python -m pytest -q --cov=app --cov-fail-under=74`.

## Evidence
```
$ python -m pytest -q --cov=app --cov-fail-under=74
TOTAL                                        4039   1044    74%
Required test coverage of 74% reached. Total coverage: 74.15%
240 passed, 1 skipped in 20.62s
```
- **Status:** `VERIFIED`
