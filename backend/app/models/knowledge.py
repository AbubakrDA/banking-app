from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TenantScopedModel


class KBCollection(TenantScopedModel):
    __tablename__ = "kb_collections"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    documents: Mapped[List["KBDocument"]] = relationship(
        "KBDocument",
        back_populates="collection",
        cascade="all, delete-orphan",
    )
    chunks: Mapped[List["KBChunk"]] = relationship(
        "KBChunk",
        back_populates="collection",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("is_public", True)
        super().__init__(**kwargs)


class KBDocument(TenantScopedModel):
    __tablename__ = "kb_documents"

    collection_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("kb_collections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(
        String(32),
        default="manual_entry",
        nullable=False,
        comment="manual_entry | file_upload | url | faq",
    )
    source_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        default="indexed",
        nullable=False,
        comment="draft | indexing | indexed | archived | error",
    )
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    doc_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)

    collection: Mapped["KBCollection"] = relationship("KBCollection", back_populates="documents")
    chunks: Mapped[List["KBChunk"]] = relationship(
        "KBChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("source_type", "manual_entry")
        kwargs.setdefault("version", 1)
        kwargs.setdefault("status", "indexed")
        kwargs.setdefault("chunk_count", 0)
        kwargs.setdefault("doc_metadata", {})
        super().__init__(**kwargs)


class KBChunk(TenantScopedModel):
    __tablename__ = "kb_chunks"

    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("kb_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    collection_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("kb_collections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chunk_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)

    document: Mapped["KBDocument"] = relationship("KBDocument", back_populates="chunks")
    collection: Mapped["KBCollection"] = relationship("KBCollection", back_populates="chunks")

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("token_count", 0)
        kwargs.setdefault("chunk_metadata", {})
        super().__init__(**kwargs)
