from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TenantScopedModel


class User(TenantScopedModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(32),
        default="agent",
        nullable=False,
        comment="owner | admin | agent | customer",
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="users")
