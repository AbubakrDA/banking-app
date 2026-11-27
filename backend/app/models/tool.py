from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Float, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import TenantScopedModel


class ToolExecution(TenantScopedModel):
    __tablename__ = "tool_executions"

    tool_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    caller_agent: Mapped[str] = mapped_column(
        String(64),
        default="customer_support_agent",
        nullable=False,
        comment="customer_support_agent | billing_agent | supervisor_agent | admin_copilot",
    )
    caller_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    requested_by_user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    requested_by_role: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    risk_level: Mapped[str] = mapped_column(
        String(32),
        default="LOW",
        nullable=False,
        comment="LOW | MEDIUM | HIGH",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="pending",
        nullable=False,
        index=True,
        comment="pending | requires_approval | approved | rejected | success | failed | timed_out",
    )
    input_parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    raw_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    approved_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("caller_agent", "customer_support_agent")
        kwargs.setdefault("risk_level", "LOW")
        kwargs.setdefault("status", "pending")
        kwargs.setdefault("duration_ms", 0.0)
        super().__init__(**kwargs)


class MCPServerConfig(TenantScopedModel):
    __tablename__ = "mcp_server_configs"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    transport_type: Mapped[str] = mapped_column(
        String(32),
        default="http",
        nullable=False,
        comment="http | sse | stdio",
    )
    endpoint_url: Mapped[str] = mapped_column(String(512), nullable=False)
    auth_token: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    discovered_tools: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("transport_type", "http")
        kwargs.setdefault("is_enabled", True)
        super().__init__(**kwargs)
