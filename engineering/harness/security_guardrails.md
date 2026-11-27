# Security Guardrails

BankingAIPlatform is a multi-tenant platform handling confidential business data and documents. These security guardrails are non-negotiable.

## 1. Multi-Tenant Isolation
- Every database entity must include an indexed `tenant_id` foreign key.
- All database queries must enforce tenant scoping via PostgreSQL Row-Level Security (RLS) or typed repository wrappers.
- Object storage keys must follow `tenants/{tenant_id}/...`. Direct object access without signed tokens is prohibited.

## 2. File Upload & Processing Safety
- File types must be verified by magic-byte inspection (not just HTTP MIME type or file extension).
- Files must be quarantined upon upload and scanned for malware prior to text extraction or public exposure.
- Extracted text and OCR results must be treated as untrusted text envelopes to protect against prompt injection.

## 3. AI & Tool Execution Security
- AI agents must never be granted arbitrary SQL execution capabilities or direct shell access.
- All actions must be mediated by the Tool Gateway with typed Pydantic validation.
- High-risk actions (modifying critical business data, deleting assets) require explicit human confirmation.

## 4. Secrets & Authentication
- Secrets and API keys must never be committed to git or exposed in client bundles or log files.
- All API routes except public health checks and OAuth callbacks require valid Keycloak JWT bearer tokens.
