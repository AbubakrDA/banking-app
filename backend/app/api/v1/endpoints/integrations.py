from typing import Dict, Any
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.auth import AuthenticatedUser, require_roles, require_surface
from app.schemas.envelope import APIResponse
from app.services.integrations.registry import IntegrationRegistry

router = APIRouter()


class MobileMoneyPayoutRequest(BaseModel):
    phone_masked: str = Field(..., min_length=4, max_length=32)
    amount_minor: int = Field(..., gt=0)
    currency: str = Field("SDG", min_length=3, max_length=3)


class AgentCashInRequest(BaseModel):
    agent_code: str = Field(..., min_length=2, max_length=32)
    amount_minor: int = Field(..., gt=0)
    currency: str = Field("SDG", min_length=3, max_length=3)


@router.get("/status", response_model=APIResponse[Dict[str, Any]])
async def integration_status(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_surface("staff")),
    _role: AuthenticatedUser = Depends(require_roles("employee", "risk_officer", "admin")),
) -> APIResponse[Dict[str, Any]]:
    return APIResponse.ok(
        data={
            "mobile_money_enabled": settings.ENABLE_MOBILE_MONEY_INTEGRATION,
            "mobile_money_provider": settings.MOBILE_MONEY_PROVIDER,
            "agent_network_enabled": settings.ENABLE_AGENT_NETWORK_INTEGRATION,
            "agent_network_provider": settings.AGENT_NETWORK_PROVIDER,
            "cross_border_transfers_enabled": settings.ENABLE_CROSS_BORDER_TRANSFERS,
        },
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/mobile-money/payout", response_model=APIResponse[Dict[str, Any]])
async def mobile_money_payout(
    payload: MobileMoneyPayoutRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_surface("both")),
    _role: AuthenticatedUser = Depends(require_roles("customer", "employee", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[Dict[str, Any]]:
    res = await IntegrationRegistry.call_mobile_money_payout(
        db,
        current_user,
        phone_masked=payload.phone_masked,
        amount_minor=payload.amount_minor,
        currency=payload.currency,
    )
    return APIResponse.ok(
        data=res,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/agent-network/cash-in", response_model=APIResponse[Dict[str, Any]])
async def agent_network_cash_in(
    payload: AgentCashInRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_surface("staff")),
    _role: AuthenticatedUser = Depends(require_roles("employee", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[Dict[str, Any]]:
    res = await IntegrationRegistry.call_agent_network_cash_in(
        db,
        current_user,
        agent_code=payload.agent_code,
        amount_minor=payload.amount_minor,
        currency=payload.currency,
    )
    return APIResponse.ok(
        data=res,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
