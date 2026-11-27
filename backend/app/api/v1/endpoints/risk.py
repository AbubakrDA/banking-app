from typing import List
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import AuthenticatedUser, require_roles
from app.models.banking import RiskAlert
from app.schemas.envelope import APIResponse
from app.schemas.banking import RiskAlertRead
from app.services.banking.service import BankingService, ResourceNotFoundError

router = APIRouter()


class RiskAlertUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(open|investigating|closed)$")


@router.get("/alerts", response_model=APIResponse[List[RiskAlertRead]])
async def list_risk_alerts(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("risk_officer", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[RiskAlertRead]]:
    res = await db.execute(
        select(RiskAlert)
        .where(RiskAlert.tenant_id == current_user.tenant_id)
        .order_by(RiskAlert.created_at.desc())
    )
    alerts = list(res.scalars().all())
    await BankingService.record_audit(
        db,
        current_user,
        event_type="RISK_ALERTS_READ",
        target_resource="risk_alerts:all",
        status="SUCCESS",
    )
    await db.commit()
    return APIResponse.ok(
        data=[RiskAlertRead.model_validate(a) for a in alerts],
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.patch("/alerts/{alert_id}", response_model=APIResponse[RiskAlertRead])
async def update_risk_alert(
    alert_id: str,
    payload: RiskAlertUpdateRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("risk_officer", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[RiskAlertRead]:
    res = await db.execute(
        select(RiskAlert).where(
            RiskAlert.id == alert_id,
            RiskAlert.tenant_id == current_user.tenant_id,
        )
    )
    alert = res.scalar_one_or_none()
    if alert is None:
        raise ResourceNotFoundError("Risk alert not found")

    alert.status = payload.status
    await BankingService.record_audit(
        db,
        current_user,
        event_type="RISK_ALERT_UPDATED",
        target_resource=f"risk_alert:{alert.id}",
        status="SUCCESS",
        details={"new_status": payload.status},
    )
    await db.commit()
    return APIResponse.ok(
        data=RiskAlertRead.model_validate(alert),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
