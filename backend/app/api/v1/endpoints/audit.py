from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import AuthenticatedUser, require_roles, require_surface
from app.models.enterprise import AuditLog
from app.schemas.envelope import APIResponse

router = APIRouter()


class AuditEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    actor_id: str
    actor_role: str
    event_type: str
    target_resource: str
    status: str
    details: Optional[Dict[str, Any]] = None
    prev_hash: Optional[str] = None
    event_hash: str
    created_at: datetime


class AuditChainVerifyResponse(BaseModel):
    valid: bool
    checked_count: int
    broken_at_id: Optional[str] = None


@router.get("", response_model=APIResponse[List[AuditEntryRead]])
async def list_audit_logs(
    request: Request,
    limit: int = Query(100, ge=1, le=500),
    current_user: AuthenticatedUser = Depends(require_roles("risk_officer", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[AuditEntryRead]]:
    res = await db.execute(
        select(AuditLog)
        .where(AuditLog.tenant_id == current_user.tenant_id)
        .order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
        .limit(limit)
    )
    entries = list(res.scalars().all())
    return APIResponse.ok(
        data=[AuditEntryRead.model_validate(e) for e in entries],
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/verify", response_model=APIResponse[AuditChainVerifyResponse])
async def verify_audit_chain(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("risk_officer", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[AuditChainVerifyResponse]:
    res = await db.execute(
        select(AuditLog)
        .where(AuditLog.tenant_id == current_user.tenant_id)
        .order_by(AuditLog.hash_timestamp.asc(), AuditLog.created_at.asc(), AuditLog.id.asc())
    )
    entries = list(res.scalars().all())

    expected_prev = "0" * 64
    for entry in entries:
        if entry.prev_hash != expected_prev:
            return APIResponse.ok(
                data=AuditChainVerifyResponse(
                    valid=False,
                    checked_count=len(entries),
                    broken_at_id=entry.id,
                ),
                request_id=getattr(request.state, "request_id", None),
                tenant_id=current_user.tenant_id,
            )
        recomputed = AuditLog.compute_event_hash(
            prev_hash=entry.prev_hash or ("0" * 64),
            tenant_id=entry.tenant_id,
            actor_id=entry.actor_id,
            event_type=entry.event_type,
            target_resource=entry.target_resource,
            status=entry.status,
            hash_timestamp=entry.hash_timestamp or "",
        )
        if recomputed != entry.event_hash:
            return APIResponse.ok(
                data=AuditChainVerifyResponse(
                    valid=False,
                    checked_count=len(entries),
                    broken_at_id=entry.id,
                ),
                request_id=getattr(request.state, "request_id", None),
                tenant_id=current_user.tenant_id,
            )
        expected_prev = entry.event_hash

    return APIResponse.ok(
        data=AuditChainVerifyResponse(
            valid=True,
            checked_count=len(entries),
            broken_at_id=None,
        ),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
