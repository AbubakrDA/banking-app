from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import AuthenticatedUser, require_roles, get_staff_access_reason, STAFF_ROLES
from app.models.banking import BankTransfer
from app.schemas.envelope import APIResponse
from app.schemas.banking import BankTransferRead, TransferCreateRequest
from app.services.banking.service import BankingService, AccessDeniedError

router = APIRouter()


@router.get("", response_model=APIResponse[List[BankTransferRead]])
async def list_transfers(
    request: Request,
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
    current_user: AuthenticatedUser = Depends(require_roles("customer", "employee", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[BankTransferRead]:
    transfer = await BankingService.create_transfer(
        db,
        current_user,
        from_account_id=payload.from_account_id,
        to_account_id=payload.to_account_id,
        amount_minor=payload.amount_minor,
        currency=payload.currency,
        reference=payload.reference,
    )
    await db.commit()
    return APIResponse.ok(
        data=BankTransferRead.model_validate(transfer),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
