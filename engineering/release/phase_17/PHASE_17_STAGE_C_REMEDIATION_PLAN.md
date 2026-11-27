# Phase 17 — Stage C: Remediation Plan

## 1. Executive Summary
In compliance with Section 15 of the Phase 17 instructions, this document presents the prioritized remediation proposals derived from the Stage B Deep Technical Audit.

**Guiding Invariant:** All proposed fixes are non-disruptive code hygiene, warning elimination, and test resource cleanups designed to ensure 100% warning-free, zero-defect quality before staging deployment. **No fixes will be implemented until you explicitly review and approve this plan.**

---

## 2. Proposed Remediation Items

### Item 1: Frontend Router Fast-Refresh Separation
- **Objective:** Eliminate the 3 `react-refresh/only-export-components` ESLint warnings in the frontend router to achieve a 100% warning-free frontend codebase.
- **Scope:**
  - Create `frontend/src/router/hooks.ts` containing `useRouter`, `useLocation`, and `useNavigate`.
  - Re-export the hooks from `frontend/src/router/index.tsx` so existing imports remain 100% backwards compatible.
- **Affected Files:**
  - `frontend/src/router/hooks.ts` (New file)
  - `frontend/src/router/index.tsx` (Modified)
- **Risk Assessment:** `Zero Risk`. Purely architectural separation of React hooks from component definitions.
- **Verification Requirement:**
  - `npm run lint` must exit with `0 errors, 0 warnings`.
  - `npm test -- --run` must pass all 8 Vitest tests.
  - `npm run build` must compile cleanly in `dist/`.

---

### Item 2: Backend Test Fixture Resource Cleanup
- **Objective:** Eliminate 5 `ResourceWarning: unclosed file` warnings reported during pytest test execution.
- **Scope:**
  - In `backend/tests/test_cloud_infrastructure.py`, replace bare `open(path).read()` calls with standard `with open(path, "r", encoding="utf-8") as f: content = f.read()` context managers.
- **Affected Files:**
  - `backend/tests/test_cloud_infrastructure.py` (Modified lines 85–105)
- **Risk Assessment:** `Zero Risk`. Standard Python I/O resource management pattern.
- **Verification Requirement:**
  - `python -m pytest tests/test_cloud_infrastructure.py -W default` must complete with 0 warnings.

---

### Item 3: SQLAlchemy Boolean Filter Polish
- **Objective:** Adhere to strict SQLAlchemy and PEP 8 best practices for Boolean column comparisons.
- **Scope:**
  - In `backend/app/api/v1/endpoints/memory.py` and `backend/app/api/v1/endpoints/nlp.py`, replace `Column == True` with `Column.is_(True)`.
- **Affected Files:**
  - `backend/app/api/v1/endpoints/memory.py` (Lines 95, 130)
  - `backend/app/api/v1/endpoints/nlp.py` (Line 86)
- **Risk Assessment:** `Zero Risk`. SQLAlchemy translates `.is_(True)` to identical SQL `IS TRUE` or `= 1` clauses.
- **Verification Requirement:**
  - Full backend test suite `python -m pytest tests/ -v` must maintain 98 / 98 passing tests.

---

### Item 4: Automated Staging Pre-Flight Verification Script
- **Objective:** Provide an automated, deterministic pre-flight check script for Stage E (Staging Readiness) to validate AWS IAM credentials, database connectivity, and required environment variables before cloud provisioning.
- **Scope:**
  - Implement `scripts/staging_readiness_check.py` to verify environment parameters (`ENVIRONMENT`, `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `S3_BUCKET_NAME`) and report ready/missing configurations without leaking secret values.
- **Affected Files:**
  - `scripts/staging_readiness_check.py` (New file)
- **Risk Assessment:** `Zero Risk`. Non-invasive CLI tool that runs in read-only diagnostic mode.
- **Verification Requirement:**
  - `python scripts/staging_readiness_check.py` executes and outputs formatted diagnostic checklist.

---

## 3. Approval Gate & Next Actions
Upon your explicit approval of this Remediation Plan:
1. **Stage D (Approved Remediation):** Implement Items 1, 2, 3, and 4. Re-run all 98 backend tests and 8 frontend tests to verify 0 errors and 0 warnings.
2. **Stage E (Staging Readiness):** Prepare staging deployment checklists and procedures.
3. Pause at the Stage E gate for your staging deployment authorization.
