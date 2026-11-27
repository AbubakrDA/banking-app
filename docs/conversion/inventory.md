# Conversion Inventory — `AbubakrDA/banking-app`

Every file from the ConversaIQ fork is classified below as **keep**, **rewrite**, or **delete**.

## 1. Root Documentation
| Path | Decision | Rationale |
|---|---|---|
| `BANKING.md` | rewrite | Update to reflect converted banking architecture & module map (Phase F) |
| `README.md` | rewrite | Rewrite for banking product setup, env vars, tests, and status (Phase F) |
| `AGENTS.md`, `GEMINI.md` | keep | Security & engineering invariants |
| `PHASE_*_COMPLETION_REPORT.md` (all) | delete | Old ConversaIQ support-desk history (Phase A) |
| `PROJECT_AUDIT.md`, `GAPS_AND_RISKS.md`, `TARGET_ARCHITECTURE.md`, `HARNESS_IMPLEMENTATION_PLAN.md`, `EXISTING_FEATURES_INVENTORY.md`, `CURRENT_ARCHITECTURE.md`, `HARDENING_REPORT.md` | delete | Old ConversaIQ reports & architecture docs (Phase A) |
| `SECURITY_ASSESSMENT.md`, `PHASE_ROADMAP.md` | delete | Replaced by `docs/SECURITY.md` and `docs/decisions.md` (Phase A/F) |

## 2. Backend Core & Migrations (`backend/`)
| Path | Decision | Rationale |
|---|---|---|
| `backend/app/core/auth.py` | rewrite | Centralize banking roles (`customer`, `employee`, `risk_officer`, `admin`) + staff reason dependency |
| `backend/app/core/security.py` | keep | Strict HS256/iss/aud/alg/exp JWT validation & prod static-secret guard |
| `backend/app/core/config.py` | rewrite | Add banking env settings (transfer approval threshold, LLM stub) |
| `backend/app/core/database.py`, `middleware.py`, `logging.py` | keep | Async SQLAlchemy, RLS ContextVar, request ID & security headers |
| `backend/alembic/versions/001`–`014` | keep | Existing migrations never edited |
| `backend/alembic/versions/015_drop_support_desk_tables.py` | add | Drop removed support-desk tables (Phase A) |
| `backend/alembic/versions/016_banking_domain_tables.py` | add | Add banking tables: `bank_accounts`, `bank_transactions`, `bank_transfers`, `bank_cards`, `risk_alerts`, `policy_documents`, `policy_chunks` (Phase B) |

## 3. Backend Domain Modules (`backend/app/`)
| Path | Decision | Rationale |
|---|---|---|
| `models/ticket.py`, `models/nlp.py`, `models/business.py` | delete | Support-desk models removed (Phase A) |
| `schemas/ticket.py`, `schemas/nlp.py`, `schemas/business.py` | delete | Support-desk schemas removed (Phase A) |
| `api/v1/endpoints/tickets.py`, `nlp.py`, `business_data.py` | delete | Support-desk endpoints removed (Phase A) |
| `services/ticket/`, `services/nlp/`, `services/connectors/`, `services/data_quality.py` | delete | Support-desk & Google Sheets/CSV connectors removed (Phase A) |
| `models/banking.py`, `schemas/banking.py`, `services/banking/` | add | Banking domain models, `BankingAPI` protocol, seeded `MockBankingAPI`, ownership & audit helpers (Phase B) |
| `api/v1/endpoints/{accounts,transactions,transfers,cards,customers,risk,approvals,policies,audit,admin,chat}.py` | rewrite / add | Banking v1 routes with RBAC, ownership, reason-required staff access, and audit logging (Phase C) |
| `services/ai/{language,intent,provider,guardrails,retrieval,agent}.py` | rewrite / add | Bilingual AR/EN/mixed chatbot, rule-based intents, `LLMProvider` stub, approved-only policy RAG with citations & abstention, AR/EN prompt guard (Phase D) |
| `services/document/scanner.py`, `services/enterprise/admin.py`, `services/tools/gateway.py` | keep / rewrite | Keep ClamAV scanner & chained SHA-256 audit log; rewrite tool gateway for banking tools only |

## 4. Backend Tests (`backend/tests/`)
| Path | Decision | Rationale |
|---|---|---|
| `test_tickets_feedback.py`, `test_question_intelligence.py`, `test_business_data_hub.py`, `test_performance_and_load.py` | delete | Tests for removed support-desk modules (Phase A) |
| `test_auth_security.py`, `test_api_error_envelopes.py`, `test_rls_postgres_integration.py`, `test_document_intelligence.py` | keep / update | Core security & RLS tests |
| `test_banking_domain.py`, `test_banking_rbac_matrix.py`, `test_banking_ai.py`, `test_audit_chain.py` | add | All required banking, RBAC, transfer, approval, policy RAG, AR/EN injection & audit tests |

## 5. Frontend (`frontend/src/`)
| Path | Decision | Rationale |
|---|---|---|
| `pages/BusinessDataHubPage.tsx`, `ComplaintsTicketsPage.tsx`, `IntegrationsToolsPage.tsx` | delete | Old support-desk pages removed (Phase A) |
| `pages/{CustomerDashboardPage,EmployeeDashboardPage,AdminRiskDashboardPage,MainDashboardPage}.tsx` | rewrite / add | Role-based banking dashboards with AR/EN i18n, RTL support, loading/empty/error states (Phase E) |
| `services/apiClient.ts`, `i18n/` | keep / add | In-memory token client + Arabic/English translations (Phase E) |
