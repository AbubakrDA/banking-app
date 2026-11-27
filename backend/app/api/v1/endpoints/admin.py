from typing import List
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.core.auth import AuthenticatedUser, require_roles, BANKING_ROLES
from app.models.user import User
from app.schemas.envelope import APIResponse
from app.schemas.auth import UserRead

router = APIRouter()


class BankingSystemConfigRead(BaseModel):
    environment: str
    high_risk_transfer_minor: int
    llm_provider: str
    roles: List[str]


@router.get("/users", response_model=APIResponse[List[UserRead]])
async def list_admin_users(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[UserRead]]:
    res = await db.execute(
        select(User).where(User.tenant_id == current_user.tenant_id)
    )
    users = list(res.scalars().all())
    return APIResponse.ok(
        data=[UserRead.model_validate(u) for u in users],
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/config", response_model=APIResponse[BankingSystemConfigRead])
async def get_admin_config(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
) -> APIResponse[BankingSystemConfigRead]:
    return APIResponse.ok(
        data=BankingSystemConfigRead(
            environment=settings.ENVIRONMENT,
            high_risk_transfer_minor=settings.HIGH_RISK_TRANSFER_MINOR,
            llm_provider=settings.LLM_PROVIDER,
            roles=sorted(BANKING_ROLES),
        ),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
