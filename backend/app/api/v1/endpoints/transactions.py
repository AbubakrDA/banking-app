from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import AuthenticatedUser, require_roles, require_surface, get_staff_access_reason
from app.schemas.envelope import APIResponse
from app.schemas.banking import BankTransactionRead, PaginatedTransactionsResponse
from app.services.banking.service import BankingService

router = APIRouter()


@router.get("", response_model=APIResponse[PaginatedTransactionsResponse])
async def list_transactions(
    request: Request,
    account_id: Optional[str] = None,
    min_amount_minor: Optional[int] = Query(None, ge=0),
    max_amount_minor: Optional[int] = Query(None, ge=0),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _surface: AuthenticatedUser = Depends(require_surface("both")),
    current_user: AuthenticatedUser = Depends(require_roles("customer", "employee", "risk_officer", "admin")),
    reason: Optional[str] = Depends(get_staff_access_reason),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[PaginatedTransactionsResponse]:
    items, total = await BankingService.list_transactions(
        db,
        current_user,
        account_id=account_id,
        min_amount_minor=min_amount_minor,
        max_amount_minor=max_amount_minor,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
        reason=reason,
    )
    await db.commit()
    return APIResponse.ok(
        data=PaginatedTransactionsResponse(
            items=[BankTransactionRead.model_validate(tx) for tx in items],
            total=total,
            page=page,
            page_size=page_size,
        ),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
