from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthenticatedUser, require_roles, require_surface
from app.core.database import get_db
from app.models.tenant import Tenant
from app.schemas.envelope import APIResponse

router = APIRouter()


class TenantContextInfo(BaseModel):
    tenant_id: str
    name: str
    business_mode: str
    status: str


@router.get("/current", response_model=APIResponse[TenantContextInfo])
async def get_current_tenant(
    request: Request,
    _surface: AuthenticatedUser = Depends(require_surface("staff")),
    current_user: AuthenticatedUser = Depends(require_roles("employee", "risk_officer", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TenantContextInfo]:
    res = await db.execute(select(Tenant).where(Tenant.id == current_user.tenant_id))
    tenant = res.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    data = TenantContextInfo(
        tenant_id=tenant.id,
        name=tenant.name,
        business_mode=tenant.business_mode,
        status=tenant.status,
    )
    return APIResponse.ok(
        data=data,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=tenant.id,
    )
