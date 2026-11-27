import pytest
import uuid
from httpx import AsyncClient
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_corporate_branding_lifecycle(client: AsyncClient) -> None:
    token_admin = create_access_token("admin_ent_01", "tenant_ent_01", "admin", "admin1@test.com")
    token_agent = create_access_token("agent_ent_01", "tenant_ent_01", "agent", "agent1@test.com")
    headers_admin = {"Authorization": f"Bearer {token_admin}"}
    headers_agent = {"Authorization": f"Bearer {token_agent}"}

    # 1. Fetch default branding
    res = await client.get("/api/v1/enterprise/branding", headers=headers_admin)
    assert res.status_code == 200
    b = res.json()["data"]
    assert b["primary_color"] == "#0B192C"

    # 2. Agent tries to update branding -> 403 Forbidden
    res_agent_fail = await client.patch(
        "/api/v1/enterprise/branding",
        headers=headers_agent,
        json={"primary_color": "#FF0000", "accent_color": "#00FF00"},
    )
    assert res_agent_fail.status_code == 403

    # 3. Admin updates branding
    res_update = await client.patch(
        "/api/v1/enterprise/branding",
        headers=headers_admin,
        json={
            "logo_url": "https://cdn.enterprise.com/logo.svg",
            "primary_color": "#1A365D",
            "accent_color": "#2B6CB0",
            "font_family": "Plus Jakarta Sans, sans-serif",
            "email_footer_text": "Enterprise Support by Acme Corp",
        },
    )
    assert res_update.status_code == 200
    updated_b = res_update.json()["data"]
    assert updated_b["primary_color"] == "#1A365D"
    assert updated_b["font_family"] == "Plus Jakarta Sans, sans-serif"


@pytest.mark.asyncio
async def test_staff_user_invite_and_rbac_role_change(client: AsyncClient) -> None:
    token_admin = create_access_token("admin_ent_02", "tenant_ent_02", "admin", "admin2@test.com")
    token_agent = create_access_token("agent_ent_02", "tenant_ent_02", "agent", "agent2@test.com")
    headers_admin = {"Authorization": f"Bearer {token_admin}"}
    headers_agent = {"Authorization": f"Bearer {token_agent}"}

    # 1. Agent tries to invite user -> 403 Forbidden
    res_agent_fail = await client.post(
        "/api/v1/enterprise/users/invite",
        headers=headers_agent,
        json={"email": "unauthorized@test.com", "full_name": "Test User", "role": "agent"},
    )
    assert res_agent_fail.status_code == 403

    # 2. Admin invites staff user
    invite_res = await client.post(
        "/api/v1/enterprise/users/invite",
        headers=headers_admin,
        json={"email": "staff.member@test.com", "full_name": "Staff Member", "role": "agent"},
    )
    assert invite_res.status_code == 200
    user_data = invite_res.json()["data"]
    user_id = user_data["id"]
    assert user_data["email"] == "staff.member@test.com"
    assert user_data["role"] == "agent"

    # 3. Admin updates role to admin
    role_res = await client.patch(
        f"/api/v1/enterprise/users/{user_id}/role",
        headers=headers_admin,
        json={"role": "admin"},
    )
    assert role_res.status_code == 200
    assert role_res.json()["data"]["role"] == "admin"

    # 4. List staff users
    list_res = await client.get("/api/v1/enterprise/users", headers=headers_admin)
    assert list_res.status_code == 200
    users = list_res.json()["data"]
    assert any(u["id"] == user_id for u in users)


@pytest.mark.asyncio
async def test_security_posture_and_session_revocation(client: AsyncClient) -> None:
    token_admin = create_access_token("admin_ent_03", "tenant_ent_03", "admin", "admin3@test.com")
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    # 1. Query posture
    posture_res = await client.get("/api/v1/enterprise/security/posture", headers=headers_admin)
    assert posture_res.status_code == 200
    data = posture_res.json()["data"]
    assert data["security_health_score"] >= 80
    assert data["status"] in ["SECURE", "NEEDS_ATTENTION"]
    assert data["data_retention_days"] >= 30

    # 2. Revoke session
    revoke_res = await client.post(
        "/api/v1/enterprise/security/revoke-session",
        headers=headers_admin,
        json={"user_id": "target_user_123", "reason": "Suspicious login from unexpected region"},
    )
    assert revoke_res.status_code == 200
    rev_data = revoke_res.json()["data"]
    assert rev_data["revoked_sessions_count"] >= 1
    assert "target_user_123" in rev_data["message"]


