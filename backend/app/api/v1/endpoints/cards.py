from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import AuthenticatedUser, require_roles, get_staff_access_reason
from app.schemas.envelope import APIResponse
from app.schemas.banking import BankCardRead, CardStatusUpdateRequest
from app.services.banking.service import BankingService

router = APIRouter()


@router.get("", response_model=APIResponse[List[BankCardRead]])
async def list_cards(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("customer", "employee", "risk_officer", "admin")),
    reason: Optional[str] = Depends(get_staff_access_reason),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[BankCardRead]]:
    cards = await BankingService.list_cards(db, current_user, reason=reason)
    await db.commit()
    return APIResponse.ok(
        data=[BankCardRead.model_validate(c) for c in cards],
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.patch("/{card_id}/status", response_model=APIResponse[BankCardRead])
async def update_card_status(
    card_id: str,
    payload: CardStatusUpdateRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("customer", "employee", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[BankCardRead]:
    card = await BankingService.update_card_status(db, current_user, card_id, payload.status)
    await db.commit()
    return APIResponse.ok(
        data=BankCardRead.model_validate(card),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
