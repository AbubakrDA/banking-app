import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.core.security import create_access_token
from app.models.banking import BankAccount
from app.models.enterprise import AuditLog
from app.services.banking.service import BankingService


def _auth(user_id: str, role: str, tenant_id: str) -> dict:
    token = create_access_token(
        subject=user_id,
        tenant_id=tenant_id,
        role=role,
        email=f"{user_id}@bank.local",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_account_ownership_and_staff_override_reason(client: AsyncClient) -> None:
    from app.main import app
    from app.core.database import get_db

    tenant = "tenant_ownership_01"
    async for db in app.dependency_overrides[get_db]():
        await BankingService.bank_api.seed_dev_data(db, tenant)
        await db.commit()
        accts = (
            await db.execute(select(BankAccount).where(BankAccount.tenant_id == tenant))
        ).scalars().all()
        c1_acct = next(a.id for a in accts if a.account_number_masked == "****1042")
        c2_acct = next(a.id for a in accts if a.account_number_masked == "****3099")
        break

    cust1 = _auth("cust_user_01", "customer", tenant)
    emp = _auth("emp_01", "employee", tenant)
    risk = _auth("risk_01", "risk_officer", tenant)

    # 1. Customer reads own account -> 200
    r_own = await client.get(f"/api/v1/accounts/{c1_acct}", headers=cust1)
    assert r_own.status_code == 200

    # 2. Customer reads another customer's account -> 404
    r_other = await client.get(f"/api/v1/accounts/{c2_acct}", headers=cust1)
    assert r_other.status_code == 404

    # 3. Staff without X-Override-Reason -> 403
    r_no_reason = await client.get(f"/api/v1/accounts/{c1_acct}", headers=emp)
    assert r_no_reason.status_code == 403

    # 4. Staff with X-Override-Reason -> 200 and audited
    r_with_reason = await client.get(
        f"/api/v1/accounts/{c1_acct}",
        headers={**emp, "X-Override-Reason": "Customer dispute investigation"},
    )
    assert r_with_reason.status_code == 200

    async for db in app.dependency_overrides[get_db]():
        audit_entry = (
            await db.execute(
                select(AuditLog).where(
                    AuditLog.tenant_id == tenant,
                    AuditLog.actor_id == "emp_01",
                    AuditLog.status == "SUCCESS",
                )
            )
        ).scalars().first()
        assert audit_entry is not None
        assert audit_entry.details.get("staff_access") is True
        assert audit_entry.details.get("reason") == "Customer dispute investigation"
        break

    # 5. Risk officer cannot transfer -> 403
    r_risk_xfer = await client.post(
        "/api/v1/transfers",
        headers=risk,
        json={
            "from_account_id": c1_acct,
            "to_account_id": c2_acct,
            "amount_minor": 1000,
            "currency": "USD",
        },
    )
    assert r_risk_xfer.status_code == 403
