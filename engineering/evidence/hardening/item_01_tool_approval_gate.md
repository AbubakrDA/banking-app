# Item 1 Plan — Tool Approval Gate Role & Self-Approval Hardening

## Plan
- **Change:** Enforce `require_roles(["owner", "admin"])` on `/tools/executions/{id}/approve` and `/reject`, add `requested_by_user_id` & `requested_by_role` to `ToolExecution` (with Alembic migration `012`), and reject self-approval/self-rejection with HTTP 403 (`SELF_APPROVAL_FORBIDDEN`).
- **Files:** `backend/app/models/tool.py`, `backend/alembic/versions/012_tool_requester_tracking.py`, `backend/app/schemas/tool.py`, `backend/app/services/tools/gateway.py`, `backend/app/api/v1/endpoints/tools.py`, `backend/tests/test_tools_mcp_gateway.py`.
- **Tests:** Add `test_non_admin_cannot_approve_or_reject_tool` and `test_self_approval_rejected_with_403`.
- **Risk:** Low; new columns are nullable for backward compatibility with existing rows.

## Execution & Evidence
- Fixed `require_roles` in `backend/app/core/auth.py` to inject `Depends(get_current_user)` and support both variadic and sequence role arguments.
- Enforced `require_roles(["owner", "admin"])` on `/api/v1/tools/executions/{execution_id}/approve` and `/reject`.
- Added `requested_by_user_id` & `requested_by_role` to `ToolExecution` (migration `012_tool_requester_tracking.py`), rejected self-approval/self-rejection with HTTP 403 (`SELF_APPROVAL_FORBIDDEN`).

```
tests/test_tools_mcp_gateway.py::test_tool_registry_discovery PASSED     [ 12%]
tests/test_tools_mcp_gateway.py::test_low_risk_tool_execution PASSED     [ 25%]
tests/test_tools_mcp_gateway.py::test_high_risk_human_approval_gate PASSED [ 37%]
tests/test_tools_mcp_gateway.py::test_high_risk_rejection_flow PASSED    [ 50%]
tests/test_tools_mcp_gateway.py::test_mcp_server_registration_and_discovery PASSED [ 62%]
tests/test_tools_mcp_gateway.py::test_strict_multi_tenant_isolation_tools PASSED [ 75%]
tests/test_tools_mcp_gateway.py::test_non_admin_cannot_approve_or_reject_tool PASSED [ 87%]
tests/test_tools_mcp_gateway.py::test_self_approval_rejected_with_403 PASSED [100%]
============================== 8 passed in 0.63s ==============================
```
