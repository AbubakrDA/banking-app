# Phase 9 Specification — Complaints, Tickets & Feedback

**Objective:** Implement enterprise ticket management, 8-stage lifecycle state machine, automated category/priority classification, duplicate detection, SLA due-date calculation, internal audit notes, multi-channel feedback collection (WhatsApp, Email, Web), and CSAT reporting.

## 1. Scope
- **8-Stage Ticket Lifecycle State Machine (Spec §4F):**
  - Valid transitions: `new` → `categorized` → `assigned` → `in_progress` → `waiting_customer` → `escalated` → `resolved` → `closed`.
  - Enforced transition invariants and status-change audit logging.
- **Priority & SLA Calculation:**
  - Priorities: `urgent` (2h SLA), `high` (8h SLA), `medium` (24h SLA), `low` (72h SLA).
  - Automated classification based on issue severity and sentiment.
- **Duplicate Ticket Detection:**
  - Prevents spam or duplicate submissions from the same customer within 24 hours.
- **Internal Notes & Audit Trail:**
  - Role-protected internal agent notes vs. customer-facing communication notes.
  - Complete history of state changes, assignments, and escalations.
- **Multi-Channel Customer Feedback (Spec §4G):**
  - Generates secure, expiring feedback tokens for WhatsApp and Email links.
  - Submits 1-5 star CSAT rating, resolution confirmation (`was_resolved`), and feedback commentary.
- **Strict Multi-Tenancy:**
  - Complete isolation across all ticket queries, note creation, and feedback submissions.

## 2. Acceptance Criteria
- [ ] Tickets transition through approved lifecycle stages and log audit notes.
- [ ] SLA due dates are calculated automatically based on ticket priority.
- [ ] Duplicate submissions within 24 hours for the same customer are flagged/prevented.
- [ ] Internal notes are tracked with actor identification.
- [ ] Feedback tokens allow secure one-time rating submission and record CSAT scores.
- [ ] Multi-tenant isolation is strictly preserved (0% cross-tenant ticket leakage).
- [ ] 100% of automated tests pass without errors.
