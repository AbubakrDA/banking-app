import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.auth import get_current_user, AuthenticatedUser
from app.models.tenant import Tenant
from app.models.customer import Customer
from app.models.conversation import Conversation, Message
from app.schemas.envelope import APIResponse
from app.schemas.chat import (
    ConversationCreate,
    ConversationRead,
    MessageCreate,
    MessageRead,
    EscalationRequest,
    TurnResult,
)
from app.services.ai.prompt_guard import PromptGuard
from app.services.ai.agent import CustomerSupportAgent

router = APIRouter()


@router.post("/conversations", response_model=APIResponse[ConversationRead])
async def create_conversation(
    conv_in: ConversationCreate,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ConversationRead]:
    customer_id = conv_in.customer_id
    if customer_id:
        # Validate customer exists in tenant
        cust_res = await db.execute(
            select(Customer).where(Customer.id == customer_id, Customer.tenant_id == current_user.tenant_id)
        )
        customer = cust_res.scalars().first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID '{customer_id}' not found",
            )
    else:
        # Create a new guest customer for this tenant
        customer_id = str(uuid.uuid4())
        new_customer = Customer(
            id=customer_id,
            tenant_id=current_user.tenant_id,
            name=conv_in.customer_name or "Valued Customer",
            tier="standard",
        )
        db.add(new_customer)
        await db.flush()

    db_conv = Conversation(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        customer_id=customer_id,
        channel=conv_in.channel,
        status="active",
        summary="Customer initiated conversation",
    )
    db.add(db_conv)
    await db.commit()
    await db.refresh(db_conv)

    # Re-fetch with loaded messages relationship
    stmt = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == db_conv.id, Conversation.tenant_id == current_user.tenant_id)
    )
    loaded = (await db.execute(stmt)).scalars().first()

    return APIResponse.ok(
        data=ConversationRead.model_validate(loaded),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/conversations", response_model=APIResponse[List[ConversationRead]])
async def list_conversations(
    request: Request,
    channel: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[ConversationRead]]:
    query = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.tenant_id == current_user.tenant_id)
    )
    if channel:
        query = query.where(Conversation.channel == channel)
    if status_filter:
        query = query.where(Conversation.status == status_filter)

    query = query.order_by(Conversation.created_at.desc())
    result = await db.execute(query)
    conversations = result.scalars().all()

    data = [ConversationRead.model_validate(c) for c in conversations]
    return APIResponse.ok(
        data=data,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/conversations/{conversation_id}", response_model=APIResponse[ConversationRead])
async def get_conversation(
    conversation_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ConversationRead]:
    query = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conversation_id, Conversation.tenant_id == current_user.tenant_id)
    )
    result = await db.execute(query)
    conv = result.scalars().first()
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{conversation_id}' not found",
        )

    return APIResponse.ok(
        data=ConversationRead.model_validate(conv),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/conversations/{conversation_id}/messages", response_model=APIResponse[TurnResult])
async def send_message(
    conversation_id: str,
    msg_in: MessageCreate,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TurnResult]:
    # 1. Fetch conversation with customer
    conv_query = (
        select(Conversation)
        .options(selectinload(Conversation.customer))
        .where(Conversation.id == conversation_id, Conversation.tenant_id == current_user.tenant_id)
    )
    result = await db.execute(conv_query)
    conv = result.scalars().first()
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{conversation_id}' not found",
        )

    customer_name = conv.customer.name if conv.customer else "Customer"

    # 2. Fetch tenant business mode
    tenant_res = await db.execute(select(Tenant).where(Tenant.id == current_user.tenant_id))
    tenant = tenant_res.scalars().first()
    business_mode = tenant.business_mode if tenant else "hybrid"

    # 3. Layer 1: Prompt Injection Check
    is_valid, sec_error = PromptGuard.validate_user_input(msg_in.content)

    # 4. Save Customer Message
    cust_msg = Message(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        conversation_id=conversation_id,
        sender_type="customer",
        content=msg_in.content,
        is_flagged=not is_valid,
        sources=[],
    )
    db.add(cust_msg)

    if not is_valid:
        # Prompt injection detected
        agent_msg = Message(
            id=str(uuid.uuid4()),
            tenant_id=current_user.tenant_id,
            conversation_id=conversation_id,
            sender_type="system",
            content=f"Security Alert: Message was rejected by prompt guard policy ({sec_error}).",
            is_flagged=True,
            sources=[{"source": "prompt_guard", "type": "security_policy", "detail": sec_error or "Untrusted pattern"}],
        )
        db.add(agent_msg)
        await db.commit()
        await db.refresh(cust_msg)
        await db.refresh(agent_msg)

        turn_result = TurnResult(
            customer_message=MessageRead.model_validate(cust_msg),
            agent_message=MessageRead.model_validate(agent_msg),
            intent="security_violation",
            sentiment="neutral",
            should_escalate=False,
            escalation_reason=sec_error,
            is_security_violation=True,
        )
        return APIResponse.ok(
            data=turn_result,
            request_id=getattr(request.state, "request_id", None),
            tenant_id=current_user.tenant_id,
        )

    # 5. Process turn via CustomerSupportAgent
    ai_turn = await CustomerSupportAgent.process_turn(
        user_message=msg_in.content,
        customer_name=customer_name,
        business_mode=business_mode,
    )

    # 6. Save AI Response Message
    agent_msg = Message(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        conversation_id=conversation_id,
        sender_type="ai_agent",
        content=ai_turn["response"],
        is_flagged=False,
        sources=ai_turn.get("sources", []),
    )
    db.add(agent_msg)

    # 7. Check automatic escalation trigger
    if ai_turn.get("should_escalate"):
        conv.status = "escalated"
        conv.summary = ai_turn.get("escalation_reason")

    await db.commit()
    await db.refresh(cust_msg)
    await db.refresh(agent_msg)

    turn_result = TurnResult(
        customer_message=MessageRead.model_validate(cust_msg),
        agent_message=MessageRead.model_validate(agent_msg),
        intent=ai_turn.get("intent", "unknown"),
        sentiment=ai_turn.get("sentiment", "neutral"),
        should_escalate=ai_turn.get("should_escalate", False),
        escalation_reason=ai_turn.get("escalation_reason"),
        is_security_violation=False,
    )

    return APIResponse.ok(
        data=turn_result,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/conversations/{conversation_id}/escalate", response_model=APIResponse[ConversationRead])
async def escalate_conversation(
    conversation_id: str,
    esc_in: EscalationRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ConversationRead]:
    query = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conversation_id, Conversation.tenant_id == current_user.tenant_id)
    )
    result = await db.execute(query)
    conv = result.scalars().first()
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{conversation_id}' not found",
        )

    conv.status = "escalated"
    conv.summary = esc_in.reason
    if esc_in.assigned_user_id:
        conv.assigned_user_id = esc_in.assigned_user_id

    # Append system notice
    sys_msg = Message(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        conversation_id=conversation_id,
        sender_type="system",
        content=f"Human escalation initiated: {esc_in.reason}",
        is_flagged=False,
        sources=[{"source": "handover_service", "type": "escalation", "detail": esc_in.reason}],
    )
    db.add(sys_msg)
    await db.commit()
    db.expire_all()

    # Re-fetch conversation with updated messages
    loaded = (await db.execute(query)).scalars().first()

    return APIResponse.ok(
        data=ConversationRead.model_validate(loaded),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
