# Phase 12 Specification — Tools, MCP & Workflow Automation

**Objective:** Implement the Governed Tool Gateway architecture (Master Spec §6, §13, and `GEMINI.md`): unified tool registry, JSON Schema generation, risk tier classification (`LOW`, `MEDIUM`, `HIGH`), human approval gate for HIGH-risk actions, input validation and output sanitization, Model Context Protocol (MCP) server integration, execution timeouts, rate limiting, and comprehensive audit logging.

## 1. Scope
- **Tool Gateway Architecture (Spec §6.1, `GEMINI.md`):**
  - Unified execution gateway at `/api/v1/tools/execute`.
  - Invariant: AI agents NEVER call databases or external systems directly; all tool executions MUST route through the Tool Gateway.
  - Parameter validation against tool Pydantic v2 schemas before execution.
  - Output sanitization: strips prompt injection tokens, credential leaks, and wraps result in untrusted data envelopes.
- **Built-in Governed Internal Tools (Spec §6.2):**
  - `lookup_order`: Queries order status, tracking, and items (LOW risk).
  - `check_availability`: Queries appointment or service calendar slots (LOW risk).
  - `query_catalog`: Searches products and service inventory (LOW risk).
  - `create_appointment`: Reserves service appointment slot (MEDIUM risk).
  - `cancel_order`: Cancels an active order (HIGH risk — requires human supervisor approval).
  - `process_refund`: Issues financial refund (HIGH risk — requires human supervisor approval).
- **Risk Classification & Human Approval Gate (Spec §6.4, §6.5):**
  - Risk Tiers: `LOW` (auto-approved read-only), `MEDIUM` (controlled reversible writes), `HIGH` (privileged financial/destructive actions).
  - High-risk tool calls are intercepted into `requires_approval` status.
  - Generates approval requests stored with execution payload.
  - Endpoints `/api/v1/tools/executions/{id}/approve` and `/reject` allow supervisors to review and resolve execution.
- **Model Context Protocol (MCP) Server Integration (Spec §6.8, §6.9):**
  - Model Context Protocol server configuration model (`MCPServerConfig`).
  - Supports registering MCP endpoints (HTTP/SSE/stdio), discovering advertised tools, and proxying invocations.
  - Output validation layer wrapping external MCP tool outputs in untrusted data envelopes.
- **Audit Logging & Telemetry (Spec §6.11):**
  - Logs every tool invocation: `tool_name`, `agent_type`, `tenant_id`, `caller_id`, `input_params` (redacting secrets), `risk_level`, `execution_status`, `duration_ms`, `approver_id`, and `output_summary`.
- **Strict Multi-Tenancy (Spec §7, §9):**
  - All tool executions, MCP server registrations, and approval requests are strictly isolated per tenant.

## 2. Acceptance Criteria
- [ ] Tool registry exposes available tools with JSON Schemas and risk classifications.
- [ ] LOW and MEDIUM risk tools execute automatically through `/api/v1/tools/execute`.
- [ ] HIGH risk tools halt execution and return `requires_approval` with an approval request ID.
- [ ] Authorized supervisor approval triggers execution; rejection halts execution without mutations.
- [ ] MCP server configuration registers external tools and wraps output in untrusted data envelopes.
- [ ] Comprehensive audit logs record every execution, duration, input, and approval metadata.
- [ ] Strict multi-tenant isolation is preserved (zero cross-tenant tool execution or data leaks).
- [ ] 100% of automated unit and integration tests pass.
