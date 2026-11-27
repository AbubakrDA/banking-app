# BankingAIPlatform

**Enterprise AI Customer Support & Business Intelligence Platform**

BankingAIPlatform is an intelligent, secure, multi-tenant customer-support and business-intelligence platform enabling organizations to automate customer support using AI agents, manage customer memory, integrate with business data hubs (Google Sheets, databases, CRM/ERP), and generate actionable management intelligence.

---

## Architecture Overview

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Recharts
- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic
- **Database & Storage:** PostgreSQL 16 with pgvector, Redis 7, MinIO / S3 object storage
- **Background Processing:** Celery with Redis broker
- **Authentication:** Keycloak OIDC with RBAC & multi-tenant row-level security
- **AI & RAG:** Controlled Agent Orchestration, pgvector vector indexing, vision models, OCR
- **Integrations:** Tool Gateway with MCP proxy & Google Sheets API connectors

---

## Engineering Control: Harness Engineering

BankingAIPlatform strictly follows the **Harness Engineering** methodology.
Every task proceeds under the mandatory protocol:
`READ` → `PLAN` → `IMPLEMENT` → `TEST` → `INSPECT` → `REPAIR` → `RETEST` → `REPORT`

See [engineering/harness/README.md](file:///D:/BANKING_AI_PLATFORM/engineering/harness/README.md) for full protocol specifications.

---

## Documentation Index

- [PROJECT_AUDIT.md](file:///D:/BANKING_AI_PLATFORM/PROJECT_AUDIT.md) — Baseline workspace audit
- [TARGET_ARCHITECTURE.md](file:///D:/BANKING_AI_PLATFORM/TARGET_ARCHITECTURE.md) — Target system architecture
- [PHASE_ROADMAP.md](file:///D:/BANKING_AI_PLATFORM/PHASE_ROADMAP.md) — 16-phase implementation roadmap
- [SECURITY_ASSESSMENT.md](file:///D:/BANKING_AI_PLATFORM/SECURITY_ASSESSMENT.md) — Security threat model and controls
- [HARNESS_IMPLEMENTATION_PLAN.md](file:///D:/BANKING_AI_PLATFORM/HARNESS_IMPLEMENTATION_PLAN.md) — Harness design
- [PHASE_0_COMPLETION_REPORT.md](file:///D:/BANKING_AI_PLATFORM/PHASE_0_COMPLETION_REPORT.md) — Phase 0 sign-off

---

## Requirements & Verification

- **Python:** `>=3.12` (managed via `uv`)
- **Node.js:** `>=20` (`22` LTS used in CI)

### Backend
```bash
cd backend
uv sync --extra dev
uv run pytest -q --cov=app --cov-fail-under=74
```

### Frontend
```bash
cd frontend
npm ci
npm run lint && npx tsc --noEmit && npm test && npm run build
```

### Current Verification Boundaries
- **Backend tests:** Verified with SQLite in-memory async test harness (`240+` tests, `74%` coverage). Live PostgreSQL 16 RLS (`tests/test_rls_postgres_integration.py`) requires `POSTGRES_TEST_URL` and is run in CI (`.github/workflows/ci-security-and-tests.yml`).
- **Authentication:** HS256 JWT (`alg`, `typ`, `iss`, `aud`) is active in dev/test (`ALLOW_DEV_STATIC_JWT_SECRET=True`, forbidden in staging/production). Live Keycloak OIDC JWKS validation is **Partial / Not yet connected**.
- **Malware scanning:** `ClamAVScanner` (`INSTREAM`) fails closed to quarantine when `CLAMAV_ENABLED=true` and `clamd` is unreachable; heuristic full-payload pre-filter is active by default.
- **Frontend:** UI shell pages currently render demo/mock data; `apiClient.ts` foundation is in place (`Partial`).
