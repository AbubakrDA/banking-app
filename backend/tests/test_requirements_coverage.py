import pytest
from httpx import AsyncClient
from sqlalchemy import select, func

from app.core.config import settings
from app.core.security import create_access_token, verify_access_token
from app.models.banking import BankAccount, BankCard, BankTransfer
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
async def test_req_C3_domestic_payments_limits_and_cross_border_off(client: AsyncClient) -> None:
    from app.main import app
    from app.core.database import get_db

    tenant = "tenant_req_c3"
    async for db in app.dependency_overrides[get_db]():
        await BankingService.bank_api.seed_dev_data(db, tenant)
        await db.commit()
        accts = (await db.execute(select(BankAccount).where(BankAccount.tenant_id == tenant))).scalars().all()
        c1_usd = next(a.id for a in accts if a.account_number_masked == "****1042")
        c2_usd = next(a.id for a in accts if a.account_number_masked == "****3099")
        break

    cust1 = _auth("cust_user_01", "customer", tenant)

    # Domestic transfer within limit -> completed
    r_ok = await client.post(
        "/api/v1/transfers",
        headers=cust1,
        json={"from_account_id": c1_usd, "to_account_id": c2_usd, "amount_minor": 1000, "currency": "USD"},
    )
    assert r_ok.status_code == 200
    assert r_ok.json()["data"]["status"] == "completed"

    # High-value transfer exceeding HIGH_RISK_TRANSFER_MINOR -> pending_approval
    r_high = await client.post(
        "/api/v1/transfers",
        headers=cust1,
        json={
            "from_account_id": c1_usd,
            "to_account_id": c2_usd,
            "amount_minor": settings.HIGH_RISK_TRANSFER_MINOR,
            "currency": "USD",
        },
    )
    assert r_high.status_code == 200
    assert r_high.json()["data"]["status"] == "pending_approval"

    # Cross-border stays off -> 403
    r_cb = await client.post(
        "/api/v1/transfers",
        headers=cust1,
        json={
            "from_account_id": c1_usd,
            "to_account_id": c2_usd,
            "amount_minor": 500,
            "currency": "USD",
            "is_cross_border": True,
        },
    )
    assert r_cb.status_code == 403


@pytest.mark.asyncio
async def test_req_C4_cards_block_unblock_audited(client: AsyncClient) -> None:
    from app.main import app
    from app.core.database import get_db

    tenant = "tenant_req_c4"
    async for db in app.dependency_overrides[get_db]():
        await BankingService.bank_api.seed_dev_data(db, tenant)
        await db.commit()
        card = (
            await db.execute(select(BankCard).where(BankCard.tenant_id == tenant).limit(1))
        ).scalar_one()
        card_id = card.id
        break

    cust1 = _auth("cust_user_01", "customer", tenant)
    r_block = await client.patch(f"/api/v1/cards/{card_id}/status", headers=cust1, json={"status": "blocked"})
    assert r_block.status_code == 200
    assert r_block.json()["data"]["status"] == "blocked"

    r_unblock = await client.patch(f"/api/v1/cards/{card_id}/status", headers=cust1, json={"status": "active"})
    assert r_unblock.status_code == 200
    assert r_unblock.json()["data"]["status"] == "active"

    async for db in app.dependency_overrides[get_db]():
        audits = (
            await db.execute(
                select(AuditLog).where(
                    AuditLog.tenant_id == tenant,
                    AuditLog.target_resource == f"card:{card_id}",
                )
            )
        ).scalars().all()
        assert len(audits) >= 2
        break


