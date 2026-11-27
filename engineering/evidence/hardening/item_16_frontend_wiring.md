# Item 16 Plan & Evidence — Frontend API Wiring & Demo Data Labeling

## Plan
- Audit `frontend/src/pages/*.tsx` for API calls (`Select-String` confirmed 0 pages call backend endpoints yet).
- Add `frontend/src/services/apiClient.ts` (`apiFetch`, `checkBackendHealth`, in-memory token support).
- Wire `AppShell.tsx` to probe `/api/v1/health` and display a clear `Demo Data` status banner across all module pages.

## Evidence
- `npm run lint`, `npx tsc --noEmit`, and `npm test` executed below.
- `npm run lint` -> exited 0
- `npx tsc --noEmit` -> exited 0
- `npm test` -> `Test Files 1 passed (1)`, `Tests 8 passed (8)` in `4.37s`
- **Status:** `PARTIALLY VERIFIED` (API health probe + Demo Data banner wired; 9 module pages remain demo-only).
