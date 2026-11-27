from typing import Optional, Dict, Any
from sqlalchemy import String, BigInteger, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import TenantScopedModel


class Document(TenantScopedModel):
    __tablename__ = "documents"

    conversation_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    customer_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(32),
        default="uploaded",
        nullable=False,
        comment="uploaded | scanning | processing | ready | quarantined | error",
    )
    is_quarantined: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    quarantine_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    doc_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("status", "uploaded")
        kwargs.setdefault("is_quarantined", False)
        kwargs.setdefault("doc_metadata", {})
        super().__init__(**kwargs)