@pytest.mark.asyncio
async def test_req_C6_mfa_hook_login_and_high_risk_actions(client: AsyncClient) -> None:
    from app.main import app
    from app.core.database import get_db

    tenant = "tenant_req_c6"
    async for db in app.dependency_overrides[get_db]():
        await BankingService.bank_api.seed_dev_data(db, tenant)
        await db.commit()
        accts = (await db.execute(select(BankAccount).where(BankAccount.tenant_id == tenant))).scalars().all()
        c1_usd = next(a.id for a in accts if a.account_number_masked == "****1042")
        c2_usd = next(a.id for a in accts if a.account_number_masked == "****3099")
        break

    orig_mfa = settings.ENABLE_MFA_VERIFICATION
    try:
        settings.ENABLE_MFA_VERIFICATION = True

        # Login without MFA code -> 401
        r_no_mfa = await client.post(
            "/api/v1/auth/login",
            json={"email": "alex@banking-ai-platform.internal", "password": "validpassword123", "tenant_id": tenant},
        )
        assert r_no_mfa.status_code == 401

        # Login with valid 6-digit MFA code -> 200
        r_with_mfa = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "alex@banking-ai-platform.internal",
                "password": "validpassword123",
                "tenant_id": tenant,
                "mfa_code": "123456",
            },
        )
        assert r_with_mfa.status_code == 200

        # High-risk transfer without X-MFA-Code -> 403
        cust1 = _auth("cust_user_01", "customer", tenant)
        r_high_no_mfa = await client.post(
            "/api/v1/transfers",
            headers=cust1,
            json={
                "from_account_id": c1_usd,
                "to_account_id": c2_usd,
                "amount_minor": settings.HIGH_RISK_TRANSFER_MINOR,
                "currency": "USD",
            },
        )
        assert r_high_no_mfa.status_code == 403

        # High-risk transfer with valid X-MFA-Code -> 200
        r_high_mfa = await client.post(
            "/api/v1/transfers",
            headers={**cust1, "X-MFA-Code": "654321"},
            json={
                "from_account_id": c1_usd,
                "to_account_id": c2_usd,
                "amount_minor": settings.HIGH_RISK_TRANSFER_MINOR,
                "currency": "USD",
            },
        )
        assert r_high_mfa.status_code == 200
    finally:
        settings.ENABLE_MFA_VERIFICATION = orig_mfa


@pytest.mark.asyncio
async def test_req_C8_mobile_transfer_idempotency_key(client: AsyncClient) -> None:
    from app.main import app
    from app.core.database import get_db

    tenant = "tenant_req_c8"
    async for db in app.dependency_overrides[get_db]():
        await BankingService.bank_api.seed_dev_data(db, tenant)
        await db.commit()
        accts = (await db.execute(select(BankAccount).where(BankAccount.tenant_id == tenant))).scalars().all()
        c1_usd = next(a.id for a in accts if a.account_number_masked == "****1042")
        c2_usd = next(a.id for a in accts if a.account_number_masked == "****3099")
        break

    cust1 = _auth("cust_user_01", "customer", tenant)
    headers = {**cust1, "Idempotency-Key": "mobile-retry-c8-001"}
    payload = {"from_account_id": c1_usd, "to_account_id": c2_usd, "amount_minor": 1500, "currency": "USD"}

    r1 = await client.post("/api/v1/transfers", headers=headers, json=payload)
    r2 = await client.post("/api/v1/transfers", headers=headers, json=payload)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["data"]["id"] == r2.json()["data"]["id"]

    async for db in app.dependency_overrides[get_db]():
        cnt = (
            await db.execute(
                select(func.count(BankTransfer.id)).where(
                    BankTransfer.tenant_id == tenant,
                    BankTransfer.idempotency_key == "mobile-retry-c8-001",
                )
            )
        ).scalar()
        assert cnt == 1
        break


@pytest.mark.asyncio
async def test_req_S1_to_S15_department_isolation_and_staff_timeout(client: AsyncClient) -> None:
    # Staff login token expires in STAFF_IDLE_TIMEOUT_MINUTES (10m < 60m customer)
    r_staff_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "alex@banking-ai-platform.internal", "password": "validpassword123"},
    )
    assert r_staff_login.status_code == 200
    assert r_staff_login.json()["data"]["expires_in"] == settings.STAFF_IDLE_TIMEOUT_MINUTES * 60
    claims = verify_access_token(r_staff_login.json()["data"]["access_token"])
    assert claims is not None
    assert claims["exp"] - claims["iat"] == settings.STAFF_IDLE_TIMEOUT_MINUTES * 60

    # HR & Marketing never receive balances or transactions
    for dept in ("hr", "marketing"):
        hdrs = {**_auth(f"{dept}_1", dept, "tenant_dept"), "X-Override-Reason": "Audit"}
        assert (await client.get("/api/v1/accounts", headers=hdrs)).status_code == 403
        assert (await client.get("/api/v1/transactions", headers=hdrs)).status_code == 403
