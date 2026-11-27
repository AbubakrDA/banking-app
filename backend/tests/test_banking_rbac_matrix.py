import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.core.security import create_access_token
from app.models.banking import BankAccount
from app.models.enterprise import AuditLog
from app.services.banking.service import BankingService


def _auth(user_id: str, role: str, tenant_id: str = "tenant_bank_01") -> dict:
    token = create_access_token(
        subject=user_id,
        tenant_id=tenant_id,
        role=role,
        email=f"{user_id}@bank.local",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_rbac_route_matrix_and_default_deny(client: AsyncClient) -> None:
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
        "unknown": _auth("rogue_01", "agent", tenant),  # Old support role -> default deny
    }

    # 1. Unauthenticated -> 401
    r_unauth = await client.get("/api/v1/accounts")
    assert r_unauth.status_code == 401

    # 2. Unknown role -> 403 default deny
    r_unknown = await client.get("/api/v1/accounts", headers=tokens["unknown"])
    assert r_unknown.status_code == 403

    # 3. Accounts: customer (own, no reason needed) vs staff (403 without reason, 200 with reason)
    assert (await client.get("/api/v1/accounts", headers=tokens["customer"])).status_code == 200
    for role in ("employee", "risk_officer", "admin"):
        assert (await client.get("/api/v1/accounts", headers=tokens[role])).status_code == 403
        assert (
            await client.get(
                "/api/v1/accounts",
                headers={**tokens[role], "X-Access-Reason": "Routine audit review"},
            )
        ).status_code == 200

    # 4. Transactions: paginated filter
    r_tx = await client.get("/api/v1/transactions?page=1&page_size=5", headers=tokens["customer"])
    assert r_tx.status_code == 200
    assert len(r_tx.json()["data"]["items"]) <= 5

    # 5. Transfers: risk_officer cannot move money (403)
    r_risk_xfer = await client.post(
        "/api/v1/transfers",
        headers=tokens["risk_officer"],
        json={"from_account_id": "a", "to_account_id": "b", "amount_minor": 100, "currency": "USD"},
    )
    assert r_risk_xfer.status_code == 403

    # 6. Cards: risk_officer cannot alter card status (403)
    r_risk_card = await client.patch(
        "/api/v1/cards/card_1/status",
        headers=tokens["risk_officer"],
        json={"status": "blocked"},
    )
    assert r_risk_card.status_code == 403

    # 7. Customers search: customer -> 403, staff without reason -> 403, staff with reason -> 200 masked
    assert (await client.get("/api/v1/customers/search", headers=tokens["customer"])).status_code == 403
    assert (await client.get("/api/v1/customers/search", headers=tokens["employee"])).status_code == 403
    r_cust_search = await client.get(
        "/api/v1/customers/search",
        headers={**tokens["employee"], "X-Access-Reason": "Customer verification"},
    )
    assert r_cust_search.status_code == 200
    assert r_cust_search.json()["data"][0]["national_id_masked"].startswith("***-**-")

    # 8. Risk & Approvals: customer & employee -> 403; risk_officer & admin -> 200
    for role in ("customer", "employee"):
        assert (await client.get("/api/v1/risk/alerts", headers=tokens[role])).status_code == 403
        assert (await client.get("/api/v1/approvals", headers=tokens[role])).status_code == 403
    for role in ("risk_officer", "admin"):
        assert (await client.get("/api/v1/risk/alerts", headers=tokens[role])).status_code == 200
        assert (await client.get("/api/v1/approvals", headers=tokens[role])).status_code == 200

    # 9. Policies: customer & risk_officer cannot upload (403); employee & admin can (200)
    policy_payload = {"title": "Wire Policy", "filename": "wire.pdf", "pages": ["Page 1 wire rules"]}
    assert (await client.post("/api/v1/policies", headers=tokens["customer"], json=policy_payload)).status_code == 403
    assert (await client.post("/api/v1/policies", headers=tokens["risk_officer"], json=policy_payload)).status_code == 403
    r_pol = await client.post("/api/v1/policies", headers=tokens["employee"], json=policy_payload)
    assert r_pol.status_code == 200
    pol_id = r_pol.json()["data"]["id"]
    assert (await client.post(f"/api/v1/policies/{pol_id}/approve", headers=tokens["employee"])).status_code == 403
    assert (await client.post(f"/api/v1/policies/{pol_id}/approve", headers=tokens["admin"])).status_code == 200

    # 10. Audit & Admin: customer/employee -> 403 on audit; only admin on /admin/*
    for role in ("customer", "employee"):
        assert (await client.get("/api/v1/audit", headers=tokens[role])).status_code == 403
        assert (await client.get("/api/v1/audit/verify", headers=tokens[role])).status_code == 403
    for role in ("customer", "employee", "risk_officer"):
        assert (await client.get("/api/v1/admin/users", headers=tokens[role])).status_code == 403
        assert (await client.get("/api/v1/admin/config", headers=tokens[role])).status_code == 403
    assert (await client.get("/api/v1/admin/config", headers=tokens["admin"])).status_code == 200


