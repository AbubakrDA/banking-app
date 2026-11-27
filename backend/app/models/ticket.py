from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TenantScopedModel


class Ticket(TenantScopedModel):
    __tablename__ = "tickets"

    customer_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    conversation_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    ticket_number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(
        String(64),
        default="general",
        nullable=False,
        comment="billing | product_defect | shipping_delay | appointment | account | general",
    )
    priority: Mapped[str] = mapped_column(
        String(32),
        default="medium",
        nullable=False,
        comment="low | medium | high | urgent",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="new",
        nullable=False,
        comment="new | categorized | assigned | in_progress | waiting_customer | escalated | resolved | closed",
    )
    assigned_user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sla_due_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_escalated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    escalation_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)

    notes: Mapped[List["TicketNote"]] = relationship(
        "TicketNote",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="TicketNote.created_at",
    )
    feedback: Mapped[Optional["Feedback"]] = relationship(
        "Feedback",
        back_populates="ticket",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("category", "general")
        kwargs.setdefault("priority", "medium")
        kwargs.setdefault("status", "new")
        kwargs.setdefault("is_escalated", False)
        kwargs.setdefault("custom_fields", {})
        super().__init__(**kwargs)


class TicketNote(TenantScopedModel):
    __tablename__ = "ticket_notes"

    ticket_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    author_name: Mapped[str] = mapped_column(String(128), default="System", nullable=False)
    note_type: Mapped[str] = mapped_column(
        String(32),
        default="internal",
        nullable=False,
        comment="internal | customer_reply | system_audit",
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="notes")

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("note_type", "internal")
        kwargs.setdefault("author_name", "System")
        super().__init__(**kwargs)


class Feedback(TenantScopedModel):
    __tablename__ = "customer_feedback"

    ticket_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    customer_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel: Mapped[str] = mapped_column(
        String(32),
        default="web",
        nullable=False,
        comment="whatsapp | email | web",
    )
    token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="1 to 5")
    was_resolved: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="feedback")

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("channel", "web")
        super().__init__(**kwargs)
