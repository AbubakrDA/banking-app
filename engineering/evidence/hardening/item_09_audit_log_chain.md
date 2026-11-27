# Item 9 Plan — Chained SHA-256 Audit Log Integrity

## Plan
- Add `prev_hash` and `hash_timestamp` columns to `AuditLog` (`backend/app/models/enterprise.py`) via migration `014_audit_log_hash_chain.py`.
- Chain `record_audit_event` in `EnterpriseAdminService` to previous tenant `event_hash` (genesis `"0" * 64`) ordered by `hash_timestamp`.
- Add `GET /api/v1/enterprise/audit-logs/verify` (`owner`/`admin`) and tamper-detection test in `backend/tests/test_enterprise_admin.py`.

## Evidence
```
$ python -m pytest tests/test_enterprise_admin.py -v
7 passed in 0.97s
```
- **Status:** `VERIFIED`
