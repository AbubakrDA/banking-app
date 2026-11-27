from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy import String, Text, Numeric, Integer, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TenantScopedModel


class Product(TenantScopedModel):
    __tablename__ = "business_products"

    sku: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    brand: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    supplier: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    specifications: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)


class Service(TenantScopedModel):
    __tablename__ = "business_services"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    staff_members: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    service_policies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)


class Order(TenantScopedModel):
    __tablename__ = "business_orders"

    customer_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_number: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        default="pending",
        nullable=False,
        comment="pending | processing | shipped | delivered | cancelled",
    )
    items: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    delivery_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Appointment(TenantScopedModel):
    __tablename__ = "business_appointments"

    customer_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("business_services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    staff_name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        default="scheduled",
        nullable=False,
        comment="scheduled | completed | rescheduled | cancelled",
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class DataSource(TenantScopedModel):
    __tablename__ = "data_sources"

    source_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="google_sheets | csv_upload | database | api",
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    sync_status: Mapped[str] = mapped_column(
        String(32),
        default="idle",
        nullable=False,
        comment="idle | syncing | error | paused",
    )
    sync_frequency: Mapped[str] = mapped_column(
        String(32),
        default="hourly",
        nullable=False,
        comment="manual | hourly | daily",
    )
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    sync_history: Mapped[List["SyncHistory"]] = relationship(
        "SyncHistory",
        back_populates="data_source",
        cascade="all, delete-orphan",
    )


class SyncHistory(TenantScopedModel):
    __tablename__ = "sync_history"

    data_source_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("data_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    records_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quality_score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    quality_issues: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, default=list)

    data_source: Mapped["DataSource"] = relationship("DataSource", back_populates="sync_history")
