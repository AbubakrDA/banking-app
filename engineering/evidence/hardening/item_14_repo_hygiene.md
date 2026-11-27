# Item 14 Plan & Evidence — Repository Hygiene

## Plan
- Audit `backend/app/` for synthetic test fixtures and tracked `storage_data/` artifacts.
- Remove tracked `backend/app/storage_data/` test PDFs from Git index (`git rm -r --cached`) while keeping `backend/app/storage_data/` ignored in `.gitignore`.

## Evidence
- Found 88 synthetic test PDFs tracked under `backend/app/storage_data/tenants/` (`exploit_spec.pdf`, `receipt.pdf`, `passwd.pdf`, `service_invoice.pdf`).
- Untracked `backend/app/storage_data` from Git index and updated `.gitignore` with `*.db`, `*.sqlite*`, `tb.txt`.
- **Status:** `VERIFIED`
