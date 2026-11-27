# Phase 4 Specification — Business Setup & Data Hub

**Objective:** Implement organization business model onboarding (Products, Services, Hybrid), the built-in Business Data Manager, Google Sheets OAuth connector, CSV/Excel ingestion, and the automated data quality validation engine.

## 1. Scope
- **Business Model Configuration (Spec §3):**
  - Tenant onboarding and runtime toggle: `products`, `services`, `hybrid`.
  - Configurable custom fields for industry-specific data structures.
- **Built-in Business Data Management:**
  - Products catalog (SKU, brand, category, price, discount, stock, specifications, supplier).
  - Services catalog (durations, pricing, staff allocation, availability, policies).
  - Orders tracking (order number, line items, total amount, status, delivery).
  - Service Appointments (customer, service, staff provider, time window, status).
- **Business Data Hub Connectors (Spec §4 Module E):**
  - Google Sheets API: OAuth2 authorization, sheet selection, column mapping, read-only sync, connection revocation.
  - CSV & Excel: Multipart file upload, schema inference, preview mapping, import validation.
- **Data Quality Engine:**
  - Automated detection of: missing values, duplicate SKUs/emails, invalid prices, inconsistent dates, invalid phone numbers.
  - Health score computation (0-100%) and structured quality reports.
- **Architectural Isolation Invariant:** External data sources synchronize into BankingAIPlatform internal tables but never replace PostgreSQL as the primary operational database.

## 2. Acceptance Criteria
- [ ] Business model can be configured to `products`, `services`, or `hybrid` and updated via API.
- [ ] Product, Service, Order, and Appointment models support full CRUD operations strictly scoped to `tenant_id`.
- [ ] CSV/Excel files are parsed with schema detection and column mapping validation.
- [ ] Data quality engine accurately detects negative prices, duplicate keys, and missing fields.
- [ ] Sync history records timestamps, records processed, and data quality issues.
- [ ] All tests execute and pass with zero failures.
