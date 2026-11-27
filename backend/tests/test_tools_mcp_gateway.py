import pytest
import uuid
from httpx import AsyncClient
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_tool_registry_discovery(client: AsyncClient) -> None:
    token = create_access_token("agent_tools_01", "tenant_tools_01", "agent", "tools1@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.get("/api/v1/tools", headers=headers)
    assert res.status_code == 200
    tools = res.json()["data"]

    tool_map = {t["name"]: t for t in tools}
    assert "lookup_order" in tool_map
    assert "create_appointment" in tool_map
    assert "cancel_order" in tool_map
    assert "process_refund" in tool_map

    # Risk classifications
    assert tool_map["lookup_order"]["risk_level"] == "LOW"
    assert tool_map["lookup_order"]["requires_human_approval"] is False

    assert tool_map["create_appointment"]["risk_level"] == "MEDIUM"

    assert tool_map["cancel_order"]["risk_level"] == "HIGH"
    assert tool_map["cancel_order"]["requires_human_approval"] is True


@pytest.mark.asyncio
async def test_low_risk_tool_execution(client: AsyncClient) -> None:
    token = create_access_token("agent_tools_02", "tenant_tools_02", "agent", "tools2@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Execute low-risk tool
    exec_res = await client.post(
        "/api/v1/tools/execute",
        headers=headers,
        json={
            "tool_name": "lookup_order",
            "caller_agent": "customer_support_agent",
            "parameters": {"order_number": "ORD-9999"},
        },
    )
    assert exec_res.status_code == 200
    data = exec_res.json()["data"]

    assert data["tool_name"] == "lookup_order"
    assert data["risk_level"] == "LOW"
    assert data["status"] == "success"
    assert data["requires_approval"] is False
    assert data["result"] is not None
    assert "_envelope" in data["result"]
    assert data["result"]["_envelope"]["untrusted"] is True


@pytest.mark.asyncio
async def test_high_risk_human_approval_gate(client: AsyncClient) -> None:
    token_agent = create_access_token("agent_tools_03", "tenant_tools_03", "agent", "tools3@test.com")
    token_supervisor = create_access_token("sup_tools_03", "tenant_tools_03", "admin", "sup3@test.com")
    headers_agent = {"Authorization": f"Bearer {token_agent}"}
    headers_sup = {"Authorization": f"Bearer {token_supervisor}"}

    # 1. Agent calls high-risk cancel_order
    exec_res = await client.post(
        "/api/v1/tools/execute",
        headers=headers_agent,
        json={
            "tool_name": "cancel_order",
            "caller_agent": "customer_support_agent",
            "parameters": {"order_number": "ORD-CANCEL-123", "reason": "Customer changed mind"},
        },
    )
    assert exec_res.status_code == 200
    data = exec_res.json()["data"]

    assert data["risk_level"] == "HIGH"
    assert data["status"] == "requires_approval"
    assert data["requires_approval"] is True
    assert data["result"] is None
    execution_id = data["execution_id"]

    # 2. Supervisor inspects executions
    list_res = await client.get("/api/v1/tools/executions?status=requires_approval", headers=headers_sup)
    assert list_res.status_code == 200
    pending_list = list_res.json()["data"]
    assert any(e["id"] == execution_id for e in pending_list)

    # 3. Supervisor approves execution
    appr_res = await client.post(f"/api/v1/tools/executions/{execution_id}/approve", headers=headers_sup)
    assert appr_res.status_code == 200
    appr_data = appr_res.json()["data"]
    assert appr_data["status"] == "success"
    assert appr_data["result"] is not None


@pytest.mark.asyncio
async def test_high_risk_rejection_flow(client: AsyncClient) -> None:
    token_agent = create_access_token("agent_tools_04", "tenant_tools_04", "agent", "tools4@test.com")
    token_supervisor = create_access_token("sup_tools_04", "tenant_tools_04", "admin", "sup4@test.com")
    headers_agent = {"Authorization": f"Bearer {token_agent}"}
    headers_sup = {"Authorization": f"Bearer {token_supervisor}"}

    # 1. Agent calls process_refund
    exec_res = await client.post(
        "/api/v1/tools/execute",
        headers=headers_agent,
        json={
            "tool_name": "process_refund",
            "caller_agent": "billing_agent",
            "parameters": {"order_number": "ORD-REFUND-456", "amount": 250.0},
        },
    )
    assert exec_res.status_code == 200
    execution_id = exec_res.json()["data"]["execution_id"]

    # 2. Supervisor rejects
    rej_res = await client.post(
        f"/api/v1/tools/executions/{execution_id}/reject",
        headers=headers_sup,
        json={"decision": "reject", "reason": "Dispute rejected: item delivered and unreturned"},
    )
    assert rej_res.status_code == 200
    rej_data = rej_res.json()["data"]
    assert rej_data["status"] == "rejected"
    assert rej_data["result"] is None


@pytest.mark.asyncio
async def test_mcp_server_registration_and_discovery(client: AsyncClient) -> None:
    token = create_access_token("admin_tools_05", "tenant_tools_05", "admin", "tools5@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Register external MCP server
    create_res = await client.post(
        "/api/v1/tools/mcp-servers",
        headers=headers,
        json={
            "name": "Stripe Billing MCP",
            "transport_type": "http",
            "endpoint_url": "https://mcp.billing.internal/v1",
            "is_enabled": True,
        },
    )
    assert create_res.status_code == 200
    server = create_res.json()["data"]
    assert server["name"] == "Stripe Billing MCP"
    assert len(server["discovered_tools"]) >= 1

    # List MCP servers
    list_res = await client.get("/api/v1/tools/mcp-servers", headers=headers)
    assert list_res.status_code == 200
    servers = list_res.json()["data"]
    assert any(s["id"] == server["id"] for s in servers)


@pytest.mark.asyncio
async def test_strict_multi_tenant_isolation_tools(client: AsyncClient) -> None:
    token_a = create_access_token("agent_a", "tenant_tools_alpha", "agent", "alpha@test.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    token_b = create_access_token("agent_b", "tenant_tools_beta", "agent", "beta@test.com")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Tenant Alpha executes tool
    exec_a = await client.post(
        "/api/v1/tools/execute",
        headers=headers_a,
        json={
            "tool_name": "lookup_order",
            "caller_agent": "customer_support_agent",
            "parameters": {"order_number": "ALPHA-ORD-001"},
        },
    )
    assert exec_a.status_code == 200
    exec_a_id = exec_a.json()["data"]["execution_id"]

    # Tenant Beta queries executions
    beta_list = await client.get("/api/v1/tools/executions", headers=headers_b)
    assert beta_list.status_code == 200
    beta_executions = beta_list.json()["data"]
    assert not any(e["id"] == exec_a_id for e in beta_executions)

    # Tenant Beta tries to fetch Tenant Alpha's execution directly -> 404
    direct_fetch = await client.get(f"/api/v1/tools/executions/{exec_a_id}", headers=headers_b)
    assert direct_fetch.status_code == 404


@pytest.mark.asyncio
async def test_non_admin_cannot_approve_or_reject_tool(client: AsyncClient) -> None:
    token_agent = create_access_token("agent_gate_01", "tenant_gate_01", "agent", "agentgate@test.com")
    headers_agent = {"Authorization": f"Bearer {token_agent}"}

    exec_res = await client.post(
        "/api/v1/tools/execute",
        headers=headers_agent,
        json={"tool_name": "cancel_order", "parameters": {"order_number": "ORD-999"}},
    )
    assert exec_res.status_code == 200
    execution_id = exec_res.json()["data"]["execution_id"]

    appr_res = await client.post(f"/api/v1/tools/executions/{execution_id}/approve", headers=headers_agent)
    assert appr_res.status_code == 403

    rej_res = await client.post(
        f"/api/v1/tools/executions/{execution_id}/reject",
        headers=headers_agent,
        json={"decision": "reject", "reason": "self reject attempt"},
    )
    assert rej_res.status_code == 403


@pytest.mark.asyncio
async def test_self_approval_rejected_with_403(client: AsyncClient) -> None:
    token_admin1 = create_access_token("admin_req_01", "tenant_self_01", "admin", "admin1@self.com")
    token_admin2 = create_access_token("admin_sup_02", "tenant_self_01", "admin", "admin2@self.com")
    headers_1 = {"Authorization": f"Bearer {token_admin1}"}
    headers_2 = {"Authorization": f"Bearer {token_admin2}"}

    # Admin 1 requests a high-risk tool
    exec_res = await client.post(
        "/api/v1/tools/execute",
        headers=headers_1,
        json={"tool_name": "process_refund", "parameters": {"order_number": "ORD-SELF-1", "amount": 50.0}},
    )
    assert exec_res.status_code == 200
    execution_id = exec_res.json()["data"]["execution_id"]

    # Admin 1 cannot self-approve or self-reject -> 403 SELF_APPROVAL_FORBIDDEN
    self_appr = await client.post(f"/api/v1/tools/executions/{execution_id}/approve", headers=headers_1)
    assert self_appr.status_code == 403
    assert "SELF_APPROVAL_FORBIDDEN" in str(self_appr.json())

    self_rej = await client.post(
        f"/api/v1/tools/executions/{execution_id}/reject",
        headers=headers_1,
        json={"decision": "reject", "reason": "nope"},
    )
    assert self_rej.status_code == 403

    # Admin 2 (distinct supervisor) CAN approve
    sup_appr = await client.post(f"/api/v1/tools/executions/{execution_id}/approve", headers=headers_2)
    assert sup_appr.status_code == 200
    assert sup_appr.json()["data"]["status"] == "success"


@pytest.mark.asyncio
async def test_cross_tenant_tool_approval_and_rejection_blocked(client: AsyncClient) -> None:
    """Verify an admin in Tenant Beta cannot approve or reject Tenant Alpha's pending tool execution."""
    token_alpha_agent = create_access_token("agent_ct_a", "tenant_ct_alpha", "agent", "ct_a@test.com")
    token_beta_admin = create_access_token("admin_ct_b", "tenant_ct_beta", "admin", "ct_b@test.com")

    exec_res = await client.post(
        "/api/v1/tools/execute",
        headers={"Authorization": f"Bearer {token_alpha_agent}"},
        json={
            "tool_name": "process_refund",
            "caller_agent": "billing_agent",
            "parameters": {"order_number": "ORD-CT-100", "amount": 50.0},
        },
    )
    assert exec_res.status_code == 200
    execution_id = exec_res.json()["data"]["execution_id"]

    app_res = await client.post(
        f"/api/v1/tools/executions/{execution_id}/approve",
        headers={"Authorization": f"Bearer {token_beta_admin}"},
        json={"decision": "approve", "reason": "Cross-tenant attempt"},
    )
    assert app_res.status_code in (400, 404)

    rej_res = await client.post(
        f"/api/v1/tools/executions/{execution_id}/reject",
        headers={"Authorization": f"Bearer {token_beta_admin}"},
        json={"decision": "reject", "reason": "Cross-tenant attempt"},
    )
    assert rej_res.status_code in (400, 404)

    # Confirm Tenant Alpha's execution remains untouched
    get_res = await client.get(
        f"/api/v1/tools/executions/{execution_id}",
        headers={"Authorization": f"Bearer {token_alpha_agent}"},
    )
    assert get_res.status_code == 200
    assert get_res.json()["data"]["status"] == "requires_approval"