@pytest.mark.asyncio
async def test_cross_customer_404_transfers_and_audit_tamper(client: AsyncClient) -> None:
    from app.main import app
    from app.core.database import get_db

    tenant = "tenant_matrix_02"
    async for db in app.dependency_overrides[get_db]():
        await BankingService.bank_api.seed_dev_data(db, tenant)
        await db.commit()
        accts = (
            await db.execute(select(BankAccount).where(BankAccount.tenant_id == tenant))
        ).scalars().all()
        c1_accts = [a for a in accts if a.customer_id == "cust_user_01"]
        c2_accts = [a for a in accts if a.customer_id == "cust_user_02"]
        c1_checking_id = c1_accts[0].id
        c1_savings_id = c1_accts[1].id
        c2_checking_id = c2_accts[0].id
        break

    cust1 = _auth("cust_user_01", "customer", tenant)
    admin1 = _auth("admin_01", "admin", tenant)
    admin2 = _auth("admin_02", "admin", tenant)

    # Cross-customer account access returns 404
    r_other_acct = await client.get(f"/api/v1/accounts/{c2_checking_id}", headers=cust1)
    assert r_other_acct.status_code == 404

    # High-risk transfer requested by admin1 -> pending_approval -> admin1 self-approve blocked (403) -> admin2 approves (200)
    r_xfer = await client.post(
        "/api/v1/transfers",
        headers=admin1,
        json={
            "from_account_id": c1_checking_id,
            "to_account_id": c1_savings_id,
            "amount_minor": 150_000,
            "currency": "USD",
            "reference": "API high risk test",
        },
    )
    assert r_xfer.status_code == 200
    xfer_id = r_xfer.json()["data"]["id"]
    assert r_xfer.json()["data"]["status"] == "pending_approval"

    r_self = await client.post(f"/api/v1/approvals/{xfer_id}/approve", headers=admin1)
    assert r_self.status_code == 403

    r_approve = await client.post(f"/api/v1/approvals/{xfer_id}/approve", headers=admin2)
    assert r_approve.status_code == 200
    assert r_approve.json()["data"]["status"] == "executed"

    # Audit chain verify valid -> tamper -> invalid
    r_verify_ok = await client.get("/api/v1/audit/verify", headers=admin2)
    assert r_verify_ok.status_code == 200
    assert r_verify_ok.json()["data"]["valid"] is True

    async for db in app.dependency_overrides[get_db]():
        latest = (
            await db.execute(
                select(AuditLog).where(AuditLog.tenant_id == tenant).limit(1)
            )
        ).scalar_one()
        latest_id = latest.id
        latest.status = "TAMPERED"
        await db.commit()
        break

    r_verify_bad = await client.get("/api/v1/audit/verify", headers=admin2)
    assert r_verify_bad.status_code == 200
    assert r_verify_bad.json()["data"]["valid"] is False
    assert r_verify_bad.json()["data"]["broken_at_id"] == latest_id
