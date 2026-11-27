import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.auth import get_current_user, require_roles, AuthenticatedUser
from app.models.customer import Customer
from app.models.ticket import Ticket, TicketNote, Feedback
from app.schemas.envelope import APIResponse
from app.schemas.ticket import (
    TicketCreate,
    TicketRead,
    TicketStatusUpdate,
    TicketAssignUpdate,
    TicketNoteCreate,
    TicketNoteRead,
    FeedbackRequestCreate,
    FeedbackSubmit,
    FeedbackRead,
)
from app.services.ticket.ticket_service import TicketService

router = APIRouter()


@router.post("", response_model=APIResponse[TicketRead])
async def create_ticket(
    ticket_in: TicketCreate,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TicketRead]:
    # 1. Verify customer exists in tenant
    cust_res = await db.execute(
        select(Customer).where(Customer.id == ticket_in.customer_id, Customer.tenant_id == current_user.tenant_id)
    )
    customer = cust_res.scalars().first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{ticket_in.customer_id}' not found.",
        )

    # 2. Duplicate Detection: Check if active ticket with same subject exists for customer in past 24h
    one_day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
    dup_query = select(Ticket).where(
        Ticket.customer_id == ticket_in.customer_id,
        Ticket.tenant_id == current_user.tenant_id,
        Ticket.subject == ticket_in.subject,
        Ticket.status.in_(["new", "categorized", "assigned", "in_progress", "waiting_customer", "escalated"]),
        Ticket.created_at >= one_day_ago,
    )
    dup_res = await db.execute(dup_query)
    existing_dup = dup_res.scalars().first()
    if existing_dup:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Duplicate ticket detected: An open ticket (#{existing_dup.ticket_number}) already exists with subject '{ticket_in.subject}'.",
        )

    # 3. Auto-classify & Priority assignment if not explicitly provided
    auto_cat, auto_pri = TicketService.auto_classify(ticket_in.subject, ticket_in.description)
    category = ticket_in.category or auto_cat
    priority = ticket_in.priority or auto_pri
    sla_due = TicketService.calculate_sla_due_date(priority)

    # 4. Generate unique ticket number
    count_res = await db.execute(select(func.count(Ticket.id)).where(Ticket.tenant_id == current_user.tenant_id))
    total_count = count_res.scalar() or 0
    ticket_number = TicketService.generate_ticket_number(total_count + 1)

    # 5. Create Ticket
    ticket_id = str(uuid.uuid4())
    ticket = Ticket(
        id=ticket_id,
        tenant_id=current_user.tenant_id,
        customer_id=ticket_in.customer_id,
        conversation_id=ticket_in.conversation_id,
        ticket_number=ticket_number,
        subject=ticket_in.subject,
        description=ticket_in.description,
        category=category,
        priority=priority,
        status="new",
        sla_due_at=sla_due,
        custom_fields=ticket_in.custom_fields or {},
    )
    db.add(ticket)

    # Initial System Audit Note
    initial_note = TicketNote(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        ticket_id=ticket_id,
        user_id=current_user.id if hasattr(current_user, "id") else None,
        author_name=current_user.email or "System",
        note_type="system_audit",
        content=f"Ticket #{ticket_number} created with category '{category}', priority '{priority}' (SLA due: {sla_due.strftime('%Y-%m-%d %H:%M UTC')}).",
    )
    db.add(initial_note)

    await db.commit()

    # Re-fetch with loaded relationships
    stmt = (
        select(Ticket)
        .options(selectinload(Ticket.notes), selectinload(Ticket.feedback))
        .where(Ticket.id == ticket_id, Ticket.tenant_id == current_user.tenant_id)
    )
    loaded = (await db.execute(stmt)).scalars().first()

    return APIResponse.ok(
        data=TicketRead.model_validate(loaded),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("", response_model=APIResponse[List[TicketRead]])
async def list_tickets(
    request: Request,
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    assigned_user_id: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[TicketRead]]:
    query = (
        select(Ticket)
        .options(selectinload(Ticket.notes), selectinload(Ticket.feedback))
        .where(Ticket.tenant_id == current_user.tenant_id)
    )
    if status_filter:
        query = query.where(Ticket.status == status_filter)
    if priority:
        query = query.where(Ticket.priority == priority)
    if category:
        query = query.where(Ticket.category == category)
    if assigned_user_id:
        query = query.where(Ticket.assigned_user_id == assigned_user_id)

    query = query.order_by(Ticket.created_at.desc())
    result = await db.execute(query)
    tickets = result.scalars().all()
    data = [TicketRead.model_validate(t) for t in tickets]

    return APIResponse.ok(
        data=data,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/{ticket_id}", response_model=APIResponse[TicketRead])
async def get_ticket(
    ticket_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TicketRead]:
    query = (
        select(Ticket)
        .options(selectinload(Ticket.notes), selectinload(Ticket.feedback))
        .where(Ticket.id == ticket_id, Ticket.tenant_id == current_user.tenant_id)
    )
    result = await db.execute(query)
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket '{ticket_id}' not found.",
        )

    return APIResponse.ok(
        data=TicketRead.model_validate(ticket),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.patch("/{ticket_id}/status", response_model=APIResponse[TicketRead])
async def update_ticket_status(
    ticket_id: str,
    status_in: TicketStatusUpdate,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TicketRead]:
    stmt = (
        select(Ticket)
        .options(selectinload(Ticket.notes), selectinload(Ticket.feedback))
        .where(Ticket.id == ticket_id, Ticket.tenant_id == current_user.tenant_id)
    )
    result = await db.execute(stmt)
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket '{ticket_id}' not found.")

    if not TicketService.validate_transition(ticket.status, status_in.status):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid state transition from '{ticket.status}' to '{status_in.status}'.",
        )

    old_status = ticket.status
    ticket.status = status_in.status

    now = datetime.now(timezone.utc)
    if status_in.status == "resolved":
        ticket.resolved_at = now
    elif status_in.status == "closed":
        ticket.closed_at = now
    elif status_in.status == "escalated":
        ticket.is_escalated = True
        ticket.escalation_reason = status_in.reason

    # Add audit note
    audit_msg = f"Status transitioned from '{old_status}' to '{status_in.status}'."
    if status_in.reason:
        audit_msg += f" Reason: {status_in.reason}"

    note = TicketNote(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        ticket_id=ticket.id,
        user_id=current_user.id if hasattr(current_user, "id") else None,
        author_name=current_user.email or "Agent",
        note_type="system_audit",
        content=audit_msg,
    )
    db.add(note)
    await db.commit()
    db.expire_all()

    loaded = (await db.execute(stmt)).scalars().first()
    return APIResponse.ok(
        data=TicketRead.model_validate(loaded),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.patch("/{ticket_id}/assign", response_model=APIResponse[TicketRead])
async def assign_ticket(
    ticket_id: str,
    assign_in: TicketAssignUpdate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TicketRead]:
    stmt = (
        select(Ticket)
        .options(selectinload(Ticket.notes), selectinload(Ticket.feedback))
        .where(Ticket.id == ticket_id, Ticket.tenant_id == current_user.tenant_id)
    )
    result = await db.execute(stmt)
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket '{ticket_id}' not found.")

    ticket.assigned_user_id = assign_in.assigned_user_id
    if ticket.status in ["new", "categorized"]:
        ticket.status = "assigned"

    note = TicketNote(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        ticket_id=ticket.id,
        author_name=current_user.email or "Agent",
        note_type="system_audit",
        content=f"Ticket assigned to user '{assign_in.assigned_user_id}'.",
    )
    db.add(note)
    await db.commit()
    db.expire_all()

    loaded = (await db.execute(stmt)).scalars().first()
    return APIResponse.ok(
        data=TicketRead.model_validate(loaded),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/{ticket_id}/notes", response_model=APIResponse[TicketNoteRead])
async def add_ticket_note(
    ticket_id: str,
    note_in: TicketNoteCreate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TicketNoteRead]:
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id, Ticket.tenant_id == current_user.tenant_id)
    )
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket '{ticket_id}' not found.")

    note = TicketNote(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        ticket_id=ticket_id,
        user_id=current_user.id if hasattr(current_user, "id") else None,
        author_name=current_user.email or "Agent",
        note_type=note_in.note_type,
        content=note_in.content,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)

    return APIResponse.ok(
        data=TicketNoteRead.model_validate(note),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/{ticket_id}/feedback-request", response_model=APIResponse[FeedbackRead])
async def request_feedback(
    ticket_id: str,
    fb_req: FeedbackRequestCreate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[FeedbackRead]:
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id, Ticket.tenant_id == current_user.tenant_id)
    )
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket '{ticket_id}' not found.")

    # Check if feedback already generated
    existing_fb = await db.execute(select(Feedback).where(Feedback.ticket_id == ticket_id))
    fb = existing_fb.scalars().first()

    if not fb:
        fb_token = TicketService.generate_feedback_token()
        expires = datetime.now(timezone.utc) + timedelta(days=7)  # 7-day expiration
        fb = Feedback(
            id=str(uuid.uuid4()),
            tenant_id=current_user.tenant_id,
            ticket_id=ticket.id,
            customer_id=ticket.customer_id,
            channel=fb_req.channel,
            token=fb_token,
            expires_at=expires,
        )
        db.add(fb)

        note = TicketNote(
            id=str(uuid.uuid4()),
            tenant_id=current_user.tenant_id,
            ticket_id=ticket.id,
            author_name="System",
            note_type="system_audit",
            content=f"Customer satisfaction feedback request triggered via {fb_req.channel.upper()}.",
        )
        db.add(note)
        await db.commit()
        await db.refresh(fb)

    return APIResponse.ok(
        data=FeedbackRead.model_validate(fb),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/feedback/submit", response_model=APIResponse[FeedbackRead])
async def submit_feedback(
    fb_sub: FeedbackSubmit,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[FeedbackRead]:
    result = await db.execute(select(Feedback).where(Feedback.token == fb_sub.token))
    fb = result.scalars().first()
    if not fb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired feedback token.",
        )

    now = datetime.now(timezone.utc)
    if fb.expires_at.replace(tzinfo=timezone.utc) < now:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This feedback link has expired.",
        )

    if fb.submitted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback has already been submitted for this ticket.",
        )

    fb.rating = fb_sub.rating
    fb.was_resolved = fb_sub.was_resolved
    fb.comment = fb_sub.comment
    fb.submitted_at = now

    await db.commit()
    await db.refresh(fb)

    return APIResponse.ok(
        data=FeedbackRead.model_validate(fb),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=fb.tenant_id,
    )
