from typing import Optional, Dict, Any
from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TenantScopedModel


class Customer(TenantScopedModel):
    __tablename__ = "customers"

    external_id: Mapped[Optional[str]] = mapped_column(String(128), index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    tier: Mapped[str] = mapped_column(String(32), default="standard", nullable=False)
    profile_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)

    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation",
        back_populates="customer",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("tier", "standard")
        kwargs.setdefault("profile_metadata", {})
        super().__init__(**kwargs)
