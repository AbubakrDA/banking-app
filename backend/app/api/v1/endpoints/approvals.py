from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import AuthenticatedUser, require_roles, require_surface
from app.models.banking import BankTransfer
from app.schemas.envelope import APIResponse
from app.schemas.banking import BankTransferRead, ApprovalDecisionRequest
from app.services.banking.service import BankingService

router = APIRouter()


@router.get("", response_model=APIResponse[List[BankTransferRead]])
async def list_pending_approvals(
    request: Request,
    _surface: AuthenticatedUser = Depends(require_surface("staff")),
    current_user: AuthenticatedUser = Depends(require_roles("risk_officer", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[BankTransferRead]]:
    res = await db.execute(
        select(BankTransfer)
        .where(
            BankTransfer.tenant_id == current_user.tenant_id,
            BankTransfer.status == "pending_approval",
        )
        .order_by(BankTransfer.created_at.desc())
    )
    pending = list(res.scalars().all())
    await BankingService.record_audit(
        db,
        current_user,
        event_type="APPROVALS_LIST",
        target_resource="approvals:pending",
        status="SUCCESS",
    )
    await db.commit()
    return APIResponse.ok(
        data=[BankTransferRead.model_validate(t) for t in pending],
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/{transfer_id}/approve", response_model=APIResponse[BankTransferRead])
async def approve_transfer(
    transfer_id: str,
    request: Request,
    payload: Optional[ApprovalDecisionRequest] = None,
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[BankTransferRead]:
    transfer = await BankingService.decide_transfer_approval(
        db,
        current_user,
        transfer_id,
        approve=True,
        reason=payload.reason if payload else None,
    )
    await db.commit()
    return APIResponse.ok(
        data=BankTransferRead.model_validate(transfer),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/{transfer_id}/reject", response_model=APIResponse[BankTransferRead])
async def reject_transfer(
    transfer_id: str,
    request: Request,
    payload: Optional[ApprovalDecisionRequest] = None,
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[BankTransferRead]:
    transfer = await BankingService.decide_transfer_approval(
        db,
        current_user,
        transfer_id,
        approve=False,
        reason=payload.reason if payload else None,
    )
    await db.commit()
    return APIResponse.ok(
        data=BankTransferRead.model_validate(transfer),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
