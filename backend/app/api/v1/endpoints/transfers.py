from typing import List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.mfa import get_mfa_provider
from app.core.auth import AuthenticatedUser, require_roles, require_surface, get_staff_access_reason, STAFF_ROLES
from app.models.banking import BankTransfer
from app.schemas.envelope import APIResponse
from app.schemas.banking import BankTransferRead, TransferCreateRequest
from app.services.banking.service import BankingService, AccessDeniedError

router = APIRouter()


@router.get("", response_model=APIResponse[List[BankTransferRead]])
async def list_transfers(
    request: Request,
    _surface: AuthenticatedUser = Depends(require_surface("both")),
    current_user: AuthenticatedUser = Depends(require_roles("customer", "employee", "risk_officer", "admin")),
    reason: Optional[str] = Depends(get_staff_access_reason),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[BankTransferRead]]:
    stmt = select(BankTransfer).where(BankTransfer.tenant_id == current_user.tenant_id)
    if current_user.role == "customer":
        stmt = stmt.where(BankTransfer.customer_id == current_user.user_id)
    elif current_user.role in STAFF_ROLES:
        if not reason or not reason.strip():
            await BankingService.record_audit(
                db,
                current_user,
                event_type="STAFF_TRANSFERS_READ",
                target_resource="transfers:all",
                status="DENIED",
                details={"reason": "missing_access_reason"},
            )
            await db.commit()
            raise AccessDeniedError("Staff access to transfers requires a written reason")
        await BankingService.record_audit(
            db,
            current_user,
            event_type="STAFF_TRANSFERS_READ",
            target_resource="transfers:all",
            status="SUCCESS",
            details={"staff_access": True, "reason": reason.strip()},
        )

    res = await db.execute(stmt.order_by(BankTransfer.created_at.desc()))
    transfers = list(res.scalars().all())
    await db.commit()
    return APIResponse.ok(
        data=[BankTransferRead.model_validate(t) for t in transfers],
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("", response_model=APIResponse[BankTransferRead])
async def create_transfer(
    payload: TransferCreateRequest,
    request: Request,
    x_idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    x_mfa_code: Optional[str] = Header(default=None, alias="X-MFA-Code"),
    _surface: AuthenticatedUser = Depends(require_surface("customer")),
    current_user: AuthenticatedUser = Depends(require_roles("customer")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[BankTransferRead]:
    if settings.ENABLE_MFA_VERIFICATION and payload.amount_minor >= settings.HIGH_RISK_TRANSFER_MINOR:
        mfa_ok = await get_mfa_provider(settings).verify(
            user_id=current_user.user_id, action="high_risk_transfer", code=x_mfa_code
        )
        if not mfa_ok:
            await BankingService.record_audit(
                db, current_user, "MFA_CHALLENGE_FAILED", "transfer:high_risk", "DENIED"
            )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="MFA verification required for high-risk transfer",
            )

    transfer = await BankingService.create_transfer(
        db,
        current_user,
        from_account_id=payload.from_account_id,
        to_account_id=payload.to_account_id,
        amount_minor=payload.amount_minor,
        currency=payload.currency,
        reference=payload.reference,
        idempotency_key=(x_idempotency_key or payload.idempotency_key),
        is_cross_border=payload.is_cross_border,
    )
    await db.commit()
    return APIResponse.ok(
        data=BankTransferRead.model_validate(transfer),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
