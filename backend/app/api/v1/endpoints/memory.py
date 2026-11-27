import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import get_db
from app.core.auth import get_current_user, require_roles, AuthenticatedUser
from app.models.customer import Customer
from app.models.memory import CustomerMemory
from app.schemas.envelope import APIResponse
from app.schemas.memory import (
    MemoryCreate,
    MemoryRead,
    CustomerMemoryContextResponse,
    MemoryPurgeResponse,
)
from app.services.memory.memory_service import MemoryService

router = APIRouter()


@router.post("", response_model=APIResponse[MemoryRead])
async def create_memory(
    mem_in: MemoryCreate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[MemoryRead]:
    # 1. Verify customer exists in tenant
    cust_res = await db.execute(
        select(Customer).where(Customer.id == mem_in.customer_id, Customer.tenant_id == current_user.tenant_id)
    )
    customer = cust_res.scalars().first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{mem_in.customer_id}' not found.",
        )

    # 2. Anti-Poisoning Defense (GEMINI.md Rule 4)
    is_safe, poison_reason = MemoryService.validate_memory_content(mem_in.key, mem_in.value)

    # Populate provenance
    provenance = mem_in.provenance or {}
    provenance.setdefault("recorded_by", current_user.email or current_user.id)
    provenance.setdefault("source", "user_agent_interaction")
    provenance.setdefault("recorded_at", datetime.now(timezone.utc).isoformat())

    memory_id = str(uuid.uuid4())
    mem = CustomerMemory(
        id=memory_id,
        tenant_id=current_user.tenant_id,
        customer_id=mem_in.customer_id,
        conversation_id=mem_in.conversation_id,
        memory_type=mem_in.memory_type,
        key=mem_in.key,
        value=mem_in.value,
        confidence_score=mem_in.confidence_score,
        provenance=provenance,
        expires_at=mem_in.expires_at,
        is_flagged=not is_safe,
        flag_reason=poison_reason,
        is_active=is_safe,  # Poisoned memories are inactivated
    )
    db.add(mem)
    await db.commit()
    await db.refresh(mem)

    if not is_safe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Memory insertion rejected: {poison_reason}",
        )

    return APIResponse.ok(
        data=MemoryRead.model_validate(mem),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/customer/{customer_id}", response_model=APIResponse[List[MemoryRead]])
async def list_customer_memories(
    customer_id: str,
    request: Request,
    memory_type: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[MemoryRead]]:
    query = select(CustomerMemory).where(
        CustomerMemory.customer_id == customer_id,
        CustomerMemory.tenant_id == current_user.tenant_id,
        CustomerMemory.is_active.is_(True),
    )
    if memory_type:
        query = query.where(CustomerMemory.memory_type == memory_type)

    query = query.order_by(CustomerMemory.created_at.desc())
    result = await db.execute(query)
    memories = result.scalars().all()

    # Filter out expired working memory
    now = datetime.now(timezone.utc)
    valid_memories = []
    for m in memories:
        if m.expires_at and m.expires_at.replace(tzinfo=timezone.utc) < now:
            continue
        valid_memories.append(m)

    data = [MemoryRead.model_validate(m) for m in valid_memories]
    return APIResponse.ok(
        data=data,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/customer/{customer_id}/context", response_model=APIResponse[CustomerMemoryContextResponse])
async def get_customer_memory_context(
    customer_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[CustomerMemoryContextResponse]:
    query = select(CustomerMemory).where(
        CustomerMemory.customer_id == customer_id,
        CustomerMemory.tenant_id == current_user.tenant_id,
        CustomerMemory.is_active.is_(True),
    ).order_by(CustomerMemory.created_at.desc())

    result = await db.execute(query)
    memories = result.scalars().all()

    now = datetime.now(timezone.utc)
    working: Dict[str, str] = {}
    episodic: List[Dict[str, Any]] = []
    semantic: Dict[str, str] = {}

    for m in memories:
        if m.expires_at and m.expires_at.replace(tzinfo=timezone.utc) < now:
            continue

        if m.memory_type == "working":
            working[m.key] = m.value
        elif m.memory_type == "semantic":
            semantic[m.key] = m.value
        elif m.memory_type == "episodic":
            episodic.append({
                "id": m.id,
                "key": m.key,
                "value": m.value,
                "provenance": m.provenance,
                "created_at": m.created_at.isoformat(),
            })

    envelope = MemoryService.format_context_envelope(working, episodic, semantic)

    data = CustomerMemoryContextResponse(
        customer_id=customer_id,
        tenant_id=current_user.tenant_id,
        working_memory=working,
        episodic_memory=episodic,
        semantic_memory=semantic,
        formatted_context_envelope=envelope,
        total_memories=len(working) + len(episodic) + len(semantic),
    )

    return APIResponse.ok(
        data=data,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.delete("/{memory_id}", response_model=APIResponse[dict])
async def delete_memory(
    memory_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[dict]:
    query = select(CustomerMemory).where(
        CustomerMemory.id == memory_id,
        CustomerMemory.tenant_id == current_user.tenant_id,
    )
    result = await db.execute(query)
    mem = result.scalars().first()
    if not mem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory '{memory_id}' not found.",
        )

    await db.delete(mem)
    await db.commit()

    return APIResponse.ok(
        data={"deleted": True, "memory_id": memory_id},
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.delete("/customer/{customer_id}/purge", response_model=APIResponse[MemoryPurgeResponse])
async def purge_customer_memories(
    customer_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[MemoryPurgeResponse]:
    """
    GDPR Right to be Forgotten: Permanently deletes all memories across Working, Episodic,
    and Semantic tiers for a customer.
    """
    stmt = delete(CustomerMemory).where(
        CustomerMemory.customer_id == customer_id,
        CustomerMemory.tenant_id == current_user.tenant_id,
    )
    result = await db.execute(stmt)
    await db.commit()

    purged_count = result.rowcount or 0
    data = MemoryPurgeResponse(
        customer_id=customer_id,
        tenant_id=current_user.tenant_id,
        purged_count=purged_count,
        purged_at=datetime.now(timezone.utc),
    )

    return APIResponse.ok(
        data=data,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
