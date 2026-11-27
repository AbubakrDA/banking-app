import pytest
from httpx import AsyncClient
from sqlalchemy import select, func

from app.core.config import Settings
from app.core.security import create_access_token
from app.models.banking import BankAccount, BankTransfer
from app.models.enterprise import AuditLog
from app.services.banking.service import BankingService
from app.services.integrations.registry import IntegrationRegistry


def _auth(user_id: str, role: str, tenant_id: str = "tenant_bank_01") -> dict:
    token = create_access_token(
        subject=user_id,
        tenant_id=tenant_id,
        role=role,
        email=f"{user_id}@bank.local",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_rbac_route_matrix_surfaces_and_department_isolation(client: AsyncClient) -> None:
    from app.main import app
    from app.core.database import get_db

    tenant = "tenant_matrix_01"
    async for db in app.dependency_overrides[get_db]():
        await BankingService.bank_api.seed_dev_data(db, tenant)
        await db.commit()
        break

    tokens = {
        "customer": _auth("cust_user_01", "customer", tenant),
        "employee": _auth("emp_01", "employee", tenant),
        "risk_officer": _auth("risk_01", "risk_officer", tenant),
        "admin": _auth("admin_01", "admin", tenant),
        "hr": _auth("hr_01", "hr", tenant),
        "marketing": _auth("mkt_01", "marketing", tenant),
        "unknown": _auth("rogue_01", "agent", tenant),  # Old support role -> default deny
    }

    # 1. Unauthenticated -> 401
    assert (await client.get("/api/v1/accounts")).status_code == 401

    # 2. Unknown role -> 403 default deny
    assert (await client.get("/api/v1/accounts", headers=tokens["unknown"])).status_code == 403

    # 3. Surface isolation: customer refused on staff-only; staff refused on customer-only
    assert (await client.get("/api/v1/customers/search", headers=tokens["customer"])).status_code == 403
    assert (await client.get("/api/v1/integrations/status", headers=tokens["customer"])).status_code == 403
    assert (await client.get("/api/v1/customers/me", headers=tokens["employee"])).status_code == 403
    assert (await client.get("/api/v1/customers/me", headers=tokens["admin"])).status_code == 403
    assert (
        await client.post(
            "/api/v1/transfers",
            headers=tokens["admin"],
            json={"from_account_id": "a", "to_account_id": "b", "amount_minor": 100, "currency": "USD"},
        )
    ).status_code == 403
    assert (
        await client.patch(
            "/api/v1/cards/card_1/status",
            headers=tokens["employee"],
            json={"status": "blocked"},
        )
    ).status_code == 403

    # 4. HR and Marketing never receive account balances or transaction data (403)
    for dept_role in ("hr", "marketing"):
        hdrs = {**tokens[dept_role], "X-Access-Reason": "Department check"}
        assert (await client.get("/api/v1/accounts", headers=hdrs)).status_code == 403
        assert (await client.get("/api/v1/transactions", headers=hdrs)).status_code == 403
        assert (await client.get("/api/v1/transfers", headers=hdrs)).status_code == 403
        assert (await client.get("/api/v1/cards", headers=hdrs)).status_code == 403
        assert (await client.get("/api/v1/customers/search", headers=hdrs)).status_code == 403
        assert (await client.get("/api/v1/risk/alerts", headers=hdrs)).status_code == 403
        # Allowed on non-financial policy list
        assert (await client.get("/api/v1/policies", headers=hdrs)).status_code == 200

    # 5. Accounts: customer (own, no reason needed) vs staff (403 without reason, 200 with reason)
    assert (await client.get("/api/v1/accounts", headers=tokens["customer"])).status_code == 200
    for role in ("employee", "risk_officer", "admin"):
        assert (await client.get("/api/v1/accounts", headers=tokens[role])).status_code == 403
        assert (
            await client.get(
                "/api/v1/accounts",
                headers={**tokens[role], "X-Access-Reason": "Routine audit review"},
            )
        ).status_code == 200

    # 6. Transactions: paginated filter
    r_tx = await client.get("/api/v1/transactions?page=1&page_size=5", headers=tokens["customer"])
    assert r_tx.status_code == 200
    assert len(r_tx.json()["data"]["items"]) <= 5

    # 7. Transfers & Cards: risk_officer cannot move money or alter cards (403)
    assert (
        await client.post(
            "/api/v1/transfers",
            headers=tokens["risk_officer"],
            json={"from_account_id": "a", "to_account_id": "b", "amount_minor": 100, "currency": "USD"},
        )
    ).status_code == 403
    assert (
        await client.patch(
            "/api/v1/cards/card_1/status",
            headers=tokens["risk_officer"],
            json={"status": "blocked"},
        )
    ).status_code == 403

    # 8. Customers search: staff with reason -> 200 masked
    r_cust_search = await client.get(
        "/api/v1/customers/search",
        headers={**tokens["employee"], "X-Access-Reason": "Customer verification"},
    )
    assert r_cust_search.status_code == 200
    assert r_cust_search.json()["data"][0]["national_id_masked"].startswith("***-**-")

    # 9. Risk & Approvals: customer & employee -> 403; risk_officer & admin -> 200
    for role in ("customer", "employee"):
        assert (await client.get("/api/v1/risk/alerts", headers=tokens[role])).status_code == 403
        assert (await client.get("/api/v1/approvals", headers=tokens[role])).status_code == 403
    for role in ("risk_officer", "admin"):
        assert (await client.get("/api/v1/risk/alerts", headers=tokens[role])).status_code == 200
        assert (await client.get("/api/v1/approvals", headers=tokens[role])).status_code == 200

    # 10. Policies: upload, self-approval blocked for admin, approval by different admin
    policy_payload = {"title": "Wire Policy", "filename": "wire.pdf", "pages": ["Page 1 wire rules"]}
    assert (await client.post("/api/v1/policies", headers=tokens["customer"], json=policy_payload)).status_code == 403
    r_pol = await client.post("/api/v1/policies", headers=tokens["admin"], json=policy_payload)
    assert r_pol.status_code == 200
    pol_id = r_pol.json()["data"]["id"]
    assert (await client.post(f"/api/v1/policies/{pol_id}/approve", headers=tokens["admin"])).status_code == 403
    admin2 = _auth("admin_02", "admin", tenant)
    assert (await client.post(f"/api/v1/policies/{pol_id}/approve", headers=admin2)).status_code == 200

    # 11. Audit & Admin
    for role in ("customer", "employee"):
        assert (await client.get("/api/v1/audit", headers=tokens[role])).status_code == 403
        assert (await client.get("/api/v1/audit/verify", headers=tokens[role])).status_code == 403
    for role in ("customer", "employee", "risk_officer"):
        assert (await client.get("/api/v1/admin/users", headers=tokens[role])).status_code == 403
        assert (await client.get("/api/v1/admin/config", headers=tokens[role])).status_code == 403
    assert (await client.get("/api/v1/admin/config", headers=tokens["admin"])).status_code == 200


@pytest.mark.asyncio
async def test_cross_customer_404_idempotency_cross_border_and_audit_tamper(client: AsyncClient) -> None:
    from app.main import app
    from app.core.database import get_db

    tenant = "tenant_matrix_02"
    async for db in app.dependency_overrides[get_db]():
        await BankingService.bank_api.seed_dev_data(db, tenant)
        await db.commit()
        accts = (
            await db.execute(select(BankAccount).where(BankAccount.tenant_id == tenant))
        ).scalars().all()
        usd_accts = [a for a in accts if a.currency == "USD"]
        c1_checking_id = next(a.id for a in usd_accts if a.account_number_masked == "****1042")
        c2_checking_id = next(a.id for a in usd_accts if a.account_number_masked == "****3099")
        break

    cust1 = _auth("cust_user_01", "customer", tenant)
    admin2 = _auth("admin_02", "admin", tenant)

    # Cross-customer account access returns 404
    assert (await client.get(f"/api/v1/accounts/{c2_checking_id}", headers=cust1)).status_code == 404

    # Cross-border transfer disabled behind feature flag -> 403
    r_cb = await client.post(
        "/api/v1/transfers",
        headers=cust1,
        json={
            "from_account_id": c1_checking_id,
            "to_account_id": c2_checking_id,
            "amount_minor": 1000,
            "currency": "USD",
            "is_cross_border": True,
        },
    )
    assert r_cb.status_code == 403

    # Idempotency-Key: retry with same key returns same transfer and does not create a second one
    idem_headers = {**cust1, "Idempotency-Key": "idem-key-001"}
    r_x1 = await client.post(
        "/api/v1/transfers",
        headers=idem_headers,
        json={
            "from_account_id": c1_checking_id,
            "to_account_id": c2_checking_id,
            "amount_minor": 2_500,
            "currency": "USD",
            "reference": "Idempotent payment",
        },
    )
    r_x2 = await client.post(
        "/api/v1/transfers",
        headers=idem_headers,
        json={
            "from_account_id": c1_checking_id,
            "to_account_id": c2_checking_id,
            "amount_minor": 2_500,
            "currency": "USD",
            "reference": "Idempotent payment",
        },
    )
    assert r_x1.status_code == 200
    assert r_x2.status_code == 200
    assert r_x1.json()["data"]["id"] == r_x2.json()["data"]["id"]

    async for db in app.dependency_overrides[get_db]():
        count = (
            await db.execute(
                select(func.count(BankTransfer.id)).where(
                    BankTransfer.tenant_id == tenant,
                    BankTransfer.idempotency_key == "idem-key-001",
                )
            )
        ).scalar()
        assert count == 1
        break

    # High-risk transfer requested by cust1 -> pending_approval -> admin2 approves (200 -> completed)
    r_high = await client.post(
        "/api/v1/transfers",
        headers=cust1,
        json={
            "from_account_id": c1_checking_id,
            "to_account_id": c2_checking_id,
            "amount_minor": 150_000,
            "currency": "USD",
            "reference": "High risk transfer",
        },
    )
    assert r_high.status_code == 200
    high_id = r_high.json()["data"]["id"]
    assert r_high.json()["data"]["status"] == "pending_approval"

    r_approve = await client.post(f"/api/v1/approvals/{high_id}/approve", headers=admin2)
    assert r_approve.status_code == 200
    assert r_approve.json()["data"]["status"] == "completed"

    # Audit chain verify valid -> tamper -> invalid
    r_verify_ok = await client.get("/api/v1/audit/verify", headers=admin2)
    assert r_verify_ok.status_code == 200
    assert r_verify_ok.json()["data"]["valid"] is True

    async for db in app.dependency_overrides[get_db]():
        latest = (
            await db.execute(select(AuditLog).where(AuditLog.tenant_id == tenant).limit(1))
        ).scalar_one()
        latest_id = latest.id
        latest.status = "TAMPERED"
        await db.commit()
        break

    r_verify_bad = await client.get("/api/v1/audit/verify", headers=admin2)
    assert r_verify_bad.status_code == 200
    assert r_verify_bad.json()["data"]["valid"] is False
    assert r_verify_bad.json()["data"]["broken_at_id"] == latest_id


@pytest.mark.asyncio
async def test_bank_selectable_integrations_and_staff_timeout(client: AsyncClient) -> None:
    from app.main import app
    from app.core.database import get_db
    from app.core.auth import AuthenticatedUser

    tenant = "tenant_int_01"
    cust1 = _auth("cust_user_01", "customer", tenant)

    # 1. Default disabled -> API returns 4xx (400)
    r_disabled = await client.post(
        "/api/v1/integrations/mobile-money/payout",
        headers=cust1,
        json={"phone_masked": "+249***1234", "amount_minor": 5000, "currency": "SDG"},
    )
    assert 400 <= r_disabled.status_code < 500

    # 2. Unknown provider name refused at startup
    bad_cfg = Settings(
        ENVIRONMENT="test",
        MOBILE_MONEY_PROVIDER="unknown_vendor_xyz",
    )
    with pytest.raises(ValueError, match="Unknown MOBILE_MONEY_PROVIDER"):
        IntegrationRegistry.validate_startup_config(bad_cfg)

    # 3. Configured stub provider is called through interface and audited
    stub_cfg = Settings(
        ENVIRONMENT="test",
        ENABLE_MOBILE_MONEY_INTEGRATION=True,
        MOBILE_MONEY_PROVIDER="stub",
    )
    async for db in app.dependency_overrides[get_db]():
        user = AuthenticatedUser("cust_user_01", "layla@bank.local", "customer", tenant)
        res = await IntegrationRegistry.call_mobile_money_payout(
            db, user, phone_masked="+249***1234", amount_minor=5000, currency="SDG", cfg=stub_cfg
        )
        assert res["status"] == "not_configured"
        assert res["provider"] == "stub"
        audit_row = (
            await db.execute(
                select(AuditLog).where(
                    AuditLog.tenant_id == tenant,
                    AuditLog.event_type == "INTEGRATION_MOBILE_MONEY",
                    AuditLog.status == "SUCCESS",
                )
            )
        ).scalar_one_or_none()
        assert audit_row is not None
        break
