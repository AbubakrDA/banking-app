# Banking Domain Architecture & Module Mapping

## Core Modules

| Module | Surface | Purpose |
|---|---|---|
| `accounts` | `both` | Masked account list and balances in integer minor units |
| `transactions` | `both` | Paginated history with date and minor-unit amount filters |
| `transfers` | `customer` (create), `both` (list) | Validated transfers with `Idempotency-Key`, cross-border flag, and high-risk approval routing |
| `cards` | `customer` (status update), `both` (list) | Masked card status, customer block/unblock (audited) |
| `customers` | `customer` (`/me`), `staff` (`/search`) | Masked profile; staff search requires written `X-Access-Reason` |
| `risk` | `staff` | Risk alerts and case queue (`risk_officer`, `admin`) |
| `approvals` | `staff` | Pending high-risk transfers; approve/reject (`admin`, self-approval blocked) |
| `policies` | `both` (list), `staff` (upload/review) | Policy PDFs; only `approved` policies feed AI retrieval |
| `audit` | `staff` | Tamper-evident hash-chained audit log and `/verify` |
| `admin` | `staff` | User and non-secret banking configuration views |
| `integrations` | `staff` / `both` | Bank-selectable `MobileMoneyProvider` & `AgentNetworkProvider` (off by default) |
| `chat` | `both` | Bilingual AR/EN/mixed chatbot routed through `BankingToolGateway` |
