from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import AuthenticatedUser, require_roles, require_surface
from app.models.banking import PolicyDocument
from app.schemas.envelope import APIResponse
from app.schemas.banking import PolicyDocumentCreate, PolicyDocumentRead, PolicyReviewRequest
from app.services.banking.service import BankingService

router = APIRouter()


@router.get("", response_model=APIResponse[List[PolicyDocumentRead]])
async def list_policies(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("customer", "employee", "risk_officer", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[PolicyDocumentRead]]:
    stmt = select(PolicyDocument).where(PolicyDocument.tenant_id == current_user.tenant_id)
    if current_user.role == "customer":
        stmt = stmt.where(PolicyDocument.status == "approved")
    res = await db.execute(stmt.order_by(PolicyDocument.created_at.desc()))
    policies = list(res.scalars().all())
    return APIResponse.ok(
        data=[PolicyDocumentRead.model_validate(p) for p in policies],
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("", response_model=APIResponse[PolicyDocumentRead])
async def upload_policy(
    payload: PolicyDocumentCreate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("employee", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[PolicyDocumentRead]:
    doc = await BankingService.upload_policy(
        db,
        current_user,
        title=payload.title,
        filename=payload.filename,
        pages=payload.pages,
    )
    await db.commit()
    return APIResponse.ok(
        data=PolicyDocumentRead.model_validate(doc),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/{policy_id}/approve", response_model=APIResponse[PolicyDocumentRead])
async def approve_policy(
    policy_id: str,
    request: Request,
    payload: Optional[PolicyReviewRequest] = None,
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[PolicyDocumentRead]:
    doc = await BankingService.review_policy(
        db,
        current_user,
        policy_id,
        approve=True,
        reason=payload.reason if payload else None,
    )
    await db.commit()
    return APIResponse.ok(
        data=PolicyDocumentRead.model_validate(doc),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/{policy_id}/reject", response_model=APIResponse[PolicyDocumentRead])
async def reject_policy(
    policy_id: str,
    request: Request,
    payload: Optional[PolicyReviewRequest] = None,
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[PolicyDocumentRead]:
    doc = await BankingService.review_policy(
        db,
        current_user,
        policy_id,
        approve=False,
        reason=payload.reason if payload else None,
    )
    await db.commit()
    return APIResponse.ok(
        data=PolicyDocumentRead.model_validate(doc),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
