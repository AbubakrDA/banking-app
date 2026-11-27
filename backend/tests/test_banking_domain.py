import pytest
from sqlalchemy import select
from app.core.auth import AuthenticatedUser
from app.models.enterprise import AuditLog
from app.services.banking.service import (
    BankingService,
    AccessDeniedError,
    ResourceNotFoundError,
    ValidationRuleError,
)


@pytest.mark.asyncio
async def test_mock_bank_seed_and_domain_rules() -> None:
    from app.main import app
    from app.core.database import get_db

    tenant = "bank_domain_test"
    cust1 = AuthenticatedUser("cust_user_01", "layla@bank.local", "customer", tenant)
    cust2 = AuthenticatedUser("cust_user_02", "omar@bank.local", "customer", tenant)
    emp = AuthenticatedUser("emp_01", "emp@bank.local", "employee", tenant)
    adm = AuthenticatedUser("admin_01", "admin@bank.local", "admin", tenant)

    async for db in app.dependency_overrides[get_db]():
        await BankingService.bank_api.seed_dev_data(db, tenant)

        # 1. Customer 1 sees only her 2 accounts (minor units int)
        accts1 = await BankingService.list_accounts(db, cust1)
        assert len(accts1) == 2
        assert all(isinstance(a.balance_minor, int) for a in accts1)

        # 2. Customer 2 cannot read Customer 1's account -> ResourceNotFoundError + audit DENY
        with pytest.raises(ResourceNotFoundError):
            await BankingService.get_account(db, cust2, accts1[0].id)

        # 3. Employee without reason is denied -> AccessDeniedError
        with pytest.raises(AccessDeniedError):
            await BankingService.list_accounts(db, emp, reason=None)

        # 4. Employee with reason is allowed & flagged in audit log
        all_accts = await BankingService.list_accounts(db, emp, reason="Customer inquiry #441")
        assert len(all_accts) == 3

        # 5. Insufficient funds -> ValidationRuleError with NO balance change
        accts2 = await BankingService.list_accounts(db, cust2)
        before_bal = accts1[0].balance_minor
        with pytest.raises(ValidationRuleError, match="Insufficient funds"):
            await BankingService.create_transfer(db, cust1, accts1[0].id, accts2[0].id, 999_999_999, "USD")
        refreshed = await BankingService.get_account(db, cust1, accts1[0].id)
        assert refreshed.balance_minor == before_bal

        # 6. Currency mismatch -> ValidationRuleError
        with pytest.raises(ValidationRuleError, match="Currency mismatch"):
            await BankingService.create_transfer(db, cust1, accts1[1].id, accts2[0].id, 1000, "EUR")

        # 7. High-risk transfer (>= 100_000) goes to pending_approval; self-approval refused; admin approves
        tr = await BankingService.create_transfer(db, cust1, accts1[0].id, accts2[0].id, 120_000, "USD", "Rent")
        assert tr.status == "pending_approval"
        with pytest.raises(AccessDeniedError, match="SELF_APPROVAL_FORBIDDEN"):
            await BankingService.decide_transfer_approval(db, cust1, tr.id, approve=True)

        done_tr = await BankingService.decide_transfer_approval(db, adm, tr.id, approve=True, reason="Verified")
        assert done_tr.status == "completed"

        # 8. Verify audit log recorded both DENIED and flagged staff access
        audits = (await db.execute(select(AuditLog).where(AuditLog.tenant_id == tenant))).scalars().all()
        assert any(a.status == "DENIED" for a in audits)
        assert any(a.event_type == "STAFF_ACCESS_WITH_REASON" and a.details.get("flagged_staff_access") for a in audits)
        break
