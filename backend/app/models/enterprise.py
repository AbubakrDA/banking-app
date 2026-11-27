import hashlib
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import TenantScopedModel


class TenantBranding(TenantScopedModel):
    __tablename__ = "tenant_brandings"

    logo_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    primary_color: Mapped[str] = mapped_column(String(32), default="#0B192C", nullable=False)
    accent_color: Mapped[str] = mapped_column(String(32), default="#1E3E62", nullable=False)
    font_family: Mapped[str] = mapped_column(String(64), default="Inter, sans-serif", nullable=False)
    email_footer_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    custom_css_vars: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("primary_color", "#0B192C")
        kwargs.setdefault("accent_color", "#1E3E62")
        kwargs.setdefault("font_family", "Inter, sans-serif")
        super().__init__(**kwargs)


class AuditLog(TenantScopedModel):
    __tablename__ = "audit_logs"

    actor_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    actor_email: Mapped[str] = mapped_column(String(255), nullable=False)
    actor_role: Mapped[str] = mapped_column(String(32), default="agent", nullable=False)
    event_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="LOGIN_SUCCESS | LOGIN_FAILED | ROLE_CHANGE | SETTINGS_UPDATE | TOOL_APPROVED | DATA_EXPORT | USER_INVITED",
    )
    target_resource: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="SUCCESS", nullable=False)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    prev_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    hash_timestamp: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    event_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    @staticmethod
    def compute_event_hash(
        prev_hash: str,
        tenant_id: str,
        actor_id: str,
        event_type: str,
        target_resource: str,
        status: str,
        hash_timestamp: str,
    ) -> str:
        raw = f"{prev_hash}:{tenant_id}:{actor_id}:{event_type}:{target_resource}:{status}:{hash_timestamp}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("actor_role", "agent")
        kwargs.setdefault("status", "SUCCESS")
        kwargs.setdefault("prev_hash", "0" * 64)
        if "hash_timestamp" not in kwargs or kwargs["hash_timestamp"] is None:
            kwargs["hash_timestamp"] = datetime.now(timezone.utc).isoformat()
        if "event_hash" not in kwargs:
            kwargs["event_hash"] = self.compute_event_hash(
                prev_hash=kwargs["prev_hash"],
                tenant_id=str(kwargs.get("tenant_id")),
                actor_id=str(kwargs.get("actor_id")),
                event_type=str(kwargs.get("event_type")),
                target_resource=str(kwargs.get("target_resource")),
                status=str(kwargs["status"]),
                hash_timestamp=str(kwargs["hash_timestamp"]),
            )
        super().__init__(**kwargs)


class TenantSecurityPolicy(TenantScopedModel):
    __tablename__ = "tenant_security_policies"

    mfa_enforced: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    session_timeout_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    password_rotation_days: Mapped[int] = mapped_column(Integer, default=90, nullable=False)
    data_retention_days: Mapped[int] = mapped_column(Integer, default=365, nullable=False)
    allowed_ip_ranges: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("mfa_enforced", False)
        kwargs.setdefault("session_timeout_minutes", 60)
        kwargs.setdefault("password_rotation_days", 90)
        kwargs.setdefault("data_retention_days", 365)
        super().__init__(**kwargs)


class ModelRoutingConfig(TenantScopedModel):
    __tablename__ = "model_routing_configs"

    default_model: Mapped[str] = mapped_column(String(64), default="gemini-2.5-flash", nullable=False)
    fallback_model: Mapped[str] = mapped_column(String(64), default="gemini-2.5-pro", nullable=False)
    temperature: Mapped[float] = mapped_column(Float, default=0.2, nullable=False)
    max_tokens: Mapped[int] = mapped_column(Integer, default=2048, nullable=False)
    system_instructions_override: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("default_model", "gemini-2.5-flash")
        kwargs.setdefault("fallback_model", "gemini-2.5-pro")
        kwargs.setdefault("temperature", 0.2)
        kwargs.setdefault("max_tokens", 2048)
        super().__init__(**kwargs)
