# Item 12 Plan & Evidence — Dependencies & Lockfiles

## Plan
- Verify `frontend/package-lock.json`, `backend/uv.lock`, and `backend/requirements.txt` are present and current.
- Fix missing extras in `backend/pyproject.toml` (`sqlalchemy[asyncio]`, `pydantic[email]`) so `uv sync --extra dev && uv run pytest` runs cleanly.
- Audit unused packages and run `npm audit --omit=dev --audit-level=high`.

## Evidence
- `backend/pyproject.toml` updated (`pydantic[email]>=2.10.0`, `sqlalchemy[asyncio]>=2.0.36`) and `uv.lock` regenerated via `uv lock`.
- `uv sync --extra dev && uv run pytest tests/test_health.py -v` -> `3 passed in 0.53s`.
- `frontend/package.json` has 5 production dependencies (`clsx`, `lucide-react`, `react`, `react-dom`, `tailwind-merge`); `npm audit --omit=dev --audit-level=high` -> `found 0 vulnerabilities`.
- `pip-audit`: `BLOCKED` on host (configured in CI).
- **Status:** `VERIFIED` (lockfiles, `uv run pytest`, frontend prod audit), `BLOCKED` (local `pip-audit`).
