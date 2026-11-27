import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthenticatedUser, STAFF_ROLES
from app.core.config import settings
from app.models.banking import (
    BankAccount,
    BankTransaction,
    BankTransfer,
    BankCard,
    RiskAlert,
    PolicyDocument,
    PolicyChunk,
)
from app.models.customer import Customer
from app.services.banking.mock_bank import MockBankingAPI
from app.services.enterprise.admin import EnterpriseAdminService


class AccessDeniedError(Exception):
    pass


class ResourceNotFoundError(Exception):
    pass


class ValidationRuleError(Exception):
    pass


class ConflictRuleError(Exception):
    pass


def mask_email(email: Optional[str]) -> Optional[str]:
    if not email or "@" not in email:
        return None
    local, domain = email.split("@", 1)
    prefix = local[:2] if len(local) >= 2 else local[:1]
    return f"{prefix}***@{domain}"


class BankingService:
    """
    Core banking business & security service layer.
    Enforces ownership, staff-reason auditing, minor-unit money math, and maker-checker approvals.
    """

    bank_api = MockBankingAPI()

    @classmethod
    async def record_audit(
        cls,
        db: AsyncSession,
        user: AuthenticatedUser,
        event_type: str,
        target_resource: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        await EnterpriseAdminService.record_audit_event(
            tenant_id=user.tenant_id,
            actor_id=user.id,
            actor_email=user.email,
            actor_role=user.role,
            event_type=event_type,
            target_resource=target_resource,
            status=status,
            details=details or {},
            db=db,
        )

    @classmethod
    async def resolve_customer_id_for_user(
        cls, db: AsyncSession, user: AuthenticatedUser
    ) -> Optional[str]:
        res = await db.execute(
            select(Customer.id).where(
                Customer.tenant_id == user.tenant_id,
                Customer.external_id == user.id,
            )
        )
        return res.scalar_one_or_none()

    @classmethod
    async def require_staff_reason_or_audit_deny(
        cls,
        db: AsyncSession,
        user: AuthenticatedUser,
        reason: Optional[str],
        resource: str,
    ) -> str:
        if not reason or not reason.strip():
            await cls.record_audit(
                db,
                user,
                event_type="STAFF_ACCESS_DENIED",
                target_resource=resource,
                status="DENIED",
                details={"reason_missing": True},
            )
            await db.commit()
            raise AccessDeniedError("Staff access to customer data requires a written reason.")
        clean = reason.strip()
        await cls.record_audit(
            db,
            user,
            event_type="STAFF_ACCESS_WITH_REASON",
            target_resource=resource,
            status="SUCCESS",
            details={"access_reason": clean, "flagged_staff_access": True},
        )
        return clean

    @classmethod
    async def list_accounts(
        cls,
        db: AsyncSession,
        user: AuthenticatedUser,
        reason: Optional[str] = None,
    ) -> List[BankAccount]:
        if user.role == "customer":
            cid = await cls.resolve_customer_id_for_user(db, user)
            if not cid:
                await cls.record_audit(db, user, "ACCOUNT_LIST", "accounts", "SUCCESS", {"count": 0})
                await db.commit()
                return []
            accounts = await cls.bank_api.list_accounts(db, user.tenant_id, customer_id=cid)
            await cls.record_audit(db, user, "ACCOUNT_LIST", "accounts", "SUCCESS", {"customer_id": cid})
            await db.commit()
            return accounts

        if user.role in STAFF_ROLES:
            await cls.require_staff_reason_or_audit_deny(db, user, reason, "accounts:all")
            accounts = await cls.bank_api.list_accounts(db, user.tenant_id)
            await db.commit()
            return accounts

        await cls.record_audit(db, user, "ACCOUNT_LIST", "accounts", "DENIED", {"role": user.role})
        await db.commit()
        raise AccessDeniedError("Unauthorized role")

    @classmethod
    async def get_account(
        cls,
        db: AsyncSession,
        user: AuthenticatedUser,
        account_id: str,
        reason: Optional[str] = None,
    ) -> BankAccount:
        acct = await cls.bank_api.get_account(db, user.tenant_id, account_id)
        if not acct:
            await cls.record_audit(db, user, "ACCOUNT_READ", f"account:{account_id}", "DENIED", {"reason": "not_found"})
            await db.commit()
            raise ResourceNotFoundError("Account not found")

        if user.role == "customer":
            cid = await cls.resolve_customer_id_for_user(db, user)
            if not cid or acct.customer_id != cid:
                await cls.record_audit(
                    db,
                    user,
                    "ACCOUNT_READ",
                    f"account:{account_id}",
                    "DENIED",
                    {"reason": "ownership_mismatch"},
                )
                await db.commit()
                # Return 404 to prevent existence enumeration of another customer's account
                raise ResourceNotFoundError("Account not found")
            await cls.record_audit(db, user, "ACCOUNT_READ", f"account:{account_id}", "SUCCESS")
            await db.commit()
            return acct

        await cls.require_staff_reason_or_audit_deny(db, user, reason, f"account:{account_id}")
        await db.commit()
        return acct

    @classmethod
    async def list_transactions(
        cls,
        db: AsyncSession,
        user: AuthenticatedUser,
        account_id: Optional[str] = None,
        min_amount_minor: Optional[int] = None,
        max_amount_minor: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
        reason: Optional[str] = None,
    ) -> Tuple[List[BankTransaction], int]:
        customer_id: Optional[str] = None
        if user.role == "customer":
            customer_id = await cls.resolve_customer_id_for_user(db, user)
            if account_id:
                acct = await cls.bank_api.get_account(db, user.tenant_id, account_id)
                if not acct or acct.customer_id != customer_id:
                    await cls.record_audit(
                        db, user, "TRANSACTION_LIST", f"account:{account_id}", "DENIED", {"reason": "ownership_mismatch"}
                    )
                    await db.commit()
                    raise ResourceNotFoundError("Account not found")
            if not customer_id:
                return [], 0
            await cls.record_audit(db, user, "TRANSACTION_LIST", "transactions", "SUCCESS")
        else:
            await cls.require_staff_reason_or_audit_deny(db, user, reason, "transactions")

        items, total = await cls.bank_api.list_transactions(
            db,
            user.tenant_id,
            account_id=account_id,
            customer_id=customer_id,
            min_amount_minor=min_amount_minor,
            max_amount_minor=max_amount_minor,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )
        await db.commit()
        return items, total

    @classmethod
    async def create_transfer(
        cls,
        db: AsyncSession,
        user: AuthenticatedUser,
        from_account_id: str,
        to_account_id: str,
        amount_minor: int,
        currency: str,
        reference: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        is_cross_border: bool = False,
    ) -> BankTransfer:
        if is_cross_border and (
            not settings.ENABLE_CROSS_BORDER_TRANSFERS or not settings.ENABLE_SANCTIONS_SCREENING_APPROVED
        ):
            await cls.record_audit(
                db,
                user,
                "TRANSFER_CREATE",
                f"transfer:{from_account_id}",
                "DENIED",
                {"reason": "cross_border_disabled"},
            )
            await db.commit()
            raise AccessDeniedError("Cross-border transfers are disabled until sanctions review is approved.")

        if idempotency_key:
            existing_res = await db.execute(
                select(BankTransfer).where(
                    BankTransfer.tenant_id == user.tenant_id,
                    BankTransfer.requested_by_user_id == user.id,
                    BankTransfer.idempotency_key == idempotency_key,
                )
            )
            existing_xfer = existing_res.scalar_one_or_none()
            if existing_xfer is not None:
                return existing_xfer

        if amount_minor <= 0:
            raise ValidationRuleError("Transfer amount must be positive integer minor units.")
        if from_account_id == to_account_id:
            raise ValidationRuleError("Source and destination accounts must differ.")

        src = await cls.bank_api.get_account(db, user.tenant_id, from_account_id)
        dst = await cls.bank_api.get_account(db, user.tenant_id, to_account_id)
        if not src or not dst:
            await cls.record_audit(db, user, "TRANSFER_CREATE", f"transfer:{from_account_id}", "DENIED", {"reason": "account_not_found"})
            await db.commit()
            raise ResourceNotFoundError("Account not found")

        if user.role == "customer":
            cid = await cls.resolve_customer_id_for_user(db, user)
            if not cid or src.customer_id != cid:
                await cls.record_audit(db, user, "TRANSFER_CREATE", f"account:{from_account_id}", "DENIED", {"reason": "ownership_mismatch"})
                await db.commit()
                raise ResourceNotFoundError("Account not found")

        curr = currency.upper()
        if src.currency != curr or dst.currency != curr:
            await cls.record_audit(db, user, "TRANSFER_CREATE", f"account:{from_account_id}", "DENIED", {"reason": "currency_mismatch"})
            await db.commit()
            raise ValidationRuleError("Currency mismatch between accounts and transfer request.")

        if src.balance_minor < amount_minor:
            await cls.record_audit(db, user, "TRANSFER_CREATE", f"account:{from_account_id}", "DENIED", {"reason": "insufficient_funds"})
            await db.commit()
            raise ValidationRuleError("Insufficient funds.")

        is_high_risk = amount_minor >= settings.HIGH_RISK_TRANSFER_MINOR
        risk_score = min(95, 15 + (amount_minor // 5000))
        transfer = BankTransfer(
            id=str(uuid.uuid4()),
            tenant_id=user.tenant_id,
            from_account_id=src.id,
            to_account_id=dst.id,
            customer_id=src.customer_id,
            requested_by_user_id=user.id,
            amount_minor=amount_minor,
            currency=curr,
            reference=reference,
            status="pending_approval" if is_high_risk else "completed",
            risk_score=risk_score,
            idempotency_key=idempotency_key,
            is_cross_border=is_cross_border,
        )
        db.add(transfer)

        if is_high_risk:
            db.add(
                RiskAlert(
                    id=str(uuid.uuid4()),
                    tenant_id=user.tenant_id,
                    customer_id=src.customer_id,
                    account_id=src.id,
                    transfer_id=transfer.id,
                    severity="high",
                    risk_score=risk_score,
                    summary=f"High-value transfer ({amount_minor} {curr}) awaiting maker-checker approval",
                    status="open",
                )
            )
            await cls.record_audit(
                db, user, "TRANSFER_PENDING_APPROVAL", f"transfer:{transfer.id}", "SUCCESS", {"amount_minor": amount_minor}
            )
        else:
            src.balance_minor -= amount_minor
            dst.balance_minor += amount_minor
            now = datetime.now(timezone.utc)
            db.add_all(
                [
                    BankTransaction(
                        id=str(uuid.uuid4()),
                        tenant_id=user.tenant_id,
                        account_id=src.id,
                        customer_id=src.customer_id,
                        tx_type="transfer",
                        amount_minor=amount_minor,
                        currency=curr,
                        description=reference or f"Transfer to {dst.account_number_masked}",
                        counterparty_masked=dst.account_number_masked,
                        occurred_at=now,
                    ),
                    BankTransaction(
                        id=str(uuid.uuid4()),
                        tenant_id=user.tenant_id,
                        account_id=dst.id,
                        customer_id=dst.customer_id,
                        tx_type="credit",
                        amount_minor=amount_minor,
                        currency=curr,
                        description=reference or f"Transfer from {src.account_number_masked}",
                        counterparty_masked=src.account_number_masked,
                        occurred_at=now,
                    ),
                ]
            )
            await cls.record_audit(
                db, user, "TRANSFER_COMPLETED", f"transfer:{transfer.id}", "SUCCESS", {"amount_minor": amount_minor}
            )

        await db.commit()
        await db.refresh(transfer)
        return transfer

    @classmethod
    async def decide_transfer_approval(
        cls,
        db: AsyncSession,
        approver: AuthenticatedUser,
        transfer_id: str,
        approve: bool,
        reason: Optional[str] = None,
    ) -> BankTransfer:
        res = await db.execute(
            select(BankTransfer).where(
                BankTransfer.id == transfer_id,
                BankTransfer.tenant_id == approver.tenant_id,
            )
        )
        transfer = res.scalar_one_or_none()
        if not transfer:
            await cls.record_audit(db, approver, "TRANSFER_APPROVAL", f"transfer:{transfer_id}", "DENIED", {"reason": "not_found"})
            await db.commit()
            raise ResourceNotFoundError("Transfer not found")

        if transfer.requested_by_user_id == approver.id:
            await cls.record_audit(db, approver, "TRANSFER_APPROVAL", f"transfer:{transfer_id}", "DENIED", {"reason": "SELF_APPROVAL_FORBIDDEN"})
            await db.commit()
            raise AccessDeniedError("SELF_APPROVAL_FORBIDDEN: Requester cannot approve or reject their own transfer.")

        if transfer.status != "pending_approval":
            raise ConflictRuleError(f"Transfer is already '{transfer.status}'.")

        if approve:
            src = await cls.bank_api.get_account(db, approver.tenant_id, transfer.from_account_id)
            dst = await cls.bank_api.get_account(db, approver.tenant_id, transfer.to_account_id)
            if not src or not dst or src.balance_minor < transfer.amount_minor:
                transfer.status = "failed"
                await cls.record_audit(db, approver, "TRANSFER_APPROVAL", f"transfer:{transfer_id}", "DENIED", {"reason": "insufficient_funds"})
                await db.commit()
                raise ValidationRuleError("Insufficient funds at approval time.")
            src.balance_minor -= transfer.amount_minor
            dst.balance_minor += transfer.amount_minor
            transfer.status = "completed"
            transfer.approved_by_user_id = approver.id
            await cls.record_audit(db, approver, "TRANSFER_APPROVED", f"transfer:{transfer_id}", "SUCCESS", {"reason": reason})
        else:
            transfer.status = "rejected"
            transfer.approved_by_user_id = approver.id
            transfer.rejection_reason = reason or "Rejected by approver"
            await cls.record_audit(db, approver, "TRANSFER_REJECTED", f"transfer:{transfer_id}", "SUCCESS", {"reason": reason})

        await db.commit()
        await db.refresh(transfer)
        return transfer

    @classmethod
    async def list_cards(
        cls, db: AsyncSession, user: AuthenticatedUser, reason: Optional[str] = None
    ) -> List[BankCard]:
        if user.role == "customer":
            cid = await cls.resolve_customer_id_for_user(db, user)
            if not cid:
                return []
            cards = await cls.bank_api.list_cards(db, user.tenant_id, customer_id=cid)
            await cls.record_audit(db, user, "CARD_LIST", "cards", "SUCCESS")
            await db.commit()
            return cards

        await cls.require_staff_reason_or_audit_deny(db, user, reason, "cards:all")
        cards = await cls.bank_api.list_cards(db, user.tenant_id)
        await db.commit()
        return cards

    @classmethod
    async def update_card_status(
        cls,
        db: AsyncSession,
        user: AuthenticatedUser,
        card_id: str,
        new_status: str,
    ) -> BankCard:
        res = await db.execute(
            select(BankCard).where(BankCard.id == card_id, BankCard.tenant_id == user.tenant_id)
        )
        card = res.scalar_one_or_none()
        if not card:
            await cls.record_audit(db, user, "CARD_STATUS_UPDATE", f"card:{card_id}", "DENIED", {"reason": "not_found"})
            await db.commit()
            raise ResourceNotFoundError("Card not found")

        if user.role == "customer":
            cid = await cls.resolve_customer_id_for_user(db, user)
            if not cid or card.customer_id != cid:
                await cls.record_audit(db, user, "CARD_STATUS_UPDATE", f"card:{card_id}", "DENIED", {"reason": "ownership_mismatch"})
                await db.commit()
                raise ResourceNotFoundError("Card not found")

        card.status = new_status
        await cls.record_audit(db, user, "CARD_STATUS_UPDATE", f"card:{card_id}", "SUCCESS", {"status": new_status})
        await db.commit()
        await db.refresh(card)
        return card

    @classmethod
    async def upload_policy(
        cls,
        db: AsyncSession,
        user: AuthenticatedUser,
        title: str,
        filename: str,
        pages: List[str],
    ) -> PolicyDocument:
        pol = PolicyDocument(
            id=str(uuid.uuid4()),
            tenant_id=user.tenant_id,
            title=title,
            filename=filename,
            status="pending",
            uploaded_by_user_id=user.id,
            page_count=len(pages),
        )
        db.add(pol)
        await db.flush()
        for idx, page_text in enumerate(pages, start=1):
            db.add(
                PolicyChunk(
                    id=str(uuid.uuid4()),
                    tenant_id=user.tenant_id,
                    policy_id=pol.id,
                    page_number=idx,
                    chunk_index=idx - 1,
                    content=page_text,
                    embedding=[],
                )
            )
        await cls.record_audit(db, user, "POLICY_UPLOADED", f"policy:{pol.id}", "SUCCESS", {"title": title})
        await db.commit()
        await db.refresh(pol)
        return pol

    @classmethod
    async def review_policy(
        cls,
        db: AsyncSession,
        user: AuthenticatedUser,
        policy_id: str,
        approve: bool,
        reason: Optional[str] = None,
    ) -> PolicyDocument:
        res = await db.execute(
            select(PolicyDocument).where(
                PolicyDocument.id == policy_id, PolicyDocument.tenant_id == user.tenant_id
            )
        )
        pol = res.scalar_one_or_none()
        if not pol:
            raise ResourceNotFoundError("Policy document not found")
        if pol.uploaded_by_user_id == user.id:
            await cls.record_audit(db, user, "POLICY_REVIEW", f"policy:{policy_id}", "DENIED", {"reason": "SELF_APPROVAL_FORBIDDEN"})
            await db.commit()
            raise AccessDeniedError("SELF_APPROVAL_FORBIDDEN: Uploader cannot approve their own policy.")
        pol.status = "approved" if approve else "rejected"
        pol.reviewed_by_user_id = user.id
        pol.review_reason = reason
        await cls.record_audit(
            db, user, "POLICY_APPROVED" if approve else "POLICY_REJECTED", f"policy:{policy_id}", "SUCCESS"
        )
        await db.commit()
        await db.refresh(pol)
        return pol
