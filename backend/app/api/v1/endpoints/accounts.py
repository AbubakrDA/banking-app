from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import AuthenticatedUser, require_roles, require_surface, get_staff_access_reason
from app.schemas.envelope import APIResponse
from app.schemas.banking import BankAccountRead
from app.services.banking.service import BankingService

router = APIRouter()


@router.get("", response_model=APIResponse[List[BankAccountRead]])
async def list_accounts(
    request: Request,
    _surface: AuthenticatedUser = Depends(require_surface("both")),
    current_user: AuthenticatedUser = Depends(require_roles("customer", "employee", "risk_officer", "admin")),
    reason: Optional[str] = Depends(get_staff_access_reason),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[BankAccountRead]]:
    accounts = await BankingService.list_accounts(db, current_user, reason=reason)
    await db.commit()
    return APIResponse.ok(
        data=[BankAccountRead.model_validate(a) for a in accounts],
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/{account_id}", response_model=APIResponse[BankAccountRead])
async def get_account(
    account_id: str,
    request: Request,
    _surface: AuthenticatedUser = Depends(require_surface("both")),
    current_user: AuthenticatedUser = Depends(require_roles("customer", "employee", "risk_officer", "admin")),
    reason: Optional[str] = Depends(get_staff_access_reason),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[BankAccountRead]:
    account = await BankingService.get_account(db, current_user, account_id, reason=reason)
    await db.commit()
    return APIResponse.ok(
        data=BankAccountRead.model_validate(account),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
