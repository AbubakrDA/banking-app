from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import AuthenticatedUser, require_roles, require_surface, get_staff_access_reason
from app.models.customer import Customer
from app.schemas.envelope import APIResponse
from app.schemas.banking import CustomerMaskedRead
from app.services.banking.service import BankingService, AccessDeniedError

router = APIRouter()


def _mask_email(email: Optional[str]) -> Optional[str]:
    if not email or "@" not in email:
        return None
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        return f"***@{domain}"
    return f"{local[:2]}***@{domain}"


def _mask_national_id(customer: Customer) -> str:
    meta = customer.profile_metadata or {}
    raw = str(meta.get("national_id", ""))
    if len(raw) >= 4:
        return f"***-**-{raw[-4:]}"
    return "***-**-0000"


def _to_masked_customer(c: Customer) -> CustomerMaskedRead:
    return CustomerMaskedRead(
        id=c.id,
        name=c.name,
        email_masked=_mask_email(c.email),
        national_id_masked=_mask_national_id(c),
        tier=c.tier,
    )


@router.get("/me", response_model=APIResponse[CustomerMaskedRead])
async def get_my_customer_profile(
    request: Request,
    _surface: AuthenticatedUser = Depends(require_surface("customer")),
    current_user: AuthenticatedUser = Depends(require_roles("customer")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[CustomerMaskedRead]:
    res = await db.execute(
        select(Customer).where(
            Customer.tenant_id == current_user.tenant_id,
            Customer.external_id == current_user.user_id,
        )
    )
    customer = res.scalar_one_or_none()
    if customer is None:
        profile = CustomerMaskedRead(
            id=current_user.user_id,
            name=current_user.email.split("@")[0],
            email_masked=_mask_email(current_user.email),
            national_id_masked="***-**-0000",
            tier=current_user.role,
        )
    else:
        profile = _to_masked_customer(customer)

    await BankingService.record_audit(
        db,
        current_user,
        event_type="CUSTOMER_PROFILE_READ",
        target_resource=f"customer:{profile.id}",
        status="SUCCESS",
    )
    await db.commit()
    return APIResponse.ok(
        data=profile,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/search", response_model=APIResponse[List[CustomerMaskedRead]])
async def search_customers(
    request: Request,
    q: Optional[str] = Query(None, max_length=100),
    _surface: AuthenticatedUser = Depends(require_surface("staff")),
    current_user: AuthenticatedUser = Depends(require_roles("employee", "risk_officer", "admin")),
    reason: Optional[str] = Depends(get_staff_access_reason),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[CustomerMaskedRead]]:
    if not reason or not reason.strip():
        await BankingService.record_audit(
            db,
            current_user,
            event_type="STAFF_CUSTOMER_SEARCH",
            target_resource="customers:search",
            status="DENIED",
            details={"reason": "missing_access_reason"},
        )
        await db.commit()
        raise AccessDeniedError("Staff customer search requires a written reason")

    stmt = select(Customer).where(Customer.tenant_id == current_user.tenant_id)
    if q and q.strip():
        stmt = stmt.where(Customer.name.ilike(f"%{q.strip()}%"))
    res = await db.execute(stmt.order_by(Customer.name.asc()).limit(50))
    customers = list(res.scalars().all())

    await BankingService.record_audit(
        db,
        current_user,
        event_type="STAFF_CUSTOMER_SEARCH",
        target_resource="customers:search",
        status="SUCCESS",
        details={"staff_access": True, "reason": reason.strip(), "result_count": len(customers)},
    )
    await db.commit()
    return APIResponse.ok(
        data=[_to_masked_customer(c) for c in customers],
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
