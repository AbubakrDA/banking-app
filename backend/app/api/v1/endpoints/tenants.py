from fastapi import APIRouter, Request
from pydantic import BaseModel
from app.schemas.envelope import APIResponse

router = APIRouter()


class TenantContextInfo(BaseModel):
    tenant_id: str
    name: str
    business_mode: str
    status: str


@router.get("/current", response_model=APIResponse[TenantContextInfo])
async def get_current_tenant(request: Request) -> APIResponse[TenantContextInfo]:
    tenant_id = getattr(request.state, "tenant_id", "tenant_enterprise_01")
    data = TenantContextInfo(
        tenant_id=tenant_id,
        name="Acme Global Ltd",
        business_mode="hybrid",
        status="active",
    )
    return APIResponse.ok(
        data=data,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=tenant_id,
    )
