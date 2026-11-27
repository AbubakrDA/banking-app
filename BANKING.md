# Banking AI Platform

Forked from a customer-support and business-intelligence platform, adapted for banking.
This repo is a separate project. It is not a deployment of the original.

## Module mapping

| Original module | Banking use |
|---|---|
| Tenant isolation (RLS, JWT-only tenant context) | One tenant per bank |
| Tool gateway with risk tiers | Only path the AI uses for banking actions |
| Approval gate (self-approval blocked) | Human approval for high-risk transfers |
| Chained audit log and /verify | Tamper-evident audit trail |
| RBAC route matrix | Customer, employee, risk officer, admin |
| Business data hub | Accounts, balances, transactions (mock API first) |
| Knowledge base / RAG | Bank policy documents, cited answers |
| NLP and chat | Arabic/English banking chatbot |
| Tickets and feedback | Customer service cases |
| Analytics and admin | Risk and admin dashboards |

## Status

- Renamed from the original project. Code structure unchanged.
- Not yet removed: support-specific modules, Google Sheets and MCP connectors. Remove only after tests run.
- Inherited, unverified: Postgres RLS against a live database, Keycloak JWKS validation, ClamAV scanning (heuristic only unless clamd runs).
