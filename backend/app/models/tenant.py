from typing import Optional, Dict, Any
from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TimeStampedModel, TenantScopedModel


class Tenant(TimeStampedModel):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    business_mode: Mapped[str] = mapped_column(
        String(32),
        default="hybrid",
        nullable=False,
        comment="products | services | hybrid",
    )

    # Relationships
    settings: Mapped[Optional["OrganizationSettings"]] = relationship(
        "OrganizationSettings",
        back_populates="tenant",
        uselist=False,
        cascade="all, delete-orphan",
    )
    users: Mapped[list["User"]] = relationship("User", back_populates="tenant", cascade="all, delete-orphan")

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("business_mode", "hybrid")
        super().__init__(**kwargs)


class OrganizationSettings(TenantScopedModel):
    __tablename__ = "organization_settings"

    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    support_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    support_phone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    primary_domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="settings")
