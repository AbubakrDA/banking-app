# Banking AI Platform Requirements & Status

## Customer & Mobile Requirements

| ID | Requirement | Status | Verification |
|---|---|---|---|
| `C3` | Domestic & own-account transfers with limits; cross-border off by default | `Built` | `test_req_C3_domestic_payments_limits_and_cross_border_off` |
| `C4` | Card status, block and unblock (customer action, audited) | `Built` | `test_req_C4_cards_block_unblock_audited` |
| `C6` | Pluggable MFA hook (`MFAProvider`) for login and high-risk actions | `Built` | `test_req_C6_mfa_hook_login_and_high_risk_actions` |
| `C8` | Mobile idempotency key on transfers (retried request creates no second transfer) | `Built` | `test_req_C8_mobile_transfer_idempotency_key` |
| `C8-Bio` | Native OS biometric / secure-enclave plugin binding (Capacitor) | `Partial` | Web/Capacitor privacy shield & `visibilitychange` lock verified in `CustomerApp.test.tsx`; native OS biometric plugin requires device build |
| `I18N` | Arabic and English on every screen with RTL layout in Arabic | `Built` | `CustomerApp.test.tsx` (`toggles Arabic RTL direction on language switch`), `packages/shared/src/translations.ts` |

## Department & Staff Access Requirements (`S1–S15`)

| ID | Role / Scope | Surface | Accounts / Transactions | Transfers / Cards | Risk / Approvals / Audit | Policies | Status | Verification |
|---|---|---|---|---|---|---|---|---|
| `S1–S3` | `employee` (Branch / Service) | `staff` | All with `X-Override-Reason` | List with reason; cannot initiate | Denied (`403`) | List & upload | `Built` | `test_req_S1_to_S15_department_isolation_and_staff_timeout`, `test_ownership.py` |
| `S4–S6` | `risk_officer` (Risk & Sanctions) | `staff` | All with `X-Override-Reason` | Read-only; cannot move money | Full read & alert triage | List | `Built` | `test_banking_rbac_matrix.py`, `test_ownership.py` |
| `S7–S10` | `admin` (Operations / Admin) | `staff` | All with `X-Override-Reason` | List with reason; cannot initiate | Approve/reject (self-approval blocked) | List, upload, approve/reject | `Built` | `test_banking_rbac_matrix.py` |
| `S11–S13` | `hr` (Human Resources) | `staff` | Denied (`403`) | Denied (`403`) | Denied (`403`) | Read-only | `Built` | `test_req_S1_to_S15_department_isolation_and_staff_timeout`, `StaffApp.test.tsx` |
| `S14–S15` | `marketing` (Marketing) | `staff` | Denied (`403`) | Denied (`403`) | Denied (`403`) | Read-only | `Built` | `test_req_S1_to_S15_department_isolation_and_staff_timeout` |
| `S-Timeout` | Staff 10-minute configurable idle timeout | `staff` | — | — | — | — | `Built` | `test_req_S1_to_S15_department_isolation_and_staff_timeout`, `apps/staff/src/App.tsx` |
