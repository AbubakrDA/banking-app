from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import require_roles, AuthenticatedUser
from app.schemas.envelope import APIResponse
from app.schemas.infrastructure import (
    InfrastructureDashboardResponse,
    ScalingPolicyResponse,
    TenantQuotaUsageResponse,
)
from app.services.infrastructure.telemetry import CloudInfrastructureService

router = APIRouter()


@router.get("/dashboard", response_model=APIResponse[InfrastructureDashboardResponse])
async def get_infrastructure_dashboard(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[InfrastructureDashboardResponse]:
    """Retrieve live cloud service health, container telemetry, and DR metrics."""
    data = await CloudInfrastructureService.get_dashboard_telemetry(db)
    return APIResponse.ok(
        data=data,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/scaling", response_model=APIResponse[ScalingPolicyResponse])
async def get_scaling_policy(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
) -> APIResponse[ScalingPolicyResponse]:
    """Retrieve AWS ECS Fargate horizontal auto-scaling policy parameters."""
    policy = CloudInfrastructureService.get_scaling_policy()
    return APIResponse.ok(
        data=policy,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/quota", response_model=APIResponse[TenantQuotaUsageResponse])
async def get_tenant_quota(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TenantQuotaUsageResponse]:
    """Measure multi-tenant storage quota and API invocation consumption."""
    quota = await CloudInfrastructureService.get_tenant_quota(current_user.tenant_id, db)
    return APIResponse.ok(
        data=quota,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
