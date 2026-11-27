from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Float, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import TenantScopedModel


class CustomerMemory(TenantScopedModel):
    __tablename__ = "customer_memories"

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
    memory_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="working | episodic | semantic",
    )
    key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    provenance: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    flag_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("confidence_score", 1.0)
        kwargs.setdefault("provenance", {})
        kwargs.setdefault("is_flagged", False)
        kwargs.setdefault("is_active", True)
        super().__init__(**kwargs)
