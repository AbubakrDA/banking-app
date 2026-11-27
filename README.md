# ConversaBank — Intelligent Banking AI Layer

An AI-powered Intelligent Banking Layer that sits on top of a bank's existing core systems without replacing them:

```
Customer / Employee → Banking AI Layer → Bank APIs → Core Banking Systems
```

## Repository Structure

- `backend/` — FastAPI + SQLAlchemy async API, RBAC, surface isolation (`customer`, `staff`, `both`), maker-checker approvals, tamper-evident hash-chained audit log, bilingual AI layer (Arabic, English, mixed), and bank-selectable integration registry.
- `apps/customer/` — Customer web and Capacitor-ready mobile app (biometric/PIN background lock, privacy shield, idempotent transfers, card controls, bilingual AI chat).
- `apps/staff/` — Separate staff operations build with its own login, 10-minute idle timeout, written-reason customer search, risk/approvals/audit consoles, and department-restricted (`hr`, `marketing`) views.
- `packages/shared/` — Shared TypeScript types, in-memory token `apiClient`, and EN/AR translations (contains no screens).
- `docs/` — Security posture ([SECURITY.md](file:///D:/banking-app/banking-app/docs/SECURITY.md)), architectural decisions ([decisions.md](file:///D:/banking-app/banking-app/docs/decisions.md)), department requirements ([requirements.md](file:///D:/banking-app/banking-app/docs/requirements.md)), integrations ([integrations.md](file:///D:/banking-app/banking-app/docs/integrations.md)), and compliance ([cbos.md](file:///D:/banking-app/banking-app/docs/compliance/cbos.md)).

## Running Tests Locally

### Backend
```powershell
cd backend
python -m pytest -q
```

### Frontend (`apps/customer` & `apps/staff`)
```powershell
npm.cmd install
npm.cmd run typecheck
npm.cmd test
npm.cmd run build
```
