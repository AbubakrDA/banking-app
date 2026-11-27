from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import AuthenticatedUser, require_roles, require_surface, get_staff_access_reason
from app.schemas.envelope import APIResponse
from app.services.ai.agent import BankingAIAgent

router = APIRouter()


class BankingChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


class BankingChatResponse(BaseModel):
    reply: str
    language: str
    intent: str
    entities: Dict[str, Any]
    citations: List[Dict[str, Any]]
    blocked: bool
    tool_used: Optional[str] = None


@router.post("", response_model=APIResponse[BankingChatResponse])
async def chat_turn(
    payload: BankingChatRequest,
    request: Request,
    _surface: AuthenticatedUser = Depends(require_surface("both")),
    current_user: AuthenticatedUser = Depends(
        require_roles("customer", "employee", "risk_officer", "admin", "hr", "marketing")
    ),
    reason: Optional[str] = Depends(get_staff_access_reason),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[BankingChatResponse]:
    result = await BankingAIAgent.handle_message(
        db,
        current_user,
        payload.message,
        staff_reason=reason,
    )
    return APIResponse.ok(
        data=BankingChatResponse(**result),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
