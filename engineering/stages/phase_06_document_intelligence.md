# Phase 6 Specification — Customer File Upload & Document Intelligence

**Objective:** Implement secure multi-tenant customer file uploads, magic-byte format validation, ClamAV/EICAR anti-malware scanning with quarantine isolation, tenant-partitioned object storage (MinIO/S3), text extraction & OCR, anti-prompt injection envelope sanitization for documents, and presigned authorized downloads.

## 1. Scope
- **File Ingestion & Boundary Controls (Spec §4B, §13):**
  - Supported formats: PDF, PNG, JPG, JPEG, WebP.
  - Validation: Magic byte inspection (not relying on caller MIME header or file extension alone).
  - Path Traversal Defense: Strict filename normalization and rejection of directory traversal sequences (`..`, `/`, `\`).
  - File size limits: Enforced quota (default 10 MB per file, configurable).
- **Anti-Malware & Quarantine Pipeline:**
  - Ingestion scanner for virus/malware signatures (EICAR standard, dangerous executable headers `MZ`/`ELF`, embedded script vectors).
  - Automatic quarantine routing: flagged files isolated, marked `is_quarantined=True`, status set to `quarantined`, and blocked from standard downloads.
- **Tenant-Isolated Storage (MinIO / S3):**
  - Tenant path partitioning: `{tenant_id}/documents/{document_id}/{sanitized_filename}`.
  - Zero cross-tenant storage access: Enforced tenant check on every read, write, signed URL generation, and deletion.
- **Document Intelligence & Anti-Prompt-Injection (Spec §7, GEMINI.md):**
  - Text extraction from documents.
  - Anti-prompt-injection defense: Document contents wrapped in `<document_content_untrusted>` data envelopes.
  - Scanner for embedded instruction overrides and adversarial jailbreaks inside document text.
- **Authorized Access & Delivery:**
  - Presigned expiring download URLs with tenant authorization check.
  - Document metadata and status tracking (`uploaded` → `scanning` → `processing` → `ready` / `quarantined` / `error`).

## 2. Acceptance Criteria
- [ ] Uploaded files are verified via magic bytes; forged extensions are rejected.
- [ ] Directory traversal attempts in file names are completely neutralized.
- [ ] Malware/EICAR payloads are quarantined and cannot be downloaded or processed.
- [ ] Extracted text is wrapped in untrusted data envelopes and scanned for prompt injection.
- [ ] Strict multi-tenant isolation ensures Tenant A cannot view, download, or delete Tenant B's files.
- [ ] 100% of automated tests pass cleanly with zero errors.
