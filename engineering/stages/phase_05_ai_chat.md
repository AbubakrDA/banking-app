# Phase 5 Specification — Customer Support AI Chat

**Objective:** Implement the conversational AI chat system, multi-turn session persistence, the controlled Customer Support AI Agent, prompt injection defense guardrails, intent/sentiment detection, and human handover protocol.

## 1. Scope
- **Multi-Turn Chat State Management:**
  - Conversations state machine: `active` → `escalated` → `resolved` → `closed`.
  - Message stream persistence with sender types: `customer`, `ai_agent`, `human_agent`, `system`.
  - Source citations tracking (`sources` JSON payload).
- **5-Layer Prompt Injection Defense (Spec §7, GEMINI.md):**
  - Layer 1: Input validation & injection heuristic filtering (overriding instruction attempts, jailbreak syntax).
  - Layer 2: Strict role isolation (user input encapsulated in untrusted data envelope, never in system instructions).
  - Layer 3: Output filtering (PII / system prompt leak detection).
  - Layer 4: Tool approval gate hook.
  - Layer 5: Audit logging of flagged interactions.
- **Intent Detection & Sentiment Analysis:**
  - Automated intent classification (`product_inquiry`, `reschedule_appointment`, `order_status`, `complaint`, `general_faq`).
  - Sentiment scoring (`positive`, `neutral`, `frustrated`).
- **Controlled Customer Support AI Agent Runtime (Spec §5):**
  - Grounded responses citing authorized business data (Products, Services, Calendars).
  - Configurable tenant instructions and business policies.
  - Automatic escalation triggers when customer frustration is elevated or high-risk actions are detected.
- **Human Handover Protocol:**
  - Explicit handover endpoints with summary handoff and agent assignment.

## 2. Acceptance Criteria
- [ ] Adversarial prompt injection attacks are intercepted and rejected with security flags.
- [ ] Multi-turn messages are persisted with proper customer and tenant scoping.
- [ ] AI responses include grounded source citations and refuse hallucinated data.
- [ ] Customer sentiment is accurately scored and high frustration triggers escalation.
- [ ] Human handover preserves conversation summary and notifies available agents.
- [ ] All tests execute and pass with zero failures.
