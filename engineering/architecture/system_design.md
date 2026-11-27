# System Design — BankingAIPlatform Architecture Reference

This document encapsulates the canonical modular monolith architecture for BankingAIPlatform as established in [TARGET_ARCHITECTURE.md](file:///D:/BANKING_AI_PLATFORM/TARGET_ARCHITECTURE.md).

## Core Modules & Responsibilities

- **Module A (AI Customer Support):** Conversational AI chat, WebSocket streaming, human escalation and handover.
- **Module B (Customer File Upload & Document Intelligence):** Uploads, magic byte validation, ClamAV quarantine, OCR, image understanding.
- **Module C (Customer Memory):** Working, episodic, and semantic memory with provenance and privacy controls.
- **Module D (Knowledge Base & RAG):** Document parsing, chunking, embeddings, pgvector hybrid search, citation tracking.
- **Module E (Business Data Hub):** Google Sheets API sync, CSV/Excel imports, internal CRUD tables, CRM/ERP connectors.
- **Module F (Complaints & Ticket Management):** Formal ticket lifecycle (New -> Closed), SLA tracking, notes.
- **Module G (Customer Feedback):** WhatsApp and Email delivery, CSAT surveys, secure tokens.
- **Module H (NLP & Question Intelligence):** Semantic clustering of customer inquiries, intent classification, knowledge gap detection.
- **Module I (Admin Intelligence):** Executive dashboards, Recharts analytics, AI Insights, Analytics Copilot.
- **Module J (Enterprise Administration):** Multi-tenant organization settings, RBAC, Security Center, audit logging.

## Technology Stack Specifications

- **Frontend:** React 18, Vite, TypeScript 5, Tailwind CSS, Lucide icons, Recharts.
- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 (async), Celery.
- **Storage:** PostgreSQL 16 with pgvector, Redis 7, MinIO / S3.
- **Security:** Keycloak OIDC, Gitleaks, Bandit, Semgrep, Trivy, Playwright.
