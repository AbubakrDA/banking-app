from typing import Optional, Dict, Any, List
from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TenantScopedModel


class Conversation(TenantScopedModel):
    __tablename__ = "conversations"

    customer_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    channel: Mapped[str] = mapped_column(
        String(32),
        default="web",
        nullable=False,
        comment="web | whatsapp | email",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="active",
        nullable=False,
        comment="active | escalated | resolved | closed",
    )
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("channel", "web")
        kwargs.setdefault("status", "active")
        super().__init__(**kwargs)


class Message(TenantScopedModel):
    __tablename__ = "messages"

    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="customer | ai_agent | human_agent | system",
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, default=list)
    is_flagged: Mapped[bool] = mapped_column(default=False, nullable=False)

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("sources", [])
        kwargs.setdefault("is_flagged", False)
        super().__init__(**kwargs)
