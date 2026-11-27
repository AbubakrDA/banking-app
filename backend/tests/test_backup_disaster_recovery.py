import pytest
from httpx import AsyncClient
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_backup_trigger_and_metadata_verification(client: AsyncClient) -> None:
    token = create_access_token("admin_dr_01", "tenant_dr_01", "admin", "admin_dr1@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Trigger manual full backup
    trigger_payload = {
        "backup_type": "FULL",
        "target_type": "POSTGRESQL",
        "retention_tier": "DAILY",
        "notes": "Pre-deployment database baseline snapshot",
    }
    res = await client.post("/api/v1/backup/trigger", headers=headers, json=trigger_payload)
    assert res.status_code == 200, res.text
    backup = res.json()["data"]

    assert backup["id"] is not None
    assert backup["tenant_id"] == "tenant_dr_01"
    assert backup["backup_type"] == "FULL"
    assert backup["target_type"] == "POSTGRESQL"
    assert backup["status"] == "COMPLETED"
    assert backup["storage_path"].startswith("s3://banking-ai-platform-backups/tenant_dr_01/daily/")
    assert backup["is_encrypted"] is True
    assert backup["encryption_algorithm"] == "AES-256-GCM"
    assert len(backup["sha256_checksum"]) == 64
    assert backup["size_bytes"] > 0
    assert backup["expires_at"] is not None
    assert backup["meta_data"]["notes"] == "Pre-deployment database baseline snapshot"

    # 2. List backup history and verify presence
    res_list = await client.get("/api/v1/backup/history", headers=headers)
    assert res_list.status_code == 200
    catalog = res_list.json()["data"]
    assert catalog["total"] >= 1
    found = any(b["id"] == backup["id"] for b in catalog["items"])
    assert found is True


@pytest.mark.asyncio
async def test_restore_drill_execution(client: AsyncClient) -> None:
    token = create_access_token("admin_dr_02", "tenant_dr_02", "admin", "admin_dr2@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # First create a backup to test restore against
    res_b = await client.post(
        "/api/v1/backup/trigger",
        headers=headers,
        json={"backup_type": "FULL", "target_type": "POSTGRESQL", "retention_tier": "DAILY"},
    )
    assert res_b.status_code == 200
    backup_id = res_b.json()["data"]["id"]

    # 1. Successful non-destructive sandbox drill
    drill_payload = {
        "backup_id": backup_id,
        "simulate_failure": False,
        "notes": "Automated weekly business continuity recovery validation",
    }
    res_drill = await client.post("/api/v1/backup/drill", headers=headers, json=drill_payload)
    assert res_drill.status_code == 200
    drill = res_drill.json()["data"]

    assert drill["id"] is not None
    assert drill["backup_id"] == backup_id
    assert drill["status"] == "SUCCESS"
    assert drill["checksum_verified"] is True
    assert drill["tables_validated"] >= 14
    assert drill["records_validated"] > 0
    assert drill["rto_seconds"] < 14400  # < 4 hours RTO target
    assert drill["rpo_minutes"] <= 60  # < 1 hour RPO target

    # 2. Chaos simulated failure drill
    chaos_payload = {
        "backup_id": backup_id,
        "simulate_failure": True,
        "notes": "Simulated checksum mismatch in table partition",
    }
    res_chaos = await client.post("/api/v1/backup/drill", headers=headers, json=chaos_payload)
    assert res_chaos.status_code == 200
    chaos = res_chaos.json()["data"]
    assert chaos["status"] == "FAILED"
    assert chaos["checksum_verified"] is False

    # 3. List drills
    res_drills = await client.get("/api/v1/backup/drills", headers=headers)
    assert res_drills.status_code == 200
    drills_catalog = res_drills.json()["data"]
    assert drills_catalog["total"] >= 2


@pytest.mark.asyncio
async def test_rpo_and_rto_compliance_status(client: AsyncClient) -> None:
    token = create_access_token("admin_dr_03", "tenant_dr_03", "admin", "admin_dr3@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Trigger a fresh backup
    await client.post(
        "/api/v1/backup/trigger",
        headers=headers,
        json={"backup_type": "FULL", "target_type": "POSTGRESQL", "retention_tier": "DAILY"},
    )

    res = await client.get("/api/v1/backup/status", headers=headers)
    assert res.status_code == 200
    status_data = res.json()["data"]

    assert status_data["overall_status"] in ["HEALTHY", "WARNING"]
    assert status_data["rpo_target"] == "< 1 Hour"
    assert status_data["rto_target"] == "< 4 Hours"
    assert status_data["rpo_compliant"] is True
    assert status_data["rto_compliant"] is True
    assert status_data["replication_status"] == "ACTIVE_CROSS_REGION_REPLICATION"
    assert status_data["encryption_status"] == "AES_256_GCM_ENCRYPTED"
    assert status_data["last_backup_timestamp"] is not None
    assert status_data["next_scheduled_backup"] is not None
    assert status_data["total_backups_count"] >= 1


@pytest.mark.asyncio
async def test_retention_policy_and_pruning(client: AsyncClient) -> None:
    token = create_access_token("admin_dr_04", "tenant_dr_04", "admin", "admin_dr4@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch default policy
    res_pol = await client.get("/api/v1/backup/retention-policy", headers=headers)
    assert res_pol.status_code == 200
    pol = res_pol.json()["data"]
    assert pol["daily_retention_days"] == 7
    assert pol["weekly_retention_weeks"] == 4
    assert pol["monthly_retention_months"] == 12

    # 2. Update policy
    update_payload = {
        "daily_retention_days": 14,
        "weekly_retention_weeks": 8,
        "monthly_retention_months": 24,
    }
    res_update = await client.put("/api/v1/backup/retention-policy", headers=headers, json=update_payload)
    assert res_update.status_code == 200
    updated_pol = res_update.json()["data"]
    assert updated_pol["daily_retention_days"] == 14
    assert updated_pol["weekly_retention_weeks"] == 8
    assert updated_pol["monthly_retention_months"] == 24

    # 3. Prune expired backups
    res_prune = await client.post("/api/v1/backup/prune", headers=headers)
    assert res_prune.status_code == 200
    prune_data = res_prune.json()["data"]
    assert "Successfully pruned" in prune_data["message"]


@pytest.mark.asyncio
async def test_strict_multi_tenant_isolation_backup(client: AsyncClient) -> None:
    token_a = create_access_token("admin_dr_a", "tenant_dr_alpha", "admin", "admin_a@alpha.com")
    token_b = create_access_token("admin_dr_b", "tenant_dr_beta", "admin", "admin_b@beta.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 1. Tenant Alpha creates private backup
    res_a = await client.post(
        "/api/v1/backup/trigger",
        headers=headers_a,
        json={"backup_type": "FULL", "target_type": "POSTGRESQL", "retention_tier": "DAILY"},
    )
    assert res_a.status_code == 200
    backup_a_id = res_a.json()["data"]["id"]

    # 2. Tenant Beta attempts to run restore drill on Tenant Alpha's backup -> 404 NOT FOUND
    res_b_drill = await client.post(
        "/api/v1/backup/drill",
        headers=headers_b,
        json={"backup_id": backup_a_id, "simulate_failure": False},
    )
    assert res_b_drill.status_code == 404
    assert "not found or access denied" in res_b_drill.json()["error"]["message"]

    # 3. Tenant Beta views backup history -> Alpha's backup must not leak
    res_b_hist = await client.get("/api/v1/backup/history", headers=headers_b)
    assert res_b_hist.status_code == 200
    b_items = res_b_hist.json()["data"]["items"]
    assert not any(item["id"] == backup_a_id for item in b_items)


@pytest.mark.asyncio
async def test_rbac_access_control_backup(client: AsyncClient) -> None:
    token_agent = create_access_token("agent_dr_01", "tenant_dr_rbac", "agent", "agent_dr@test.com")
    headers_agent = {"Authorization": f"Bearer {token_agent}"}

    # 1. Agent cannot trigger backup -> 403 Forbidden
    res_trigger = await client.post(
        "/api/v1/backup/trigger",
        headers=headers_agent,
        json={"backup_type": "FULL", "target_type": "POSTGRESQL", "retention_tier": "DAILY"},
    )
    assert res_trigger.status_code == 403

    # 2. Agent cannot execute restore drill -> 403 Forbidden
    res_drill = await client.post(
        "/api/v1/backup/drill",
        headers=headers_agent,
        json={"backup_id": "dummy-uuid", "simulate_failure": False},
    )
    assert res_drill.status_code == 403

    # 3. Agent cannot update retention policy -> 403 Forbidden
    res_policy = await client.put(
        "/api/v1/backup/retention-policy",
        headers=headers_agent,
        json={"daily_retention_days": 30},
    )
    assert res_policy.status_code == 403

    # 4. Agent cannot trigger prune -> 403 Forbidden
    res_prune = await client.post("/api/v1/backup/prune", headers=headers_agent)
    assert res_prune.status_code == 403


@pytest.mark.asyncio
async def test_infrastructure_dashboard_backup_integration(client: AsyncClient) -> None:
    token = create_access_token("admin_dr_infra", "tenant_dr_infra", "admin", "admin_infra@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Trigger a backup first
    await client.post(
        "/api/v1/backup/trigger",
        headers=headers,
        json={"backup_type": "FULL", "target_type": "POSTGRESQL", "retention_tier": "DAILY"},
    )

    # Query infrastructure dashboard
    res = await client.get("/api/v1/infrastructure/dashboard", headers=headers)
    assert res.status_code == 200
    data = res.json()["data"]
    assert "Verified Clean" in data["last_backup_status"]