@pytest.mark.asyncio
async def test_immutable_audit_log_and_csv_export(client: AsyncClient) -> None:
    token_admin = create_access_token("admin_ent_04", "tenant_ent_04", "admin", "admin4@test.com")
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    # Trigger action to generate audit log
    await client.patch(
        "/api/v1/enterprise/branding",
        headers=headers_admin,
        json={"primary_color": "#112233"},
    )

    # 1. List audit logs
    log_res = await client.get("/api/v1/enterprise/audit-logs", headers=headers_admin)
    assert log_res.status_code == 200
    logs = log_res.json()["data"]
    assert len(logs) >= 1
    first_log = logs[0]
    assert first_log["event_type"] in ["SETTINGS_UPDATE", "USER_INVITED", "ROLE_CHANGE"]
    assert len(first_log["event_hash"]) == 64  # SHA-256

    # 2. Export audit trail to CSV
    export_res = await client.get("/api/v1/enterprise/audit-logs/export?format=csv", headers=headers_admin)
    assert export_res.status_code == 200
    export_data = export_res.json()["data"]
    assert export_data["format"] == "csv"
    assert "Timestamp (UTC),Actor ID" in export_data["content"]
    assert export_data["total_records"] >= 1


@pytest.mark.asyncio
async def test_model_routing_configuration(client: AsyncClient) -> None:
    token_admin = create_access_token("admin_ent_05", "tenant_ent_05", "admin", "admin5@test.com")
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    # 1. Get model config
    res = await client.get("/api/v1/enterprise/model-config", headers=headers_admin)
    assert res.status_code == 200
    cfg = res.json()["data"]
    assert cfg["default_model"] == "gemini-2.5-flash"
    assert cfg["temperature"] == 0.2

    # 2. Update model config
    update_res = await client.patch(
        "/api/v1/enterprise/model-config",
        headers=headers_admin,
        json={
            "default_model": "gemini-2.5-pro",
            "fallback_model": "gemini-2.5-flash",
            "temperature": 0.35,
            "max_tokens": 4096,
            "system_instructions_override": "You are an enterprise AI support agent for BankingAIPlatform.",
        },
    )
    assert update_res.status_code == 200
    updated_cfg = update_res.json()["data"]
    assert updated_cfg["default_model"] == "gemini-2.5-pro"
    assert updated_cfg["temperature"] == 0.35
    assert updated_cfg["max_tokens"] == 4096


@pytest.mark.asyncio
async def test_strict_multi_tenant_isolation_enterprise(client: AsyncClient) -> None:
    token_a = create_access_token("admin_a", "tenant_ent_alpha", "admin", "alpha@test.com")
    token_b = create_access_token("admin_b", "tenant_ent_beta", "admin", "beta@test.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Tenant Alpha updates branding to custom hex
    await client.patch(
        "/api/v1/enterprise/branding",
        headers=headers_a,
        json={"primary_color": "#AABBCC"},
    )

    # Tenant Alpha invites a user
    await client.post(
        "/api/v1/enterprise/users/invite",
        headers=headers_a,
        json={"email": "alpha_exclusive@test.com", "full_name": "Alpha Staff", "role": "agent"},
    )

    # Tenant Beta queries branding -> must NOT see Alpha's color
    b_branding_res = await client.get("/api/v1/enterprise/branding", headers=headers_b)
    assert b_branding_res.status_code == 200
    assert b_branding_res.json()["data"]["primary_color"] != "#AABBCC"

    # Tenant Beta queries staff -> must NOT see Alpha's invited user
    b_users_res = await client.get("/api/v1/enterprise/users", headers=headers_b)
    assert b_users_res.status_code == 200
    assert not any("alpha_exclusive" in u["email"] for u in b_users_res.json()["data"])


@pytest.mark.asyncio
async def test_audit_log_hash_chain_and_tamper_detection(client: AsyncClient) -> None:
    """Verify chained SHA-256 audit logs and tamper detection via /audit-logs/verify."""
    from sqlalchemy import update
    from app.main import app
    from app.core.database import get_db
    from app.models.enterprise import AuditLog

    tenant = f"tenant_chain_{uuid.uuid4().hex[:8]}"
    token_admin = create_access_token("admin_chain", tenant, "admin", "chain@test.com")
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    for color in ("#111111", "#222222", "#333333"):
        r = await client.patch(
            "/api/v1/enterprise/branding",
            headers=headers_admin,
            json={"primary_color": color, "accent_color": "#444444"},
        )
        assert r.status_code == 200

    verify_res = await client.get("/api/v1/enterprise/audit-logs/verify", headers=headers_admin)
    assert verify_res.status_code == 200
    vdata = verify_res.json()["data"]
    assert vdata["valid"] is True
    assert vdata["total_records"] == 3

    logs_res = await client.get("/api/v1/enterprise/audit-logs", headers=headers_admin)
    assert logs_res.status_code == 200
    logs = logs_res.json()["data"]
    assert logs[0]["prev_hash"] == logs[1]["event_hash"]
    assert logs[1]["prev_hash"] == logs[2]["event_hash"]
    assert logs[2]["prev_hash"] == "0" * 64

    target_id = logs[1]["id"]
    async for db in app.dependency_overrides[get_db]():
        await db.execute(
            update(AuditLog)
            .where(AuditLog.id == target_id)
            .values(target_resource="tampered_resource")
        )
        await db.commit()
        break

    tamper_res = await client.get("/api/v1/enterprise/audit-logs/verify", headers=headers_admin)
    assert tamper_res.status_code == 200
    tdata = tamper_res.json()["data"]
    assert tdata["valid"] is False
    assert tdata["broken_id"] == target_id
    assert tdata["reason"] == "event_hash_mismatch"
